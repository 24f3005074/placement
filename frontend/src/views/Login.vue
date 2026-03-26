<template>
    <div class="auth-wrapper">
      <div class="auth-card">
        <div class="auth-logo">🎓</div>
        <h1>Placement Portal</h1>
        <p class="auth-subtitle">Sign in to your account</p>
  
        <div v-if="errorMsg" class="alert alert-error">{{ errorMsg }}</div>
  
        <form @submit.prevent="handleLogin" class="auth-form">
          <div class="form-group">
            <label>Email</label>
            <input v-model="email" type="email" placeholder="Enter your email" required class="form-input" />
          </div>
          <div class="form-group">
            <label>Password</label>
            <input v-model="password" type="password" placeholder="Enter your password" required class="form-input" />
          </div>
          <button type="submit" :disabled="loading" class="btn-submit">
            {{ loading ? 'Signing in...' : 'Login' }}
          </button>
        </form>
  
        <div class="auth-footer">
          <p>Don't have an account?</p>
          <div class="register-links">
            <router-link to="/register/student" class="link-btn">Register as Student</router-link>
            <router-link to="/register/company" class="link-btn">Register as Company</router-link>
          </div>
        </div>
      </div>
    </div>
  </template>
  
  <script setup>
  import { ref } from 'vue'
  import { useRouter } from 'vue-router'
  import { useAuthStore } from '@/stores/auth'
  
  const router = useRouter()
  const authStore = useAuthStore()
  
  const email = ref('')
  const password = ref('')
  const loading = ref(false)
  const errorMsg = ref('')
  
  async function handleLogin() {
    loading.value = true
    errorMsg.value = ''
    const result = await authStore.login(email.value, password.value)
    if (result.success) {
      const role = authStore.userRole
      if (role === 'admin') router.push('/admin')
      else if (role === 'company') router.push('/company')
      else if (role === 'student') router.push('/student')
      else errorMsg.value = 'Invalid user role'
    } else {
      errorMsg.value = result.error || 'Login failed'
    }
    loading.value = false
  }
  </script>
  
  <style scoped>
  .auth-wrapper {
    min-height: 100vh;
    display: flex;
    align-items: center;
    justify-content: center;
    background: linear-gradient(135deg, #1e293b 0%, #334155 100%);
  }
  .auth-card {
    width: 400px;
    background: white;
    padding: 40px;
    border-radius: 16px;
    box-shadow: 0 20px 60px rgba(0,0,0,0.3);
    text-align: center;
  }
  .auth-logo { font-size: 48px; margin-bottom: 12px; }
  h1 { font-size: 22px; font-weight: 700; color: #1e293b; margin: 0 0 6px; font-family: 'Inter',sans-serif; }
  .auth-subtitle { font-size: 14px; color: #64748b; margin: 0 0 24px; }
  .auth-form { text-align: left; }
  .form-group { display: flex; flex-direction: column; gap: 6px; margin-bottom: 16px; }
  .form-group label { font-size: 13px; font-weight: 600; color: #374151; }
  .form-input { padding: 10px 14px; border: 1px solid #e2e8f0; border-radius: 8px; font-size: 14px; outline: none; width: 100%; font-family: 'Inter',sans-serif; }
  .form-input:focus { border-color: #3b82f6; box-shadow: 0 0 0 3px rgba(59,130,246,.15); }
  .btn-submit { width: 100%; padding: 11px; background: #3b82f6; color: white; border: none; border-radius: 8px; cursor: pointer; font-size: 15px; font-weight: 600; margin-top: 8px; transition: background .2s; }
  .btn-submit:hover { background: #2563eb; }
  .btn-submit:disabled { background: #93c5fd; cursor: not-allowed; }
  .alert-error { background: #fee2e2; color: #b91c1c; padding: 10px 14px; border-radius: 8px; font-size: 14px; margin-bottom: 16px; text-align: left; }
  .auth-footer { margin-top: 24px; padding-top: 20px; border-top: 1px solid #f1f5f9; }
  .auth-footer p { font-size: 13px; color: #64748b; margin: 0 0 10px; }
  .register-links { display: flex; gap: 10px; justify-content: center; flex-wrap: wrap; }
  .link-btn { padding: 8px 14px; border: 1px solid #e2e8f0; border-radius: 8px; font-size: 13px; color: #3b82f6; text-decoration: none; font-weight: 500; transition: all .2s; }
  .link-btn:hover { background: #eff6ff; border-color: #bfdbfe; }
  </style>
  