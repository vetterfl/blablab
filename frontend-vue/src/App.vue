<template>
  <LoginOverlay v-if="!auth.isLoggedIn" />

  <template v-else>
    <AppHeader
      :show-settings="showSettings"
      :show-users="showUsers"
      @toggle-settings="showSettings = !showSettings; showUsers = false"
      @toggle-users="showUsers = !showUsers; showSettings = false"
    />

    <div class="layout-body">
      <div class="col-left">
        <RecordSection @transcribed="onTranscribed" />
        <TranscriptSection v-model="transcript" />
        <RefinedSection :text="refined" />
      </div>
      <RefinePanel
        :transcript="transcript"
        :has-transcript="transcript.trim().length > 0"
        @refined="onRefined"
      />
    </div>

    <footer class="app-footer">
      <p>BlabLab &mdash; powered by Whisper &amp; OpenRouter</p>
    </footer>

    <!-- Settings modal -->
    <Transition name="modal">
      <div v-if="showSettings" class="modal-overlay" @mousedown.self="showSettings = false">
        <div class="modal-panel" role="dialog" aria-modal="true" aria-label="Settings">
          <button class="modal-close" @click="showSettings = false" aria-label="Close">
            <svg width="14" height="14" viewBox="0 0 14 14" fill="none">
              <path d="M1 1l12 12M13 1L1 13" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"/>
            </svg>
          </button>
          <SettingsPage />
        </div>
      </div>
    </Transition>

    <!-- Users modal -->
    <Transition name="modal">
      <div v-if="showUsers" class="modal-overlay" @mousedown.self="showUsers = false">
        <div class="modal-panel modal-panel--wide" role="dialog" aria-modal="true" aria-label="User Management">
          <button class="modal-close" @click="showUsers = false" aria-label="Close">
            <svg width="14" height="14" viewBox="0 0 14 14" fill="none">
              <path d="M1 1l12 12M13 1L1 13" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"/>
            </svg>
          </button>
          <UsersPage />
        </div>
      </div>
    </Transition>
  </template>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount } from 'vue'
import { useAuthStore } from './stores/auth.js'
import AppHeader from './components/AppHeader.vue'
import LoginOverlay from './components/LoginOverlay.vue'
import RecordSection from './components/RecordSection.vue'
import TranscriptSection from './components/TranscriptSection.vue'
import RefinedSection from './components/RefinedSection.vue'
import RefinePanel from './components/RefinePanel.vue'
import SettingsPage from './components/SettingsPage.vue'
import UsersPage from './components/UsersPage.vue'

const auth = useAuthStore()
const transcript = ref('')
const refined = ref('')
const showSettings = ref(false)
const showUsers = ref(false)

function onTranscribed(text) {
  transcript.value = text
  refined.value = ''
}

function onRefined(text) {
  refined.value = text
}

function onKeydown(e) {
  if (e.key === 'Escape') {
    showSettings.value = false
    showUsers.value = false
  }
}

onMounted(() => document.addEventListener('keydown', onKeydown))
onBeforeUnmount(() => document.removeEventListener('keydown', onKeydown))
</script>

<style>
.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.55);
  backdrop-filter: blur(2px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 150;
  padding: 24px;
}

.modal-panel {
  position: relative;
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: 12px;
  width: 100%;
  max-width: 520px;
  max-height: 88vh;
  overflow: hidden;
  display: flex;
  flex-direction: column;
  box-shadow: 0 24px 64px rgba(0, 0, 0, 0.5);
}

.modal-panel--wide {
  max-width: 680px;
}

.modal-close {
  position: absolute;
  top: 16px;
  right: 16px;
  width: 28px;
  height: 28px;
  border-radius: 6px;
  background: var(--chip-bg);
  border: 1px solid var(--border);
  color: var(--text-muted);
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 10;
  transition: background 0.12s, color 0.12s, border-color 0.12s;
}

.modal-close:hover {
  background: rgba(239, 68, 68, 0.1);
  border-color: rgba(239, 68, 68, 0.3);
  color: #f87171;
}

/* Scroll the inner content, not the panel */
.modal-panel > * {
  overflow: auto;
  flex: 1;
  min-height: 0;
}

/* Modal transition */
.modal-enter-active {
  transition: opacity 0.18s ease, transform 0.18s ease;
}
.modal-leave-active {
  transition: opacity 0.13s ease, transform 0.13s ease;
}
.modal-enter-from {
  opacity: 0;
  transform: scale(0.97) translateY(6px);
}
.modal-leave-to {
  opacity: 0;
  transform: scale(0.97) translateY(6px);
}
</style>
