<template>
    <div class="auth-wrapper">
      <div class="auth-card">
        <div class="auth-logo">🏢</div>
        <h1>Register Company</h1>
        <p class="auth-subtitle">Create your company account</p>
  
        <div v-if="error" class="alert alert-error">{{ error }}</div>
        <div v-if="success" class="alert alert-success">{{ success }}</div>
  
        <form @submit.prevent="handleRegister" class="auth-form">
          <div class="form-group"><label>Username *</label><input v-model="form.username" placeholder="Enter username" required class="form-input" /></div>
          <div class="form-group"><label>Email *</label><input v-model="form.email" type="email" placeholder="company@example.com" required class="form-input" /></div>
          <div class="form-group"><label>Password *</label><input v-model="form.password" type="password" placeholder="Create a password" required class="form-input" /></div>
          <div class="form-group"><label>Company Name *</label><input v-model="form.company_name" placeholder="Enter company name" required class="form-input" /></div>
          <div class="form-group"><label>HR Contact</label><input v-model="form.hr_contact" placeholder="HR contact name or email" class="form-input" /></div>
          <div class="form-group"><label>Website</label><input v-model="form.website" placeholder="https://yourcompany.com" class="form-input" /></div>
          <div class="form-group"><label>Description</label><textarea v-model="form.description" placeholder="Brief description of your company..." rows="3" class="form-input"></textarea></div>
          <button type="submit" :disabled="loading" class="btn-submit">
            {{ loading ? 'Registering...' : 'Register Company' }}
          </button>
        </form>
  
        <div class="auth-footer">
          Already have an account? <router-link to="/login" class="link">Login here</router-link>
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
  const loading = ref(false)
  const error = ref('')
  const success = ref('')
  const form = ref({ username:'', email:'', password:'', company_name:'', hr_contact:'', website:'', description:'' })
  
  async function handleRegister() {
    loading.value = true
    error.value = ''
    const result = await authStore.registerCompany(form.value)
    if (result.success) {
      success.value = 'Company registered! Awaiting admin approval. You can now login.'
      setTimeout(() => router.push('/login'), 2500)
    } else {
      error.value = result.error || 'Registration failed'
    }
    loading.value = false
  }
  </script>
  
  <style scoped>
  .auth-wrapper{min-height:100vh;display:flex;align-items:center;justify-content:center;background:linear-gradient(135deg,#1e293b,#334155);padding:20px}
  .auth-card{width:440px;background:white;padding:36px;border-radius:16px;box-shadow:0 20px 60px rgba(0,0,0,0.3);text-align:center}
  .auth-logo{font-size:44px;margin-bottom:10px}
  h1{font-size:20px;font-weight:700;color:#1e293b;margin:0 0 6px;font-family:'Inter',sans-serif}
  .auth-subtitle{font-size:14px;color:#64748b;margin:0 0 22px}
  .auth-form{text-align:left}
  .form-group{display:flex;flex-direction:column;gap:5px;margin-bottom:13px}
  .form-group label{font-size:13px;font-weight:600;color:#374151}
  .form-input{padding:9px 12px;border:1px solid #e2e8f0;border-radius:8px;font-size:14px;outline:none;width:100%;font-family:inherit;resize:vertical}
  .form-input:focus{border-color:#3b82f6;box-shadow:0 0 0 3px rgba(59,130,246,.1)}
  .btn-submit{width:100%;padding:11px;background:#1e293b;color:white;border:none;border-radius:8px;cursor:pointer;font-size:14px;font-weight:600;margin-top:6px}
  .btn-submit:hover{background:#334155}
  .btn-submit:disabled{background:#94a3b8;cursor:not-allowed}
  .alert{padding:10px 14px;border-radius:8px;font-size:14px;margin-bottom:14px;text-align:left}
  .alert-error{background:#fee2e2;color:#b91c1c}
  .alert-success{background:#dcfce7;color:#166534}
  .auth-footer{margin-top:18px;font-size:13px;color:#64748b;padding-top:16px;border-top:1px solid #f1f5f9}
  .link{color:#3b82f6;text-decoration:none;font-weight:500}
  </style>
  