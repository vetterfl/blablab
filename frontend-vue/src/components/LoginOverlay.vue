<template>
  <div class="auth-overlay">
    <div class="auth-card">
      <div class="auth-logo">
        <div class="logo-dot"></div>
        <span class="logo-text">BlabLab</span>
      </div>
      <h1 class="auth-title">Sign in</h1>
      <p v-if="errorMsg" class="auth-error">{{ errorMsg }}</p>
      <form @submit.prevent="handleSubmit" autocomplete="on">
        <label class="auth-label" for="auth-username">Username</label>
        <input
          id="auth-username"
          v-model="username"
          class="auth-input"
          type="text"
          name="username"
          autocomplete="username"
          required
        />
        <label class="auth-label" for="auth-password">Password</label>
        <input
          id="auth-password"
          v-model="password"
          class="auth-input"
          type="password"
          name="password"
          autocomplete="current-password"
          required
        />
        <button type="submit" class="btn auth-btn" :disabled="loading">
          {{ loading ? 'Signing in…' : 'Sign in' }}
        </button>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useAuthStore } from '../stores/auth.js'

const auth = useAuthStore()
const username = ref('')
const password = ref('')
const loading = ref(false)
const errorMsg = ref('')

async function handleSubmit() {
  errorMsg.value = ''
  loading.value = true
  try {
    await auth.login(username.value.trim(), password.value)
    username.value = ''
    password.value = ''
  } catch (err) {
    errorMsg.value = err.message
  } finally {
    loading.value = false
  }
}
</script>
