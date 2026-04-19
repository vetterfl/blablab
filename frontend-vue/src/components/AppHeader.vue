<template>
  <header class="app-header">
    <div class="header-inner">
      <div class="logo">
        <div class="logo-dot"></div>
        <span class="logo-text">BlabLab</span>
      </div>
      <p class="tagline">Speak. Transcribe. Refine.</p>

      <div class="avatar-wrapper" ref="wrapperRef">
        <button
          class="avatar-btn"
          :class="{ 'avatar-btn--open': open }"
          @click="open = !open"
          :aria-expanded="open"
          aria-label="Account menu"
        >
          <span class="avatar-initials">{{ initials }}</span>
          <span class="avatar-chevron" :class="{ 'avatar-chevron--up': open }">
            <svg width="10" height="6" viewBox="0 0 10 6" fill="none">
              <path d="M1 1l4 4 4-4" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
          </span>
        </button>

        <Transition name="dropdown">
          <div v-if="open" class="dropdown" role="menu">
            <div class="dropdown-header">
              <div class="dropdown-avatar">{{ initials }}</div>
              <div class="dropdown-user-info">
                <span class="dropdown-username">{{ auth.username ?? 'Account' }}</span>
                <span v-if="auth.isAdmin" class="dropdown-role">Admin</span>
              </div>
            </div>

            <div class="dropdown-divider"></div>

            <button
              v-if="auth.isAdmin"
              class="dropdown-item"
              :class="{ 'dropdown-item--active': showUsers }"
              role="menuitem"
              @click="select('users')"
            >
              <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">
                <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/>
                <circle cx="9" cy="7" r="4"/>
                <path d="M23 21v-2a4 4 0 0 0-3-3.87"/>
                <path d="M16 3.13a4 4 0 0 1 0 7.75"/>
              </svg>
              Users
            </button>

            <button
              class="dropdown-item"
              :class="{ 'dropdown-item--active': showSettings }"
              role="menuitem"
              @click="select('settings')"
            >
              <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">
                <circle cx="12" cy="12" r="3"/>
                <path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1-2.83 2.83l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-4 0v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83-2.83l.06-.06A1.65 1.65 0 0 0 4.68 15a1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1 0-4h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 2.83-2.83l.06.06A1.65 1.65 0 0 0 9 4.68a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 4 0v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 2.83l-.06.06A1.65 1.65 0 0 0 19.4 9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 0 4h-.09a1.65 1.65 0 0 0-1.51 1z"/>
              </svg>
              Settings
            </button>

            <div class="dropdown-divider"></div>

            <button
              class="dropdown-item dropdown-item--danger"
              role="menuitem"
              @click="handleLogout"
            >
              <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">
                <path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"/>
                <polyline points="16 17 21 12 16 7"/>
                <line x1="21" y1="12" x2="9" y2="12"/>
              </svg>
              Sign out
            </button>
          </div>
        </Transition>
      </div>
    </div>
  </header>
</template>

<script setup>
import { ref, computed, onMounted, onBeforeUnmount } from 'vue'
import { useAuthStore } from '../stores/auth.js'

const auth = useAuthStore()
const open = ref(false)
const wrapperRef = ref(null)

const props = defineProps({
  showSettings: { type: Boolean, default: false },
  showUsers: { type: Boolean, default: false },
})

const emit = defineEmits(['toggleSettings', 'toggleUsers'])

const initials = computed(() => {
  const name = auth.username ?? '?'
  return name.slice(0, 2).toUpperCase()
})

function select(target) {
  open.value = false
  if (target === 'settings') emit('toggleSettings')
  if (target === 'users') emit('toggleUsers')
}

function handleLogout() {
  open.value = false
  auth.logout()
}

function onOutsideClick(e) {
  if (wrapperRef.value && !wrapperRef.value.contains(e.target)) {
    open.value = false
  }
}

onMounted(() => document.addEventListener('mousedown', onOutsideClick))
onBeforeUnmount(() => document.removeEventListener('mousedown', onOutsideClick))
</script>

<style scoped>
.avatar-wrapper {
  position: relative;
}

.avatar-btn {
  display: flex;
  align-items: center;
  gap: 6px;
  background: var(--chip-bg);
  border: 1px solid var(--border);
  border-radius: 999px;
  padding: 4px 10px 4px 4px;
  cursor: pointer;
  transition: border-color 0.15s, background 0.15s;
  color: var(--text-muted);
}

.avatar-btn:hover,
.avatar-btn--open {
  border-color: var(--accent);
  background: rgba(56, 189, 248, 0.07);
  color: var(--accent);
}

.avatar-initials {
  width: 26px;
  height: 26px;
  border-radius: 999px;
  background: linear-gradient(135deg, var(--accent) 0%, #0ea5e9 100%);
  color: var(--on-accent);
  font-size: 10px;
  font-weight: 700;
  letter-spacing: 0.5px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.avatar-chevron {
  display: flex;
  align-items: center;
  transition: transform 0.2s ease;
}

.avatar-chevron--up {
  transform: rotate(180deg);
}

/* Dropdown */
.dropdown {
  position: absolute;
  top: calc(100% + 8px);
  right: 0;
  width: 220px;
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: 10px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.4), 0 2px 8px rgba(0, 0, 0, 0.3);
  overflow: hidden;
  z-index: 200;
  transform-origin: top right;
}

.dropdown-header {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 14px 14px 12px;
}

.dropdown-avatar {
  width: 34px;
  height: 34px;
  border-radius: 999px;
  background: linear-gradient(135deg, var(--accent) 0%, #0ea5e9 100%);
  color: var(--on-accent);
  font-size: 11px;
  font-weight: 700;
  letter-spacing: 0.5px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.dropdown-user-info {
  display: flex;
  flex-direction: column;
  gap: 2px;
  min-width: 0;
}

.dropdown-username {
  font-size: 13px;
  font-weight: 600;
  color: var(--text-strong);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.dropdown-role {
  font-size: 10px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  color: var(--accent);
}

.dropdown-divider {
  height: 1px;
  background: var(--border);
  margin: 2px 0;
}

.dropdown-item {
  display: flex;
  align-items: center;
  gap: 10px;
  width: 100%;
  padding: 9px 14px;
  background: none;
  border: none;
  cursor: pointer;
  font-size: 13px;
  color: var(--text);
  text-align: left;
  transition: background 0.12s, color 0.12s;
}

.dropdown-item:hover {
  background: rgba(56, 189, 248, 0.07);
  color: var(--text-strong);
}

.dropdown-item--active {
  color: var(--accent);
  background: rgba(56, 189, 248, 0.08);
}

.dropdown-item--danger {
  color: var(--text-muted);
}

.dropdown-item--danger:hover {
  background: rgba(239, 68, 68, 0.08);
  color: #f87171;
}

/* Transition */
.dropdown-enter-active {
  transition: opacity 0.15s ease, transform 0.15s ease;
}
.dropdown-leave-active {
  transition: opacity 0.1s ease, transform 0.1s ease;
}
.dropdown-enter-from {
  opacity: 0;
  transform: scale(0.95) translateY(-4px);
}
.dropdown-leave-to {
  opacity: 0;
  transform: scale(0.95) translateY(-4px);
}
</style>
