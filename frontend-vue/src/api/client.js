import { useAuthStore } from '../stores/auth.js'

export async function authFetch(url, options = {}) {
  const auth = useAuthStore()
  const headers = {
    ...options.headers,
    ...(auth.token ? { Authorization: `Bearer ${auth.token}` } : {}),
  }
  const res = await fetch(url, { ...options, headers })
  if (res.status === 401) {
    auth.logout()
    throw new Error('Session expired. Please sign in again.')
  }
  return res
}

export async function apiLogin(username, password) {
  const res = await fetch('/api/auth/login', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ username, password }),
  })
  const data = await res.json()
  if (!res.ok) throw new Error(data.detail || 'Login failed')
  return data
}

export async function apiGetPresets() {
  const res = await authFetch('/api/presets')
  const data = await res.json()
  if (!res.ok) throw new Error(data.detail || `HTTP ${res.status}`)
  return data
}

export async function apiRefine(transcript, presetId) {
  const res = await authFetch('/api/refine', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ transcript, preset_id: presetId }),
  })
  const data = await res.json()
  if (!res.ok) throw new Error(data.detail || `HTTP ${res.status}`)
  return data
}

export async function apiGetSettings() {
  const res = await authFetch('/api/settings')
  const data = await res.json()
  if (!res.ok) throw new Error(data.detail || `HTTP ${res.status}`)
  return data
}

export async function apiTranscribe(blob) {
  const formData = new FormData()
  const ext = blob.type.includes('ogg') ? 'ogg' : 'webm'
  formData.append('audio', blob, `recording.${ext}`)
  const res = await authFetch('/api/transcribe', {
    method: 'POST',
    body: formData,
  })
  const data = await res.json()
  if (!res.ok) throw new Error(data.detail || `HTTP ${res.status}`)
  return data
}

export async function apiCreatePreset(preset) {
  const res = await authFetch('/api/presets', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(preset),
  })
  const data = await res.json()
  if (!res.ok) throw new Error(data.detail || `HTTP ${res.status}`)
  return data
}

export async function apiUpdatePreset(slug, preset) {
  const res = await authFetch(`/api/presets/${slug}`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(preset),
  })
  const data = await res.json()
  if (!res.ok) throw new Error(data.detail || `HTTP ${res.status}`)
  return data
}

export async function apiDeletePreset(slug) {
  const res = await authFetch(`/api/presets/${slug}`, { method: 'DELETE' })
  if (!res.ok) {
    const data = await res.json().catch(() => ({}))
    throw new Error(data.detail || `HTTP ${res.status}`)
  }
}

export async function apiUpdateSettings(settings) {
  const res = await authFetch('/api/settings', {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(settings),
  })
  const data = await res.json()
  if (!res.ok) throw new Error(data.detail || `HTTP ${res.status}`)
  return data
}

export async function apiChangePassword(currentPassword, newPassword) {
  const res = await authFetch('/api/settings/change-password', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ current_password: currentPassword, new_password: newPassword }),
  })
  const data = await res.json()
  if (!res.ok) throw new Error(data.detail || `HTTP ${res.status}`)
  return data
}
