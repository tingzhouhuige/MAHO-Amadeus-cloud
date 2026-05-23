import config from '../config.json'

type MessageHandler = (data: any) => void
type EventHandler = () => void

export class MahoWebSocket {
  private ws: WebSocket | null = null
  private url: string
  private reconnectTimer: number | null = null
  private pendingMessages: any[] = []
  private messageHandlers: Map<string, MessageHandler[]> = new Map()
  private eventHandlers: Map<string, EventHandler[]> = new Map()

  constructor() {
    this.url = `ws://${config.ip}:8080/ws`
    this.connect()
  }

  private connect() {
    if (this.ws && this.ws.readyState !== WebSocket.CLOSED) return
    this.ws = new WebSocket(this.url)
    this.bindEvents()
  }

  private bindEvents() {
    if (!this.ws) return
    this.triggerEvent('connecting')

    this.ws.onopen = () => {
      console.log('WebSocket connected:', this.ws?.url)
      this.triggerEvent('open')
      this.flushPendingMessages()
      if (this.reconnectTimer) {
        clearInterval(this.reconnectTimer)
        this.reconnectTimer = null
      }
    }

    this.ws.onmessage = (event) => {
      try {
        const msg = JSON.parse(event.data)
        this.triggerMessage(msg.type, msg)
      } catch (e) {
        console.error('Failed to parse WS message', e)
      }
    }

    this.ws.onclose = () => {
      this.triggerEvent('close')
      this.reconnect()
    }

    this.ws.onerror = (error) => {
      console.error('WebSocket error:', error)
      this.triggerEvent('error')
    }
  }

  private reconnect() {
    if (this.ws?.readyState === WebSocket.OPEN || this.ws?.readyState === WebSocket.CONNECTING) return
    if (this.reconnectTimer) return

    this.reconnectTimer = window.setInterval(() => {
      if (!this.ws || this.ws.readyState === WebSocket.CLOSED) {
        console.log('Reconnecting WebSocket...')
        this.connect()
      }
    }, 1000)
  }

  public send(data: any) {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify(data))
      return
    }
    this.pendingMessages.push(data)
    this.reconnect()
    console.warn('WebSocket not open yet; queued message')
  }

  private flushPendingMessages() {
    if (!this.ws || this.ws.readyState !== WebSocket.OPEN) return
    const messages = this.pendingMessages.splice(0)
    messages.forEach(data => this.ws?.send(JSON.stringify(data)))
  }

  public on(event: string, callback: MessageHandler | EventHandler) {
    if (['connecting', 'open', 'close', 'error'].includes(event)) {
      if (!this.eventHandlers.has(event)) {
        this.eventHandlers.set(event, [])
      }
      this.eventHandlers.get(event)?.push(callback as EventHandler)

      if (event === 'open' && this.ws?.readyState === WebSocket.OPEN) {
        window.setTimeout(() => (callback as EventHandler)(), 0)
      }
      if (event === 'connecting' && this.ws?.readyState === WebSocket.CONNECTING) {
        window.setTimeout(() => (callback as EventHandler)(), 0)
      }
      return
    }

    if (!this.messageHandlers.has(event)) {
      this.messageHandlers.set(event, [])
    }
    this.messageHandlers.get(event)?.push(callback as MessageHandler)
  }

  private triggerEvent(event: string) {
    this.eventHandlers.get(event)?.forEach(handler => handler())
  }

  private triggerMessage(type: string, data: any) {
    const handlers = this.messageHandlers.get(type)
    if (handlers) {
      handlers.forEach(handler => handler(data))
    } else {
      console.warn('Unknown WS message type:', type, data)
    }
  }
}
