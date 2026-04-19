import { defineStore } from 'pinia'
import { ref, watch } from 'vue'

export const useThemeStore = defineStore(
  'theme',
  () => {
    const mode = ref('dark') // 'dark' | 'light' | 'system'

    function apply(m) {
      document.documentElement.setAttribute('data-theme', m)
    }

    function setMode(m) {
      mode.value = m
      apply(m)
    }

    // Apply on init (called from main.js or first use)
    function init() {
      apply(mode.value)
    }

    watch(mode, apply)

    return { mode, setMode, init }
  },
  {
    persist: {
      key: 'blablab_theme',
      paths: ['mode'],
      afterRestore: (ctx) => {
        document.documentElement.setAttribute('data-theme', ctx.store.mode)
      },
    },
  }
)
