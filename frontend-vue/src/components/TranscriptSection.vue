<template>
  <div>
    <div class="step-label">02 &middot; Transcript</div>
    <section class="card transcript-section">
      <div class="card-header">
        <div style="min-width:0">
          <h2 class="card-title">Transcript</h2>
          <p class="card-subtitle">Edit in place before refining.</p>
        </div>
      </div>
      <textarea
        :value="modelValue"
        @input="$emit('update:modelValue', $event.target.value)"
        class="fancy-textarea"
        placeholder="Your transcription will appear here. You can edit it before refining..."
        style="min-height:200px;resize:vertical"
      ></textarea>
    </section>
  </div>
</template>

<script setup>
defineProps({
  modelValue: {
    type: String,
    default: '',
  },
})
defineEmits(['update:modelValue'])
</script>
