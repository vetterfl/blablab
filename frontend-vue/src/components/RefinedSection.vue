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
          <button class="btn btn-copy" @click="copyText">{{ copyLabel }}</button>
        </div>
      </div>
      <textarea
        :value="text"
        @input="$emit('update:text', $event.target.value)"
        class="fancy-textarea fancy-textarea--output"
        readonly
        style="flex:1;min-height:80px"
      ></textarea>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'

defineProps({
  text: {
    type: String,
    default: '',
  },
})
defineEmits(['update:text'])

const copyLabel = ref('Copy')

async function copyText() {
  const textarea = document.querySelector('.fancy-textarea--output')
  if (!textarea || !textarea.value) return
  try {
    await navigator.clipboard.writeText(textarea.value)
    copyLabel.value = '✓ Copied!'
    setTimeout(() => {
      copyLabel.value = 'Copy'
    }, 1500)
  } catch {
    textarea.select()
    document.execCommand('copy')
  }
}
</script>
