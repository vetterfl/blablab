import { defineStore } from 'pinia'
import { computed, ref } from 'vue'
import { apiLogin } from '../api/client.js'

export const useAuthStore = defineStore(
  'auth',
  () => {
    const token = ref(null)

    const isLoggedIn = computed(() => !!token.value)

    async function login(username, password) {
      const data = await apiLogin(username, password)
      token.value = data.access_token
    }

    function logout() {
      token.value = null
    }

    return { token, isLoggedIn, login, logout }
  },
  {
    persist: {
      key: 'blablab_token',
      paths: ['token'],
    },
  }
)
