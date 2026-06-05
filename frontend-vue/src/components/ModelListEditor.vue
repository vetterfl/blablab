<template>
  <section class="settings-section">
    <h3 class="settings-section-title">{{ title }}</h3>
    <p class="settings-section-desc">{{ description }}</p>

    <div class="model-chips" v-if="models.length">
      <span v-for="m in models" :key="m.id" class="model-chip">
        <span class="model-chip-slug">{{ m.slug }}</span>
        <button
          type="button"
          class="model-chip-remove"
          :disabled="busy"
          @click="handleDelete(m)"
          aria-label="Remove model"
        >×</button>
      </span>
    </div>
    <div v-else class="model-empty">No models configured yet.</div>

    <div class="model-add-row">
      <input
        v-model="newSlug"
        :list="datalistId"
        class="auth-input model-add-input"
        :placeholder="placeholder"
        :disabled="busy"
        @focus="ensureCatalog"
        @keyup.enter="handleAdd"
      />
      <datalist :id="datalistId">
        <option v-for="s in catalogFiltered" :key="s" :value="s" />
      </datalist>
      <button
        type="button"
        class="btn btn-copy model-add-btn"
        :disabled="busy || !newSlug.trim()"
        @click="handleAdd"
      >{{ busy ? '…' : 'Add' }}</button>
    </div>
    <div v-if="errorMsg" class="auth-error settings-feedback-block">{{ errorMsg }}</div>
    <div v-if="successMsg" class="settings-success-block">{{ successMsg }}</div>
  </section>
</template>

<script setup>
import { computed, ref, onMounted } from 'vue'
import {
  apiListAvailableModels,
  apiAddAvailableModel,
  apiDeleteAvailableModel,
  apiGetOpenRouterCatalog,
} from '../api/client.js'

const props = defineProps({
  kind: { type: String, required: true },          // 'refine' | 'transcription'
  title: { type: String, required: true },
  description: { type: String, default: '' },
  placeholder: { type: String, default: 'e.g. openai/gpt-4o-mini' },
})
const emit = defineEmits(['changed'])

const datalistId = `catalog-${props.kind}`

const models = ref([])
const newSlug = ref('')
const busy = ref(false)
const errorMsg = ref('')
const successMsg = ref('')

const catalog = ref([])
const catalogLoaded = ref(false)

const catalogFiltered = computed(() => {
  const existing = new Set(models.value.map(m => m.slug))
  return catalog.value.filter(s => !existing.has(s))
})

async function loadModels() {
  try {
    models.value = await apiListAvailableModels(props.kind)
  } catch (err) {
    errorMsg.value = err.message
  }
}

async function ensureCatalog() {
  if (catalogLoaded.value) return
  try {
    catalog.value = await apiGetOpenRouterCatalog(props.kind)
    catalogLoaded.value = true
  } catch (err) {
    // soft-fail: autocomplete just won't have suggestions
    catalogLoaded.value = true
  }
}

function flashSuccess(msg) {
  successMsg.value = msg
  setTimeout(() => { successMsg.value = '' }, 2000)
}

async function handleAdd() {
  const slug = newSlug.value.trim()
  if (!slug) return
  errorMsg.value = ''
  successMsg.value = ''
  busy.value = true
  try {
    await apiAddAvailableModel(slug, props.kind)
    newSlug.value = ''
    await loadModels()
    emit('changed')
    flashSuccess(`Added ${slug}.`)
  } catch (err) {
    errorMsg.value = err.message
  } finally {
    busy.value = false
  }
}

async function handleDelete(model) {
  errorMsg.value = ''
  successMsg.value = ''
  busy.value = true
  try {
    await apiDeleteAvailableModel(model.id)
    await loadModels()
    emit('changed')
  } catch (err) {
    errorMsg.value = err.message
  } finally {
    busy.value = false
  }
}

onMounted(loadModels)
</script>

<style scoped>
.model-chips {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  margin-bottom: 12px;
}

.model-chip {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 4px 4px 4px 10px;
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: var(--radius-chip);
  font-size: 12px;
  color: var(--text);
}

.model-chip-slug {
  font-family: var(--mono, ui-monospace, SFMono-Regular, monospace);
}

.model-chip-remove {
  appearance: none;
  background: transparent;
  border: none;
  color: var(--text-muted);
  cursor: pointer;
  font-size: 16px;
  line-height: 1;
  padding: 0 4px;
  border-radius: 4px;
}
.model-chip-remove:hover:not(:disabled) {
  background: rgba(248, 113, 113, 0.15);
  color: #f87171;
}
.model-chip-remove:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}

.model-empty {
  font-size: 12px;
  color: var(--text-muted);
  font-style: italic;
  margin-bottom: 12px;
}

.model-add-row {
  display: flex;
  gap: 8px;
}

.model-add-input {
  flex: 1;
}

.model-add-btn {
  white-space: nowrap;
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

.settings-section {
  display: flex;
  flex-direction: column;
  padding: 20px 0;
}

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
</style>
