import type { Ref } from 'vue'

export function useLipSyncAudio(
  audioQueue: Ref<{ id?: string; data: string; is_final: boolean }[]>,
  getAudioContext: () => AudioContext,
  onMouthOpen: (value: number) => void,
  onPlaybackIdle?: () => void
) {
  // 音频分析器
  let analyser: AnalyserNode | null = null
  let dataArray: Uint8Array<ArrayBuffer> | null = null
  let isProcessing = false
  let playbackGeneration = 0
  const playedAudioIds = new Set<string>()

  const initAudioContext = async () => {
    const audioContext = getAudioContext()
    if (audioContext.state === 'suspended') {
      await audioContext.resume()
    }
    if (!analyser) {
      analyser = audioContext.createAnalyser()
      analyser.fftSize = 256
      dataArray = new Uint8Array(analyser.frequencyBinCount)
    }
    return audioContext
  }

  const playAudio = (blob: Blob) => {
    return new Promise<void>(async (resolve) => {
      try {
        const generation = playbackGeneration
        const audioContext = await initAudioContext()

        const arrayBuffer = await blob.arrayBuffer()
        const audioBuffer = await audioContext.decodeAudioData(arrayBuffer)

        const source = audioContext.createBufferSource()
        source.buffer = audioBuffer
        source.connect(analyser!)
        analyser!.connect(audioContext.destination)

        let animationId = 0
        const updateLipSync = () => {
          if (!analyser || !dataArray) return
          analyser.getByteFrequencyData(dataArray)

          // 计算平均音量
          let sum = 0
          for (let i = 0; i < dataArray.length; i++) {
            sum += dataArray[i] ?? 0
          }
          const average = sum / dataArray.length

          // 增加门限防止一直张嘴 (底噪过滤)
          const threshold = 10
          let value = 0
          if (average > threshold) {
            value = Math.min(1, ((average - threshold) / (255 - threshold)) * 3.0)
          }

          onMouthOpen(value)

          animationId = requestAnimationFrame(updateLipSync)
        }

        source.onended = () => {
          cancelAnimationFrame(animationId)
          onMouthOpen(0) // 播放结束闭嘴
          resolve()
        }

        console.log('开始播放TTS音频:', Math.round(audioBuffer.duration * 1000), 'ms')
        updateLipSync()
        if (generation !== playbackGeneration) {
          resolve()
          return
        }
        source.start(0)
      } catch (error) {
        console.error('音频解码/播放失败:', error)
        onMouthOpen(0)
        resolve()
      }
    })
  }

  const processAudioQueue = async () => {
    if (isProcessing) return
    isProcessing = true
    let audioBuffer = ''
    let audioId = ''
    while (true) {
      if (audioQueue.value.length > 0) {
        const chunk = audioQueue.value.shift()
        if (chunk) {
          if (chunk.id) {
            if (!audioId) audioId = chunk.id
            if (audioId !== chunk.id) {
              audioBuffer = ''
              audioId = chunk.id
            }
          }
          audioBuffer += chunk.data
          if (chunk.is_final) {
            try {
              if (audioId && playedAudioIds.has(audioId)) {
                continue
              }
              if (audioId) {
                playedAudioIds.add(audioId)
                if (playedAudioIds.size > 100) {
                  playedAudioIds.clear()
                }
              }
              const binaryString = window.atob(audioBuffer)
              const len = binaryString.length
              const bytes = new Uint8Array(new ArrayBuffer(len))
              for (let i = 0; i < len; i++) {
                bytes[i] = binaryString.charCodeAt(i)
              }
              const blob = new Blob([bytes], { type: 'audio/wav' })
              await playAudio(blob)
            } catch (error) {
              console.error('音频播放失败:', error)
            } finally {
              audioBuffer = ''
              audioId = ''
            }
          }
        }
      } else {
        if (audioQueue.value.length === 0) {
          playbackGeneration++
        }
        onPlaybackIdle?.()
        await new Promise(resolve => setTimeout(resolve, 20))
      }
    }
  }

  return {
    processAudioQueue
  }
}
