import { defineStore } from 'pinia'
import { computed, ref } from 'vue'

const USD_TO_EUR = 0.92

export const useStatsStore = defineStore('stats', () => {
  const audioDurationSec = ref(null)
  const audioBytes = ref(null)
  const transcriptChars = ref(null)
  const refinedChars = ref(null)
  const transcribeCostUsd = ref(null)
  const refineCostUsd = ref(null)

  function reset() {
    audioDurationSec.value = null
    audioBytes.value = null
    transcriptChars.value = null
    refinedChars.value = null
    transcribeCostUsd.value = null
    refineCostUsd.value = null
  }

  function recordTranscribe({ durationSec, audioBytes: bytes, transcript, costUsd }) {
    audioDurationSec.value = durationSec ?? null
    audioBytes.value = bytes ?? null
    transcriptChars.value = transcript ? transcript.length : 0
    refinedChars.value = null
    transcribeCostUsd.value = costUsd ?? null
    refineCostUsd.value = null
  }

  function recordRefine({ refined, costUsd }) {
    refinedChars.value = refined ? refined.length : 0
    refineCostUsd.value = costUsd ?? null
  }

  const hasAny = computed(
    () => audioDurationSec.value != null
      || audioBytes.value != null
      || transcriptChars.value != null
      || refinedChars.value != null
      || transcribeCostUsd.value != null
      || refineCostUsd.value != null
  )

  const totalCostEur = computed(() => {
    const t = transcribeCostUsd.value
    const r = refineCostUsd.value
    if (t == null && r == null) return null
    return ((t ?? 0) + (r ?? 0)) * USD_TO_EUR
  })

  return {
    audioDurationSec,
    audioBytes,
    transcriptChars,
    refinedChars,
    transcribeCostUsd,
    refineCostUsd,
    hasAny,
    totalCostEur,
    reset,
    recordTranscribe,
    recordRefine,
  }
})
