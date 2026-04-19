import { createApp } from 'vue'
import { createPinia } from 'pinia'
import piniaPluginPersistedstate from 'pinia-plugin-persistedstate'
import App from './App.vue'
import './assets/style.css'
import { useThemeStore } from './stores/theme.js'

const pinia = createPinia()
pinia.use(piniaPluginPersistedstate)

const app = createApp(App)
app.use(pinia)

// Apply persisted theme before first render to avoid flash
useThemeStore().init()

app.mount('#app')
