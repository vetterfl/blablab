<template>
  <div>
    <div class="step-label">02 &middot; Transcript</div>
    <section class="card transcript-section">
      <div class="card-header">
        <div style="min-width:0">
          <h2 class="card-title">Transcript</h2>
          <p class="card-subtitle">Edit in place before refining. New recordings insert at the cursor.</p>
        </div>
      </div>
      <textarea
        ref="textareaRef"
        :value="modelValue"
        @input="onInput"
        @click="updateCursor"
        @keyup="updateCursor"
        @select="updateCursor"
        @blur="updateCursor"
        class="fancy-textarea"
        placeholder="Your transcription will appear here. You can edit it before refining..."
        style="min-height:200px;resize:vertical"
      ></textarea>
    </section>
  </div>
</template>

<script setup>
import { nextTick, ref } from 'vue'

const props = defineProps({
  modelValue: { type: String, default: '' },
})
const emit = defineEmits(['update:modelValue'])

const textareaRef = ref(null)
const cursorPos = ref(0)

function onInput(e) {
  cursorPos.value = e.target.selectionStart
  emit('update:modelValue', e.target.value)
}

function updateCursor() {
  if (textareaRef.value) cursorPos.value = textareaRef.value.selectionStart
}

function insertAtCursor(text) {
  const el = textareaRef.value
  const cur = props.modelValue ?? ''
  const focused = el && document.activeElement === el
  const pos = focused ? el.selectionStart : (cursorPos.value > cur.length ? cur.length : cursorPos.value)

  const before = cur.slice(0, pos)
  const after = cur.slice(pos)
  let insertText = text
  if (before.length > 0 && !/[\s\n]$/.test(before) && !/^[\s\n]/.test(insertText)) {
    insertText = ' ' + insertText
  }
  if (after.length > 0 && !/^[\s\n]/.test(after) && !/[\s\n]$/.test(insertText)) {
    insertText = insertText + ' '
  }

  const newVal = before + insertText + after
  emit('update:modelValue', newVal)

  nextTick(() => {
    if (!el) return
    const newPos = pos + insertText.length
    el.focus()
    el.setSelectionRange(newPos, newPos)
    cursorPos.value = newPos
  })
}

defineExpose({ insertAtCursor })
</script>
