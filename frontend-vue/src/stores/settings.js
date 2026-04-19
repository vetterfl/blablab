import { defineStore } from 'pinia'
import { ref } from 'vue'
import { apiGetSettings } from '../api/client.js'

export const useSettingsStore = defineStore('settings', () => {
  const defaultModel = ref(null)
  const availableModels = ref([])

  async function fetchSettings() {
    try {
      const data = await apiGetSettings()
      defaultModel.value = data.default_model ?? null
      availableModels.value = data.available_models ?? []
    } catch {
      // silently ignore — settings are non-critical
    }
  }

  return { defaultModel, availableModels, fetchSettings }
})
