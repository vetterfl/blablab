<template>
  <div class="settings-page">
    <div class="settings-inner">
      <h2 class="settings-title">Settings</h2>

      <!-- Default model -->
      <section class="settings-section">
        <h3 class="settings-section-title">Default model</h3>
        <p class="settings-section-desc">Used for refine when a preset has no model override.</p>
        <div class="settings-row">
          <select
            v-model="selectedModel"
            class="auth-input settings-select"
            :disabled="modelSaving"
            @change="handleModelChange"
          >
            <option v-if="!settings.availableModels.length" value="">Loading models…</option>
            <option
              v-for="m in settings.availableModels"
              :key="m"
              :value="m"
            >{{ m }}</option>
          </select>
          <span v-if="modelStatus" :class="['settings-feedback', modelStatusType]">{{ modelStatus }}</span>
        </div>
      </section>

      <div class="settings-divider"></div>

      <!-- Change password -->
      <section class="settings-section">
        <h3 class="settings-section-title">Change password</h3>
        <form @submit.prevent="handleChangePassword" novalidate>
          <label class="auth-label">Current password</label>
          <input
            v-model="currentPw"
            type="password"
            class="auth-input"
            autocomplete="current-password"
            placeholder="••••••••"
          />

          <label class="auth-label">New password</label>
          <input
            v-model="newPw"
            type="password"
            class="auth-input"
            autocomplete="new-password"
            placeholder="••••••••"
          />

          <label class="auth-label">Confirm new password</label>
          <input
            v-model="confirmPw"
            type="password"
            class="auth-input"
            autocomplete="new-password"
            placeholder="••••••••"
          />

          <div v-if="pwError" class="auth-error settings-feedback-block">{{ pwError }}</div>
          <div v-if="pwSuccess" class="settings-success-block">{{ pwSuccess }}</div>

          <button
            type="submit"
            class="btn btn-copy settings-submit-btn"
            :disabled="pwSaving"
          >
            {{ pwSaving ? 'Saving…' : 'Change password' }}
          </button>
        </form>
      </section>
    </div>
  </div>
</template>

<script setup>
import { ref, watch } from 'vue'
import { useSettingsStore } from '../stores/settings.js'

const settings = useSettingsStore()

// Model
const selectedModel = ref(settings.defaultModel ?? '')
const modelSaving = ref(false)
const modelStatus = ref('')
const modelStatusType = ref('')

watch(
  () => settings.defaultModel,
  (val) => { if (val) selectedModel.value = val }
)

async function handleModelChange() {
  modelSaving.value = true
  modelStatus.value = ''
  try {
    await settings.updateDefaultModel(selectedModel.value)
    modelStatus.value = 'Saved'
    modelStatusType.value = 'success'
    setTimeout(() => { modelStatus.value = '' }, 2000)
  } catch (err) {
    modelStatus.value = err.message
    modelStatusType.value = 'error'
  } finally {
    modelSaving.value = false
  }
}

// Password
const currentPw = ref('')
const newPw = ref('')
const confirmPw = ref('')
const pwSaving = ref(false)
const pwError = ref('')
const pwSuccess = ref('')

async function handleChangePassword() {
  pwError.value = ''
  pwSuccess.value = ''

  if (!currentPw.value) { pwError.value = 'Enter your current password.'; return }
  if (!newPw.value)     { pwError.value = 'Enter a new password.'; return }
  if (newPw.value !== confirmPw.value) { pwError.value = 'New passwords do not match.'; return }

  pwSaving.value = true
  try {
    await settings.changePassword(currentPw.value, newPw.value)
    pwSuccess.value = 'Password changed successfully.'
    currentPw.value = ''
    newPw.value = ''
    confirmPw.value = ''
  } catch (err) {
    pwError.value = err.message
  } finally {
    pwSaving.value = false
  }
}
</script>

<style scoped>
.settings-page {
  flex: 1;
  overflow: auto;
  padding: 32px 28px;
  display: flex;
  justify-content: center;
}

.settings-inner {
  width: 100%;
  max-width: 480px;
  display: flex;
  flex-direction: column;
  gap: 0;
}

.settings-title {
  font-size: 20px;
  font-weight: 700;
  color: var(--text-strong);
  letter-spacing: -0.3px;
  margin-bottom: 24px;
}

.settings-section {
  display: flex;
  flex-direction: column;
  gap: 0;
  padding: 20px 0;
}

.settings-section-title {
  font-size: 14px;
  font-weight: 700;
  color: var(--text-strong);
  margin-bottom: 4px;
}

.settings-section-desc {
  font-size: 12px;
  color: var(--text-muted);
  margin-bottom: 12px;
}

.settings-divider {
  height: 1px;
  background: var(--border);
}

.settings-row {
  display: flex;
  align-items: center;
  gap: 12px;
}

.settings-select {
  flex: 1;
  appearance: none;
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='12' height='12' viewBox='0 0 12 12'%3E%3Cpath fill='%236b7985' d='M6 8L1 3h10z'/%3E%3C/svg%3E");
  background-repeat: no-repeat;
  background-position: right 10px center;
  padding-right: 28px;
}

.settings-select option {
  background: var(--bg-card);
  color: var(--text);
}

.settings-feedback {
  font-size: 12px;
  font-weight: 500;
  white-space: nowrap;
}

.settings-feedback.success { color: var(--green); }
.settings-feedback.error   { color: #f87171; }

.settings-feedback-block {
  margin-top: 10px;
}

.settings-success-block {
  margin-top: 10px;
  font-size: 12px;
  color: var(--green);
  background: rgba(16, 185, 129, 0.1);
  border: 1px solid rgba(16, 185, 129, 0.25);
  border-radius: var(--radius-chip);
  padding: 0.5rem 0.75rem;
}

.settings-submit-btn {
  margin-top: 16px;
  align-self: flex-start;
}
</style>
