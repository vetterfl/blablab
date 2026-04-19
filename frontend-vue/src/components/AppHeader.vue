<template>
  <header class="app-header">
    <div class="header-inner">
      <div class="logo">
        <div class="logo-dot"></div>
        <span class="logo-text">BlabLab</span>
      </div>
      <p class="tagline">Speak. Transcribe. Refine.</p>
      <div class="header-actions">
        <button
          v-if="auth.isAdmin"
          :class="['btn', 'btn-logout', { 'btn-logout--active': showUsers }]"
          @click="emit('toggleUsers')"
        >
          Users
        </button>
        <button
          :class="['btn', 'btn-logout', { 'btn-logout--active': showSettings }]"
          @click="emit('toggleSettings')"
        >
          Settings
        </button>
        <button class="btn btn-logout" @click="auth.logout()">Sign out</button>
      </div>
    </div>
  </header>
</template>

<script setup>
import { useAuthStore } from '../stores/auth.js'

const auth = useAuthStore()

defineProps({
  showSettings: { type: Boolean, default: false },
  showUsers: { type: Boolean, default: false },
})

const emit = defineEmits(['toggleSettings', 'toggleUsers'])
</script>

<style scoped>
.header-actions {
  display: flex;
  gap: 8px;
  align-items: center;
}

.btn-logout--active {
  background: var(--chip-bg);
  color: var(--accent);
  border-color: var(--accent);
}
</style>
