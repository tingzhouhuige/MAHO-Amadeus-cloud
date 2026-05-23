<template>
  <div>
    <CenterRevealMask :visible="showMask">
      <DialogBackground />
      <meswinName :name="currentName" class="Meswinname" />
      <div v-if="isReading" class="continue-overlay" :class="{ waiting: isWaiting }" @click="handleContinue">
        <span class="continue-text">{{ isWaiting ? '点击跳过语音' : '点击继续' }}</span>
      </div>
      <DialogTextArea
        :thinkText="thinkText"
        :isInputMode="isInputMode"
        :textQueue="textQueue"
        @send="handleSend"
      />
    </CenterRevealMask>
    <SiriWave :visible="showSiriWave" class="Siri-wave"/>
  </div>
</template>

<script setup lang="js">
import { ref, onMounted, onUnmounted } from 'vue'
import CenterRevealMask from '@/component/CenterRevealMask.vue'
import DialogBackground from './DialogBackground.vue'
import meswinName from './meswinName.vue'
import SiriWave from './SiriWave.vue'
import DialogTextArea from './DialogTextArea.vue'

const props = defineProps({
  currentName: String,
  videoMode: Boolean,
  thinkText: String,
  isInputMode: Boolean,
  isReading: Boolean,
  isWaiting: Boolean,
  textQueue: Array
})

const emit = defineEmits(['send', 'continue'])

const showMask = ref(false)
const showSiriWave = ref(false)

function handleSend(payload) {
  emit('send', payload)
}

function handleContinue() {
  emit('continue')
}

const handleKeyDown = (e) => {
  if (e.key.toLowerCase() === 'h' && e.shiftKey) {
    showMask.value = !showMask.value
  }
}

onMounted(() => {
  window.addEventListener('keydown', handleKeyDown)
  setTimeout(() => {
    showMask.value = true
  }, 1000)
})

onUnmounted(() => {
  window.removeEventListener('keydown', handleKeyDown)
})
</script>

<style>
.Meswinname {
  position: absolute;
  bottom: 40px;
  left: 50%;
  transform: translateX(-50%);
  z-index: 10;
}

.continue-overlay {
  position: absolute;
  bottom: 0;
  left: 0;
  width: 100%;
  height: 100px;
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 20;
  cursor: pointer;
  background: linear-gradient(transparent, rgba(0, 0, 0, 0.6));
}

.continue-overlay.waiting {
  cursor: pointer;
}

.continue-text {
  color: #e6a23c;
  font-family: 'Microsoft YaHei', 'SimHei', 'SimSun', sans-serif;
  font-size: 2rem;
  text-shadow: 2px 2px 6px #000;
  animation: blink 1.5s infinite;
}

@keyframes blink {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.3; }
}
</style>
