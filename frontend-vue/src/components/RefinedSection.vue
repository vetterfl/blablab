<template>
  <div v-if="text" class="refined-section">
    <div style="display:flex;align-items:baseline;justify-content:space-between;margin-bottom:6px;gap:12px">
      <div class="step-label step-label--accent" style="margin-bottom:0">03 &middot; Result</div>
    </div>
    <div class="result-box">
      <div class="result-header">
        <div style="min-width:0">
          <div class="result-title">
            <span class="result-dot"></span>
            Refined output
          </div>
          <p class="card-subtitle">Rewritten by AI. Edit, re-run, or copy.</p>
        </div>
        <div class="result-actions">
          <button
            class="btn btn-rerun"
            :disabled="rerunning"
            @click="$emit('rerun')"
            title="Re-run with same preset"
          >
            <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">
              <polyline points="1 4 1 10 7 10"/>
              <path d="M3.51 15a9 9 0 1 0 .49-4"/>
            </svg>
            {{ rerunning ? 'Running…' : 'Re-run' }}
          </button>
          <button class="btn btn-copy" @click="copyText">{{ copyLabel }}</button>
        </div>
      </div>
      <textarea
        ref="outputRef"
        :value="text"
        @input="onInput"
        class="fancy-textarea fancy-textarea--output"
        readonly
        style="min-height:200px;resize:none;overflow:hidden"
      ></textarea>
    </div>
  </div>
</template>

<script setup>
import { nextTick, onMounted, ref, watch } from 'vue'

const props = defineProps({
  text: { type: String, default: '' },
  rerunning: { type: Boolean, default: false },
})
const emit = defineEmits(['update:text', 'rerun'])

const copyLabel = ref('Copy')
const outputRef = ref(null)

function autosize() {
  const el = outputRef.value
  if (!el) return
  el.style.height = 'auto'
  el.style.height = `${el.scrollHeight}px`
}

function onInput(e) {
  emit('update:text', e.target.value)
  nextTick(autosize)
}

watch(() => props.text, () => nextTick(autosize))
onMounted(() => nextTick(autosize))

async function copyText() {
  const el = outputRef.value
  if (!el || !el.value) return
  try {
    await navigator.clipboard.writeText(el.value)
    copyLabel.value = '✓ Copied!'
    setTimeout(() => { copyLabel.value = 'Copy' }, 1500)
  } catch {
    el.select()
    document.execCommand('copy')
  }
}
</script>

<style scoped>
.result-actions {
  display: flex;
  gap: 8px;
  align-items: center;
  flex-shrink: 0;
}

.btn-rerun {
  display: flex;
  align-items: center;
  gap: 5px;
  font-size: 12px;
}
</style>
