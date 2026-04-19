import { defineStore } from 'pinia'
import { ref, watch } from 'vue'
import { useAuthStore } from './auth.js'
import { apiGetPresets, apiRefine, apiDeletePreset } from '../api/client.js'

export const usePresetsStore = defineStore('presets', () => {
  const items = ref([])
  const loading = ref(false)
  const error = ref(null)

  async function fetchPresets() {
    loading.value = true
    error.value = null
    try {
      const data = await apiGetPresets()
      // backend returns { presets: [...] } or just an array
      items.value = Array.isArray(data) ? data : (data.presets ?? [])
    } catch (err) {
      error.value = err.message
      items.value = []
    } finally {
      loading.value = false
    }
  }

  async function refine(presetId, transcript) {
    const data = await apiRefine(transcript, presetId)
    return data.refined
  }

  async function deletePreset(slug) {
    await apiDeletePreset(slug)
    items.value = items.value.filter((p) => p.slug !== slug)
  }

  // Auto-fetch when user logs in
  const auth = useAuthStore()
  watch(
    () => auth.isLoggedIn,
    (loggedIn) => {
      if (loggedIn) fetchPresets()
      else items.value = []
    },
    { immediate: true }
  )

  return { items, loading, error, fetchPresets, refine, deletePreset }
})
