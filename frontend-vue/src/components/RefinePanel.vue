<template>
  <div class="col-right">
    <div>
      <div class="step-label step-label--accent">Refine</div>
      <div class="refine-title">Refine with AI</div>
      <div class="refine-subtitle">Pick a preset to reformat your transcript.</div>
    </div>

    <div>
      <div class="section-label">Quick presets</div>
      <div class="preset-buttons">
        <span v-if="presets.loading" class="loading-presets">Loading presets…</span>
        <span v-else-if="presets.error" class="status-text error">
          Failed to load presets: {{ presets.error }}
        </span>
        <template v-else>
          <div
            v-for="preset in presets.items"
            :key="preset.id ?? preset.slug"
            class="preset-chip-wrap"
          >
            <button
              :class="['btn-preset', { active: activePresetId === (preset.id ?? preset.slug) }]"
              :disabled="refining || !hasTranscript"
              @click="handleRefine(preset)"
            >
              {{ preset.label }}
            </button>
            <button
              class="btn-preset-edit"
              title="Edit preset"
              @click.stop="openEdit(preset)"
            >&#9998;</button>
          </div>
          <span v-if="!presets.items.length" class="loading-presets">No presets found.</span>
        </template>
      </div>

      <button class="btn btn-rerun btn-new-preset" @click="openCreate">
        + New preset
      </button>
    </div>

    <div v-if="statusMsg" class="divider"></div>
    <p v-if="statusMsg" :class="['status-text', statusType]">{{ statusMsg }}</p>
  </div>

  <PresetEditor
    :show="editorVisible"
    :preset="editingPreset"
    @close="editorVisible = false"
    @saved="onSaved"
  />
</template>

<script setup>
import { ref } from 'vue'
import { usePresetsStore } from '../stores/presets.js'
import PresetEditor from './PresetEditor.vue'

const props = defineProps({
  transcript: {
    type: String,
    default: '',
  },
  hasTranscript: {
    type: Boolean,
    default: false,
  },
})

const emit = defineEmits(['refined'])

const presets = usePresetsStore()
const activePresetId = ref(null)
const refining = ref(false)
const statusMsg = ref('')
const statusType = ref('')

const editorVisible = ref(false)
const editingPreset = ref(null)

function setStatus(msg, type = '') {
  statusMsg.value = msg
  statusType.value = type
}

async function handleRefine(preset) {
  const transcript = props.transcript.trim()
  if (!transcript) {
    setStatus('Nothing to refine — transcript is empty.', 'error')
    return
  }

  const id = preset.id ?? preset.slug
  activePresetId.value = id
  refining.value = true
  setStatus('Refining…', 'active')

  try {
    const refined = await presets.refine(id, transcript)
    emit('refined', refined)
    setStatus('Done.', 'success')
  } catch (err) {
    setStatus(`Refinement failed: ${err.message}`, 'error')
  } finally {
    refining.value = false
  }
}

function openEdit(preset) {
  editingPreset.value = preset
  editorVisible.value = true
}

function openCreate() {
  editingPreset.value = null
  editorVisible.value = true
}

function onSaved() {
  // fetchPresets is called inside PresetEditor on save
}
</script>

<style scoped>
.preset-chip-wrap {
  position: relative;
  display: inline-flex;
  align-items: center;
}

.preset-chip-wrap .btn-preset-edit {
  display: none;
  position: absolute;
  right: -6px;
  top: -6px;
  width: 18px;
  height: 18px;
  border-radius: 50%;
  background: var(--bg-card);
  border: 1px solid var(--border);
  color: var(--text-muted);
  font-size: 10px;
  cursor: pointer;
  align-items: center;
  justify-content: center;
  padding: 0;
  line-height: 1;
  transition: color 0.15s, border-color 0.15s, background 0.15s;
  z-index: 1;
}

.preset-chip-wrap:hover .btn-preset-edit {
  display: flex;
}

.btn-preset-edit:hover {
  color: var(--accent);
  border-color: var(--accent);
  background: var(--chip-bg);
}

.btn-new-preset {
  margin-top: 10px;
  font-size: 12px;
}
</style>
