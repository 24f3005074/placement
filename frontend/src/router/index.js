import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  { path: '/', redirect: '/login' },
  { 
    path: '/login', 
    name: 'Login',
    component: () => import('@/views/Login.vue')
  },
  { 
    path: '/register/student', 
    name: 'RegisterStudent',
    component: () => import('@/views/RegisterStudent.vue')
  },
  { 
    path: '/register/company', 
    name: 'RegisterCompany',
    component: () => import('@/views/RegisterCompany.vue')
  },
  { 
    path: '/admin', 
    name: 'AdminDashboard',
    component: () => import('@/views/AdminDashboard.vue'),
    meta: { requiresAuth: true, role: 'admin' }
  },
  { 
    path: '/company', 
    name: 'CompanyDashboard',
    component: () => import('@/views/CompanyDashboard.vue'),
    meta: { requiresAuth: true, role: 'company' }
  },
  { 
    path: '/student', 
    name: 'StudentDashboard',
    component: () => import('@/views/StudentDashboard.vue'),
    meta: { requiresAuth: true, role: 'student' }
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

router.beforeEach((to, from, next) => {
  const token = localStorage.getItem('token')
  const user = JSON.parse(localStorage.getItem('user') || '{}')
  
  if (to.meta.requiresAuth && !token) {
    next('/login')
  } else if (to.meta.role && user.role !== to.meta.role) {
    // Redirect to correct dashboard
    if (user.role === 'admin') next('/admin')
    else if (user.role === 'company') next('/company')
    else if (user.role === 'student') next('/student')
    else next('/login')
  } else {
    next()
  }
})

export default router