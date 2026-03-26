import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import api from '@/services/api'

export const useAuthStore = defineStore('auth', () => {
  const user = ref(null)
  const token = ref(null)
  const isLoading = ref(false)
  const error = ref(null)

  const isAuthenticated = computed(() => !!token.value)
  const userRole = computed(() => user.value?.role || null)
  const userName = computed(() => {
    if (user.value?.role === 'student') return user.value.username
    if (user.value?.role === 'company') return user.value.username
    return user.value?.username || 'User'
  })

  async function login(email, password) {
    isLoading.value = true
    error.value = null
    
    try {
      const response = await api.post('/auth/login', { email, password })
      
      if (response.data.success) {
        token.value = response.data.data.access_token
        user.value = response.data.data.user
        
        localStorage.setItem('token', token.value)
        localStorage.setItem('user', JSON.stringify(user.value))
        
        return { success: true }
      }
    } catch (err) {
      error.value = err.response?.data?.error || 'Login failed'
      return { success: false, error: error.value }
    } finally {
      isLoading.value = false
    }
  }

  async function registerStudent(data) {
    isLoading.value = true
    error.value = null
    
    try {
      await api.post('/auth/register/student', data)
      return { success: true }
    } catch (err) {
      error.value = err.response?.data?.error || 'Registration failed'
      return { success: false, error: error.value }
    } finally {
      isLoading.value = false
    }
  }

  async function registerCompany(data) {
    isLoading.value = true
    error.value = null
    
    try {
      await api.post('/auth/register/company', data)
      return { success: true }
    } catch (err) {
      error.value = err.response?.data?.error || 'Registration failed'
      return { success: false, error: error.value }
    } finally {
      isLoading.value = false
    }
  }

  function logout() {
    token.value = null
    user.value = null
    localStorage.removeItem('token')
    localStorage.removeItem('user')
  }

  function initializeAuth() {
    const savedToken = localStorage.getItem('token')
    const savedUser = localStorage.getItem('user')
    
    if (savedToken && savedUser) {
      token.value = savedToken
      user.value = JSON.parse(savedUser)
    }
  }

  return {
    user,
    token,
    isLoading,
    error,
    isAuthenticated,
    userRole,
    userName,
    login,
    registerStudent,
    registerCompany,
    logout,
    initializeAuth
  }
})