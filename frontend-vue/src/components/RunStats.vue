<template>
  <div v-if="stats.hasAny" class="run-stats" role="status" aria-label="Last run statistics">
    <div class="run-stats-title">Last run</div>
    <dl class="run-stats-grid">
      <div class="run-stats-row">
        <dt>Audio</dt>
        <dd>{{ fmtDuration }}</dd>
      </div>
      <div class="run-stats-row">
        <dt>Size</dt>
        <dd>{{ fmtSize }}</dd>
      </div>
      <div class="run-stats-row">
        <dt>Transcript</dt>
        <dd>{{ fmtChars }}</dd>
      </div>
      <div v-if="stats.refinedChars != null" class="run-stats-row">
        <dt>Refined</dt>
        <dd>{{ fmtRefined }}</dd>
      </div>
      <div class="run-stats-row">
        <dt>Cost</dt>
        <dd>{{ fmtCost }}</dd>
      </div>
    </dl>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useStatsStore } from '../stores/stats.js'

const stats = useStatsStore()

const fmtDuration = computed(() => {
  const s = stats.audioDurationSec
  return s == null ? '—' : `${s.toFixed(1)} s`
})

const fmtSize = computed(() => {
  const b = stats.audioBytes
  if (b == null) return '—'
  return `${(b / (1024 * 1024)).toFixed(2)} MB`
})

const fmtChars = computed(() => {
  const c = stats.transcriptChars
  return c == null ? '—' : `${c.toLocaleString()} chars`
})

const fmtRefined = computed(() => {
  const c = stats.refinedChars
  return c == null ? '—' : `${c.toLocaleString()} chars`
})

const fmtCost = computed(() => {
  const eur = stats.totalCostEur
  if (eur == null) return '—'
  return `€${eur.toFixed(4)}`
})
</script>

<style scoped>
.run-stats {
  position: fixed;
  right: 16px;
  bottom: 16px;
  z-index: 90;
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: 10px;
  padding: 10px 14px;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.35);
  font-size: 12px;
  min-width: 180px;
}

.run-stats-title {
  font-size: 10px;
  font-weight: 700;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  color: var(--text-muted);
  margin-bottom: 6px;
}

.run-stats-grid {
  margin: 0;
  display: grid;
  gap: 2px;
}

.run-stats-row {
  display: flex;
  justify-content: space-between;
  gap: 12px;
}

.run-stats-row dt {
  color: var(--text-muted);
}

.run-stats-row dd {
  margin: 0;
  font-variant-numeric: tabular-nums;
  color: var(--text-strong);
  font-weight: 600;
}
</style>
