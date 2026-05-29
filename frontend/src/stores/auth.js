import { ref, computed } from 'vue'
import { defineStore } from 'pinia'
import api from '@/utils/api'

export const useAuthStore = defineStore('auth', () => {
  const user = ref(null)
  const token = ref(localStorage.getItem('token') || '')

  const isLoggedIn = computed(() => !!token.value)
  const isAdmin = computed(() => user.value?.role === 'admin')
  const isSales = computed(() => user.value?.role === 'sales')
  const isCustomer = computed(() => user.value?.role === 'customer')

  async function login(username, password) {
    const { data } = await api.post('/auth/login', { username, password })
    token.value = data.token
    user.value = data.user
    localStorage.setItem('token', data.token)
    return data
  }

  async function register(form) {
    const { data } = await api.post('/auth/register', form)
    return data
  }

  async function fetchUser() {
    if (!token.value) return
    try {
      const { data } = await api.get('/auth/me')
      user.value = data.user
    } catch {
      logout()
    }
  }

  function logout() {
    token.value = ''
    user.value = null
    localStorage.removeItem('token')
  }

  return { user, token, isLoggedIn, isAdmin, isSales, isCustomer, login, register, fetchUser, logout }
})
