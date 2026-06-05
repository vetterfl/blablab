import { defineStore } from 'pinia'
import { ref, watch } from 'vue'
import { useAuthStore } from './auth.js'
import {
  apiGetSettings,
  apiUpdateSettings,
  apiChangePassword,
  apiGetTranscriptionSettings,
  apiUpdateTranscriptionSettings,
} from '../api/client.js'

export const useSettingsStore = defineStore('settings', () => {
  const defaultModel = ref(null)
  const availableModels = ref([])
  const transcriptionModel = ref(null)
  const availableTranscriptionModels = ref([])

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
      }
    },
    { immediate: true }
  )

  return {
    defaultModel,
    availableModels,
    transcriptionModel,
    availableTranscriptionModels,
    fetchSettings,
    updateDefaultModel,
    updateTranscriptionModel,
    changePassword,
  }
})
