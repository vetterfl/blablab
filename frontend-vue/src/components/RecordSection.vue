<template>
  <div>
    <div class="step-label">01 &middot; Record</div>
    <section class="card record-section">
      <div class="card-header">
        <div style="min-width:0">
          <h2 class="card-title">Speak into the mic</h2>
          <p class="card-subtitle">Click record, speak naturally, stop when done.</p>
        </div>
        <p :class="['status-text', statusType]">{{ statusMsg }}</p>
      </div>
      <div class="record-controls">
        <div class="record-btn-wrap">
          <div :class="['record-ring', { active: isRecording && !isPaused }]"></div>
          <button
            :class="['btn-record-main', { recording: isRecording && !isPaused, paused: isPaused }]"
            :disabled="isTranscribing"
            aria-label="Record / Pause / Resume"
            @click="handleRecordClick"
          >
            <span class="record-icon">{{ recordIcon }}</span>
          </button>
        </div>
        <div :class="['waveform', { active: isRecording && !isPaused }]">
          <span v-for="n in 10" :key="n"></span>
        </div>
        <button
          id="btn-stop"
          class="btn btn-stop"
          :disabled="!isRecording"
          @click="stopRecording"
        >
          &#9632; Stop
        </button>
      </div>
    </section>
  </div>
</template>

<script setup>
import { ref, computed, onUnmounted } from 'vue'
import { apiTranscribe } from '../api/client.js'

const emit = defineEmits(['transcribed'])

const MAX_RECORD_SECONDS = 90

let mediaRecorder = null
let audioChunks = []
let recordingTimer = null

const isRecording = ref(false)
const isPaused = ref(false)
const isTranscribing = ref(false)
const secondsLeft = ref(0)
const statusMsg = ref('Ready to record')
const statusType = ref('')

const recordIcon = computed(() => {
  if (!isRecording.value) return '●'
  if (isPaused.value) return '▶'
  return '⏸'
})

function setStatus(msg, type = '') {
  statusMsg.value = msg
  statusType.value = type
}

function handleRecordClick() {
  if (!isRecording.value) startRecording()
  else if (!isPaused.value) pauseRecording()
  else resumeRecording()
}

async function startRecording() {
  let stream
  try {
    stream = await navigator.mediaDevices.getUserMedia({ audio: true })
  } catch (err) {
    setStatus(`Microphone access denied: ${err.message}`, 'error')
    return
  }

  audioChunks = []

  const mimeType = ['audio/webm;codecs=opus', 'audio/webm', 'audio/ogg'].find(
    (m) => MediaRecorder.isTypeSupported(m)
  ) || ''

  mediaRecorder = new MediaRecorder(stream, mimeType ? { mimeType } : {})

  mediaRecorder.addEventListener('dataavailable', (e) => {
    if (e.data.size > 0) audioChunks.push(e.data)
  })

  mediaRecorder.addEventListener('stop', () => {
    stream.getTracks().forEach((t) => t.stop())
    const blob = new Blob(audioChunks, {
      type: mediaRecorder.mimeType || 'audio/webm',
    })
    sendAudio(blob)
  })

  mediaRecorder.start(250)
  isRecording.value = true
  isPaused.value = false

  secondsLeft.value = MAX_RECORD_SECONDS
  setStatus(`Recording… (${secondsLeft.value}s)`, 'active')

  recordingTimer = setInterval(() => {
    if (isPaused.value) return
    secondsLeft.value--
    if (secondsLeft.value <= 0) {
      stopRecording()
    } else {
      setStatus(`Recording… (${secondsLeft.value}s)`, 'active')
    }
  }, 1000)
}

function pauseRecording() {
  mediaRecorder.pause()
  isPaused.value = true
  setStatus('Paused — click to resume', 'paused')
}

function resumeRecording() {
  mediaRecorder.resume()
  isPaused.value = false
  setStatus(`Recording… (${secondsLeft.value}s)`, 'active')
}

function stopRecording() {
  if (!mediaRecorder || !isRecording.value) return
  clearInterval(recordingTimer)
  recordingTimer = null
  isRecording.value = false
  isPaused.value = false
  isTranscribing.value = true
  mediaRecorder.stop()
  setStatus('Transcribing…', 'active')
}

async function sendAudio(blob) {
  try {
    const data = await apiTranscribe(blob)
    emit('transcribed', data.transcript)
    setStatus('Transcription complete. Edit if needed, then pick a preset.', 'success')
  } catch (err) {
    setStatus(`Transcription failed: ${err.message}`, 'error')
  } finally {
    isTranscribing.value = false
  }
}

onUnmounted(() => {
  clearInterval(recordingTimer)
  if (mediaRecorder && isRecording.value) {
    mediaRecorder.stop()
  }
})
</script>
