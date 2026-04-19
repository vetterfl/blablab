import { defineStore } from 'pinia'
import { computed, ref } from 'vue'
import { apiLogin } from '../api/client.js'

export const useAuthStore = defineStore(
  'auth',
  () => {
    const token = ref(null)
    const isAdmin = ref(false)
    const username = ref(null)

    const isLoggedIn = computed(() => !!token.value)

    async function login(u, password) {
      const data = await apiLogin(u, password)
      token.value = data.access_token
      isAdmin.value = data.is_admin ?? false
      username.value = u
    }

    function logout() {
      token.value = null
      isAdmin.value = false
      username.value = null
    }

    return { token, isAdmin, username, isLoggedIn, login, logout }
  },
  {
    persist: {
      key: 'blablab_token',
      paths: ['token', 'isAdmin', 'username'],
    },
  }
)
