import { defineStore } from 'pinia'
import { ref } from 'vue'
import config from '../config.json'
import { MahoWebSocket } from '../api/ws'

export const useHomeStore = defineStore('home', () => {
  // 文本框相关
  const textQueue = ref<string[]>([])
  const thinkText = ref('')
  // 音频相关
  const audioQueue = ref<{ id?: string, data: string, is_final: boolean }[]>([])
  const mouthOpen = ref(0) // 嘴巴张开程度 0-1
  
  // 按钮状态
  const buttonStates = ref({
    video: false
  })
  
  // 用户名
  const userName = ref(localStorage.getItem('username') || '未命名')
  const amadeusName = ref(config.amadeusName || '比屋定真帆')
  const currentName = ref(userName.value)


  // WS客户端
  const wsClient = new MahoWebSocket()

  // WS状态
  const isWaiting = ref(false)
  const isReading = ref(false)
  const isTextDone = ref(false)
  const isAudioDone = ref(false)
  const wsStatus = ref('connecting')

  // 注册 WebSocket 回调函数
  wsClient.on('connecting', () => {
    wsStatus.value = 'connecting'
  })

  wsClient.on('open', () => {
    wsStatus.value = 'connected'
  })

  wsClient.on('close', () => {
    wsStatus.value = 'closed'
  })

  wsClient.on('error', () => {
    wsStatus.value = 'error'
  })

  wsClient.on('tts_loading', () => {
    wsStatus.value = 'connected'
    isWaiting.value = true
    isReading.value = false
    textQueue.value = ['语音加载中…']
    currentName.value = amadeusName.value
  })

  wsClient.on('tts_ready', () => {
    wsStatus.value = 'connected'
    if (!isReading.value) {
      isWaiting.value = false
      textQueue.value = []
      currentName.value = userName.value
    }
  })

  wsClient.on('thinkText', (msg: any) => {
    wsStatus.value = 'connected'
    thinkText.value += msg.data
  })

  wsClient.on('text', (msg: any) => {
    wsStatus.value = 'connected'
    if (thinkText.value) {
      thinkText.value = ''
    }
    textQueue.value.push(msg.data)
  })

  wsClient.on('audio', (msg: any) => {
    wsStatus.value = 'connected'
    audioQueue.value.push({
      id: msg.id,
      data: msg.data,
      is_final: msg.is_final
    })
  })

  wsClient.on('start', () => {
    wsStatus.value = 'connected'
    textQueue.value = []
    thinkText.value = ''
    isWaiting.value = true
    isReading.value = true
    isTextDone.value = false
    isAudioDone.value = false
    currentName.value = amadeusName.value
  })

  wsClient.on('end', () => {
    wsStatus.value = 'connected'
    isTextDone.value = true
  })

  wsClient.on('audio_done', () => {
    wsStatus.value = 'connected'
    isAudioDone.value = true
    if (isTextDone.value && audioQueue.value.length === 0) {
      isWaiting.value = false
    }
  })

  function finishAudioPlayback() {
    if (isTextDone.value && isAudioDone.value && audioQueue.value.length === 0) {
      isWaiting.value = false
    }
  }

  function finishReading() {
    if (isWaiting.value) {
      wsClient.send({ type: 'interrupt' })
    }
    isReading.value = false
    isWaiting.value = false
    isTextDone.value = false
    isAudioDone.value = false
    currentName.value = userName.value
    textQueue.value = []
    audioQueue.value = []
  }

  function send(data: any) {
    wsClient.send(data)
  }

  return {
    textQueue,
    thinkText,
    audioQueue,
    isWaiting,
    isReading,
    wsStatus,
    buttonStates,
    mouthOpen,
    currentName,
    finishReading,
    finishAudioPlayback,
    send
  }
})
