<template>
  <div style="display:flex;flex-direction:column;min-height:0;flex:0 1 40%">
    <div class="step-label">02 &middot; Transcript</div>
    <section class="card transcript-section" style="flex:1;display:flex;flex-direction:column;min-height:0">
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
        style="flex:1;min-height:80px"
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
