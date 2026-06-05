import { defineStore } from 'pinia'
import { ref, watch } from 'vue'
import { useAuthStore } from './auth.js'
import {
  apiGetSettings,
  apiUpdateSettings,
  apiChangePassword,
  apiGetTranscriptionSettings,
  apiUpdateTranscriptionSettings,
  apiGetLimits,
  apiUpdateLimits,
} from '../api/client.js'

const DEFAULT_LIMITS = {
  max_audio_bytes: 25 * 1024 * 1024,
  max_recording_seconds: 90,
  max_transcript_chars: 2000,
}

export const useSettingsStore = defineStore('settings', () => {
  const defaultModel = ref(null)
  const availableModels = ref([])
  const transcriptionModel = ref(null)
  const availableTranscriptionModels = ref([])
  const limits = ref({ ...DEFAULT_LIMITS })

  async function fetchSettings() {
    try {
      const data = await apiGetSettings()
      defaultModel.value = data.default_model ?? null
      availableModels.value = data.available_models ?? []
    } catch {
      // silently ignore — settings are non-critical
    }
    try {
      const data = await apiGetTranscriptionSettings()
      transcriptionModel.value = data.transcription_model ?? null
      availableTranscriptionModels.value = data.available_models ?? []
    } catch {
      // silently ignore
    }
    try {
      limits.value = await apiGetLimits()
    } catch {
      // fall back to defaults
    }
  }

  async function updateLimits(newLimits) {
    const data = await apiUpdateLimits(newLimits)
    limits.value = data
  }

  async function updateDefaultModel(model) {
    const data = await apiUpdateSettings({ default_model: model })
    defaultModel.value = data.default_model ?? model
  }

  async function updateTranscriptionModel(model) {
    const data = await apiUpdateTranscriptionSettings(model)
    transcriptionModel.value = data.transcription_model ?? model
  }

  async function changePassword(currentPassword, newPassword) {
    await apiChangePassword(currentPassword, newPassword)
  }

  const auth = useAuthStore()
  watch(
    () => auth.isLoggedIn,
    (loggedIn) => {
      if (loggedIn) fetchSettings()
      else {
        defaultModel.value = null
        availableModels.value = []
        transcriptionModel.value = null
        availableTranscriptionModels.value = []
        limits.value = { ...DEFAULT_LIMITS }
      }
    },
    { immediate: true }
  )

  return {
    defaultModel,
    availableModels,
    transcriptionModel,
    availableTranscriptionModels,
    limits,
    fetchSettings,
    updateDefaultModel,
    updateTranscriptionModel,
    updateLimits,
    changePassword,
  }
})
