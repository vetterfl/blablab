import { defineStore } from 'pinia'
import { ref, watch } from 'vue'
import { useAuthStore } from './auth.js'
import { apiGetSettings, apiUpdateSettings, apiChangePassword } from '../api/client.js'

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

  async function updateDefaultModel(model) {
    const data = await apiUpdateSettings({ default_model: model })
    defaultModel.value = data.default_model ?? model
  }

  async function changePassword(currentPassword, newPassword) {
    await apiChangePassword(currentPassword, newPassword)
  }

  // Auto-fetch when user logs in
  const auth = useAuthStore()
  watch(
    () => auth.isLoggedIn,
    (loggedIn) => {
      if (loggedIn) fetchSettings()
      else { defaultModel.value = null; availableModels.value = [] }
    },
    { immediate: true }
  )

  return { defaultModel, availableModels, fetchSettings, updateDefaultModel, changePassword }
})
