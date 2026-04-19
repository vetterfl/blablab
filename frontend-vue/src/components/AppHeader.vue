<template>
  <header class="app-header">
    <div class="header-inner">
      <div class="logo">
        <div class="logo-dot"></div>
        <span class="logo-text">BlabLab</span>
      </div>
      <p class="tagline">Speak. Transcribe. Refine.</p>
      <button class="btn btn-logout" @click="auth.logout()">Sign out</button>
    </div>
  </header>
</template>

<script setup>
import { useAuthStore } from '../stores/auth.js'
const auth = useAuthStore()
</script>
