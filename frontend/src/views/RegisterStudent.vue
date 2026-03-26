<template>
    <div class="auth-wrapper">
      <div class="auth-card">
        <div class="auth-logo">🎓</div>
        <h1>Register as Student</h1>
        <p class="auth-subtitle">Create your student account</p>
  
        <div v-if="error" class="alert alert-error">{{ error }}</div>
        <div v-if="success" class="alert alert-success">{{ success }}</div>
  
        <form @submit.prevent="handleRegister" class="auth-form">
          <div class="form-row">
            <div class="form-group"><label>Username *</label><input v-model="form.username" placeholder="Username" required class="form-input" /></div>
            <div class="form-group"><label>Full Name *</label><input v-model="form.full_name" placeholder="Full name" required class="form-input" /></div>
          </div>
          <div class="form-group"><label>Email *</label><input v-model="form.email" type="email" placeholder="student@college.edu" required class="form-input" /></div>
          <div class="form-group"><label>Password *</label><input v-model="form.password" type="password" placeholder="Create a password" required class="form-input" /></div>
          <div class="form-row">
            <div class="form-group"><label>Branch *</label>
              <select v-model="form.branch" required class="form-input">
                <option value="">Select branch</option>
                <option>CSE</option><option>ECE</option><option>EEE</option><option>ME</option><option>CE</option><option>IT</option><option>Other</option>
              </select>
            </div>
            <div class="form-group"><label>Year *</label>
              <select v-model="form.year" required class="form-input">
                <option value="">Year</option>
                <option value="1">1st Year</option><option value="2">2nd Year</option><option value="3">3rd Year</option><option value="4">4th Year</option>
              </select>
            </div>
          </div>
          <div class="form-row">
            <div class="form-group"><label>CGPA *</label><input v-model="form.cgpa" type="number" step="0.01" min="0" max="10" placeholder="e.g. 8.5" required class="form-input" /></div>
            <div class="form-group"><label>Phone</label><input v-model="form.phone" placeholder="Phone number" class="form-input" /></div>
          </div>
          <button type="submit" :disabled="loading" class="btn-submit">
            {{ loading ? 'Registering...' : 'Register' }}
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
  const form = ref({ username:'', email:'', password:'', full_name:'', branch:'', cgpa:'', year:'', phone:'' })
  
  async function handleRegister() {
    loading.value = true
    error.value = ''
    const result = await authStore.registerStudent({ ...form.value, cgpa: parseFloat(form.value.cgpa), year: parseInt(form.value.year) })
    if (result.success) {
      success.value = 'Registered successfully! Redirecting to login...'
      setTimeout(() => router.push('/login'), 1500)
    } else {
      error.value = result.error || 'Registration failed'
    }
    loading.value = false
  }
  </script>
  
  <style scoped>
  .auth-wrapper{min-height:100vh;display:flex;align-items:center;justify-content:center;background:linear-gradient(135deg,#1e293b,#334155);padding:20px}
  .auth-card{width:500px;background:white;padding:36px;border-radius:16px;box-shadow:0 20px 60px rgba(0,0,0,0.3);text-align:center}
  .auth-logo{font-size:44px;margin-bottom:10px}
  h1{font-size:20px;font-weight:700;color:#1e293b;margin:0 0 6px;font-family:'Inter',sans-serif}
  .auth-subtitle{font-size:14px;color:#64748b;margin:0 0 22px}
  .auth-form{text-align:left}
  .form-row{display:grid;grid-template-columns:1fr 1fr;gap:12px}
  .form-group{display:flex;flex-direction:column;gap:5px;margin-bottom:13px}
  .form-group label{font-size:13px;font-weight:600;color:#374151}
  .form-input{padding:9px 12px;border:1px solid #e2e8f0;border-radius:8px;font-size:14px;outline:none;width:100%;font-family:inherit;background:white}
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
  