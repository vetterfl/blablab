<template>
  <LoginOverlay v-if="!auth.isLoggedIn" />

  <template v-else>
    <AppHeader :show-settings="showSettings" @toggle-settings="showSettings = !showSettings" />

    <SettingsPage v-if="showSettings" />

    <template v-else>
      <div class="layout-body">
        <!-- Left column -->
        <div class="col-left">
          <RecordSection @transcribed="onTranscribed" />
          <TranscriptSection v-model="transcript" />
          <RefinedSection :text="refined" />
        </div>

        <!-- Right column -->
        <RefinePanel
          :transcript="transcript"
          :has-transcript="transcript.trim().length > 0"
          @refined="onRefined"
        />
      </div>

      <footer class="app-footer">
        <p>BlabLab &mdash; powered by Whisper &amp; OpenRouter</p>
      </footer>
    </template>
  </template>
</template>

<script setup>
import { ref } from 'vue'
import { useAuthStore } from './stores/auth.js'
import AppHeader from './components/AppHeader.vue'
import LoginOverlay from './components/LoginOverlay.vue'
import RecordSection from './components/RecordSection.vue'
import TranscriptSection from './components/TranscriptSection.vue'
import RefinedSection from './components/RefinedSection.vue'
import RefinePanel from './components/RefinePanel.vue'
import SettingsPage from './components/SettingsPage.vue'

const auth = useAuthStore()
const transcript = ref('')
const refined = ref('')
const showSettings = ref(false)

function onTranscribed(text) {
  transcript.value = text
  refined.value = ''
}

function onRefined(text) {
  refined.value = text
}
</script>
