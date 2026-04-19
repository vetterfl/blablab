<template>
  <div v-if="show" class="modal-overlay" @click.self="emit('close')">
    <div class="modal-card">
      <div class="modal-header">
        <span class="refine-title">{{ isEdit ? 'Edit preset' : 'New preset' }}</span>
        <button class="modal-close-btn" @click="emit('close')" title="Close">&#x2715;</button>
      </div>

      <div class="modal-body">
        <label class="auth-label">Label <span class="required">*</span></label>
        <input
          v-model="form.label"
          class="auth-input"
          type="text"
          placeholder="e.g. Bullet points"
          autocomplete="off"
        />

        <label class="auth-label">Slug <span class="required">*</span></label>
        <input
          v-model="form.slug"
          class="auth-input"
          type="text"
          placeholder="e.g. bullet_points"
          :readonly="isEdit"
          :class="{ 'auth-input--readonly': isEdit }"
          autocomplete="off"
        />
        <span v-if="!isEdit" class="field-hint">Lowercase letters and underscores only.</span>

        <label class="auth-label">Prompt <span class="required">*</span></label>
        <textarea
          v-model="form.prompt"
          class="auth-input fancy-textarea"
          placeholder="System prompt for the LLM…"
          rows="5"
        ></textarea>

        <label class="auth-label">Model</label>
        <select v-model="form.model" class="auth-input">
          <option value="">Inherit from settings</option>
          <option
            v-for="m in settings.availableModels"
            :key="m"
            :value="m"
          >{{ m }}</option>
        </select>

        <label class="auth-label checkbox-label">
          <input v-model="form.subject_field" type="checkbox" class="checkbox-input" />
          Show subject field in output
        </label>
      </div>

      <div v-if="errorMsg" class="auth-error">{{ errorMsg }}</div>

      <div class="modal-footer">
        <button
          v-if="isEdit"
          class="btn btn-danger"
          :disabled="saving"
          @click="handleDelete"
        >
          {{ confirmDelete ? 'Confirm delete' : 'Delete' }}
        </button>
        <div class="modal-footer-right">
          <button class="btn btn-rerun" :disabled="saving" @click="emit('close')">Cancel</button>
          <button class="btn btn-copy" :disabled="saving" @click="handleSave">
            {{ saving ? 'Saving…' : 'Save' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, watch, computed } from 'vue'
import { useSettingsStore } from '../stores/settings.js'
import { usePresetsStore } from '../stores/presets.js'
import { apiCreatePreset, apiUpdatePreset } from '../api/client.js'

const props = defineProps({
  show: { type: Boolean, default: false },
  preset: { type: Object, default: null },
})

const emit = defineEmits(['close', 'saved'])

const settings = useSettingsStore()
const presets = usePresetsStore()

const isEdit = computed(() => !!props.preset)

const form = ref({ label: '', slug: '', prompt: '', model: '', subject_field: false })
const saving = ref(false)
const errorMsg = ref('')
const confirmDelete = ref(false)

watch(
  () => props.show,
  (visible) => {
    if (visible) {
      errorMsg.value = ''
      confirmDelete.value = false
      if (props.preset) {
        form.value = {
          label: props.preset.label ?? '',
          slug: props.preset.slug ?? '',
          prompt: props.preset.prompt ?? '',
          model: props.preset.model ?? '',
          subject_field: props.preset.subject_field ?? false,
        }
      } else {
        form.value = { label: '', slug: '', prompt: '', model: '', subject_field: false }
      }
    }
  },
  { immediate: true }
)

// Auto-generate slug from label in create mode
watch(
  () => form.value.label,
  (label) => {
    if (!isEdit.value) {
      form.value.slug = label
        .toLowerCase()
        .replace(/\s+/g, '_')
        .replace(/[^a-z0-9_]/g, '')
    }
  }
)

async function handleSave() {
  errorMsg.value = ''
  const { label, slug, prompt, model, subject_field } = form.value

  if (!label.trim()) { errorMsg.value = 'Label is required.'; return }
  if (!slug.trim())  { errorMsg.value = 'Slug is required.'; return }
  if (!prompt.trim()) { errorMsg.value = 'Prompt is required.'; return }

  saving.value = true
  try {
    if (isEdit.value) {
      await apiUpdatePreset(props.preset.slug, {
        label: label.trim(),
        prompt: prompt.trim(),
        model: model || null,
        subject_field,
      })
    } else {
      await apiCreatePreset({
        slug: slug.trim(),
        label: label.trim(),
        prompt: prompt.trim(),
        model: model || null,
        subject_field,
      })
    }
    await presets.fetchPresets()
    emit('saved')
    emit('close')
  } catch (err) {
    errorMsg.value = err.message
  } finally {
    saving.value = false
  }
}

async function handleDelete() {
  if (!confirmDelete.value) {
    confirmDelete.value = true
    return
  }
  saving.value = true
  errorMsg.value = ''
  try {
    await presets.deletePreset(props.preset.slug)
    emit('saved')
    emit('close')
  } catch (err) {
    errorMsg.value = err.message
  } finally {
    saving.value = false
    confirmDelete.value = false
  }
}
</script>

<style scoped>
.modal-overlay {
  position: fixed;
  inset: 0;
  z-index: 200;
  background: rgba(0, 0, 0, 0.6);
  display: flex;
  align-items: center;
  justify-content: center;
}

.modal-card {
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  padding: 28px;
  width: 100%;
  max-width: 480px;
  display: flex;
  flex-direction: column;
  gap: 0;
  max-height: 90vh;
  overflow-y: auto;
}

.modal-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 16px;
}

.modal-close-btn {
  background: none;
  border: none;
  color: var(--text-muted);
  cursor: pointer;
  font-size: 16px;
  padding: 4px 6px;
  border-radius: var(--radius-chip);
  line-height: 1;
}

.modal-close-btn:hover {
  color: var(--text-strong);
  background: var(--chip-bg);
}

.modal-body {
  display: flex;
  flex-direction: column;
  gap: 0;
}

.field-hint {
  font-size: 11px;
  color: var(--text-muted);
  margin-top: 3px;
}

.required {
  color: #f87171;
}

.auth-input--readonly {
  opacity: 0.6;
  cursor: default;
}

.fancy-textarea {
  min-height: 100px;
  resize: vertical;
}

select.auth-input {
  appearance: none;
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='12' height='12' viewBox='0 0 12 12'%3E%3Cpath fill='%236b7985' d='M6 8L1 3h10z'/%3E%3C/svg%3E");
  background-repeat: no-repeat;
  background-position: right 10px center;
  padding-right: 28px;
}

select.auth-input option {
  background: var(--bg-card);
  color: var(--text);
}

.checkbox-label {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  margin-top: 0.5rem;
  font-size: 13px;
  color: var(--text);
}

.checkbox-input {
  width: 14px;
  height: 14px;
  accent-color: var(--accent);
  cursor: pointer;
  flex-shrink: 0;
}

.modal-footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-top: 20px;
  gap: 8px;
}

.modal-footer-right {
  display: flex;
  gap: 8px;
  margin-left: auto;
}

.btn-danger {
  background: transparent;
  color: #f87171;
  border: 1px solid rgba(239, 68, 68, 0.4);
  font-size: 12px;
  padding: 6px 12px;
  border-radius: var(--radius-chip);
}

.btn-danger:not(:disabled):hover {
  background: rgba(239, 68, 68, 0.1);
  border-color: #f87171;
}
</style>
