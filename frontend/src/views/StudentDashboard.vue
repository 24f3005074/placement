<template>
    <div class="layout">
      <!-- SIDEBAR -->
      <aside class="sidebar">
        <div class="sidebar-header">
          <div class="sidebar-logo">🎓</div>
          <h2>{{ profile.full_name || 'Student' }}</h2>
          <span class="dept-badge">{{ profile.branch || '...' }}</span>
        </div>
        <ul>
          <li :class="{active: view==='dashboard'}" @click="navigate('dashboard')">
            <span class="icon">📊</span> Dashboard
          </li>
          <li :class="{active: view.startsWith('org')}" @click="navigate('orgs')">
            <span class="icon">🏢</span> Organizations
          </li>
          <li :class="{active: view.startsWith('drive')}" @click="navigate('drives')">
            <span class="icon">📋</span> Available Drives
          </li>
          <li :class="{active: view==='applications'}" @click="navigate('applications')">
            <span class="icon">📝</span> Applied Drives
          </li>
          <li :class="{active: view==='history'}" @click="navigate('history')">
            <span class="icon">🕐</span> History
          </li>
          <li :class="{active: view==='profile'}" @click="navigate('profile')">
            <span class="icon">👤</span> Profile
          </li>
          <li class="logout" @click="logout"><span class="icon">🚪</span> Logout</li>
        </ul>
      </aside>
  
      <!-- MAIN CONTENT -->
      <main class="content">
  
        <!-- ==================== DASHBOARD ==================== -->
        <div v-if="view === 'dashboard'">
          <div class="page-header">
            <h1>Welcome, {{ profile.full_name || '...' }}</h1>
            <div class="header-btns">
              <button class="btn-outline btn-sm" @click="navigate('history')">History</button>
              <button class="btn-outline btn-sm" @click="navigate('profile')">Edit Profile</button>
              <button class="btn-outline btn-sm red-btn" @click="logout">Logout</button>
            </div>
          </div>
          <div class="stats-row">
            <div class="stat-box blue">
              <div class="stat-num">{{ applications.length }}</div>
              <div class="stat-lbl">Applications</div>
            </div>
            <div class="stat-box green">
              <div class="stat-num">{{ applications.filter(a=>a.status==='Selected').length }}</div>
              <div class="stat-lbl">Selected</div>
            </div>
            <div class="stat-box purple">
              <div class="stat-num">{{ applications.filter(a=>a.status==='Shortlisted').length }}</div>
              <div class="stat-lbl">Shortlisted</div>
            </div>
            <div class="stat-box orange">
              <div class="stat-num">{{ organizations.length }}</div>
              <div class="stat-lbl">Companies</div>
            </div>
          </div>
  
          <!-- Applied Drives table on dashboard -->
          <div class="card" v-if="applications.length">
            <div class="card-header">
              <h3>Applied Drives</h3>
            </div>
            <table>
              <thead><tr><th>Sr No.</th><th>Drive Name</th><th>Company</th><th>Date</th><th>Action</th></tr></thead>
              <tbody>
                <tr v-for="(app, idx) in applications" :key="app.id">
                  <td>{{ idx+1 }}</td>
                  <td>{{ app.drive && app.drive.job_title }}</td>
                  <td>{{ app.drive && app.drive.company_name }}</td>
                  <td>{{ fmtDate(app.applied_on) }}</td>
                  <td>
                    <button class="btn-sm btn-blue" @click="viewAppDriveDetail(app)">View Details</button>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
          <div class="empty-card" v-else>
            <p>No applications yet. <button class="link-btn" @click="navigate('drives')">Browse drives →</button></p>
          </div>
        </div>
  
        <!-- ==================== ORGANIZATIONS LIST ==================== -->
        <div v-if="view === 'orgs'">
          <div class="page-header"><h1>Organizations</h1></div>
          <div v-if="loading" class="loading-box"><div class="spinner"></div> Loading...</div>
          <div v-else-if="organizations.length === 0" class="empty-card"><p>No approved companies available.</p></div>
          <div v-else class="card">
            <table>
              <thead><tr><th>Company</th><th>Website</th><th>Action</th></tr></thead>
              <tbody>
                <tr v-for="org in organizations" :key="org.id">
                  <td><strong>{{ org.company_name }}</strong></td>
                  <td>
                    <a v-if="org.website" :href="org.website" target="_blank" class="text-link">{{ org.website }}</a>
                    <span v-else class="muted">—</span>
                  </td>
                  <td>
                    <button class="btn-sm btn-blue" @click="viewOrgDetail(org)">View Details</button>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
  
        <!-- ==================== ORG DETAIL ==================== -->
        <div v-if="view === 'org-detail'">
          <div class="page-header">
            <h1>{{ currentOrg.company_name }}</h1>
            <button class="btn-back" @click="navigate('orgs')">← Back</button>
          </div>
          <div class="two-col">
            <div class="card">
              <h3>Overview</h3>
              <p class="overview-text">{{ currentOrg.description || 'No description provided.' }}</p>
              <div v-if="currentOrg.hr_contact" class="detail-row"><label>HR Contact</label><span>{{ currentOrg.hr_contact }}</span></div>
              <div v-if="currentOrg.website" class="detail-row"><label>Website</label><a :href="currentOrg.website" target="_blank" class="text-link">{{ currentOrg.website }}</a></div>
            </div>
            <div class="card">
              <h3>Current Drives</h3>
              <div v-if="orgDrives.length === 0" class="muted">No active drives.</div>
              <div v-for="drive in orgDrives" :key="drive.id" class="drive-row" @click="viewOrgDriveDetail(drive)">
                <div class="drive-row-title">{{ drive.job_title }}</div>
                <div class="drive-row-meta">Deadline: {{ drive.application_deadline }} | Min CGPA: {{ drive.min_cgpa }}</div>
                <button class="btn-sm btn-blue">View Details</button>
              </div>
            </div>
          </div>
        </div>
  
        <!-- ==================== ORG DRIVE DETAIL ==================== -->
        <div v-if="view === 'org-drive-detail'">
          <div class="page-header">
            <h1>{{ currentDrive.job_title }}</h1>
            <button class="btn-back" @click="view='org-detail'">← Back</button>
          </div>
          <div class="drive-detail-layout">
            <div class="drive-detail-info card">
              <div class="detail-row"><label>Job Title</label><span>{{ currentDrive.job_title }}</span></div>
              <div class="detail-row"><label>Company</label><span>{{ currentDrive.company_name }}</span></div>
              <div class="detail-row"><label>Job Description</label><p class="desc-text">{{ currentDrive.job_description }}</p></div>
              <div class="detail-row"><label>Salary</label><span>{{ currentDrive.salary || 'Not disclosed' }}</span></div>
              <div class="detail-row"><label>Location</label><span>{{ currentDrive.location || 'Not specified' }}</span></div>
              <div class="detail-row"><label>Min CGPA</label><span>{{ currentDrive.min_cgpa }}</span></div>
              <div class="detail-row"><label>Deadline</label><span>{{ currentDrive.application_deadline }}</span></div>
            </div>
            <div class="drive-logo-box card">
              <div class="company-logo">COMPANY<br>NAME</div>
            </div>
          </div>
          <div class="action-bar">
            <button
              v-if="!isApplied(currentDrive.id)"
              class="btn-primary"
              @click="applyToDrive(currentDrive.id)"
              :disabled="applying">
              {{ applying ? 'Applying...' : 'Apply' }}
            </button>
            <span v-else class="status-chip chip-applied">✓ Already Applied</span>
            <button class="btn-back" @click="view='org-detail'">Go Back</button>
          </div>
        </div>
  
        <!-- ==================== AVAILABLE DRIVES LIST ==================== -->
        <div v-if="view === 'drives'">
          <div class="page-header"><h1>Available Drives</h1></div>
          <div class="toolbar">
            <input v-model="driveSearch" placeholder="Search job title..." class="search-inp" @keyup.enter="fetchDrives" />
            <button class="btn-primary btn-sm" @click="fetchDrives">Search</button>
          </div>
          <div v-if="loading" class="loading-box"><div class="spinner"></div> Loading...</div>
          <div v-else-if="drives.length === 0" class="empty-card"><p>No drives available right now.</p></div>
          <div v-else class="card">
            <table>
              <thead>
                <tr><th>Job Title</th><th>Company</th><th>Min CGPA</th><th>Deadline</th><th>Eligible</th><th>Action</th></tr>
              </thead>
              <tbody>
                <tr v-for="drive in drives" :key="drive.id">
                  <td><strong>{{ drive.job_title }}</strong></td>
                  <td>{{ drive.company_name }}</td>
                  <td>{{ drive.min_cgpa }}</td>
                  <td>{{ drive.application_deadline }}</td>
                  <td>
                    <span :class="drive.eligible ? 'status-chip chip-yes' : 'status-chip chip-no'">
                      {{ drive.eligible ? 'Yes' : 'No' }}
                    </span>
                  </td>
                  <td>
                    <button class="btn-sm btn-blue" @click="viewDriveDetail(drive)">View</button>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
  
        <!-- ==================== DRIVE DETAIL ==================== -->
        <div v-if="view === 'drive-detail'">
          <div class="page-header">
            <h1>{{ currentDrive.job_title }}</h1>
            <button class="btn-back" @click="navigate('drives')">← Back</button>
          </div>
          <div class="drive-detail-layout">
            <div class="drive-detail-info card">
              <div class="detail-row"><label>Company</label><span>{{ currentDrive.company_name }}</span></div>
              <div class="detail-row"><label>Job Description</label><p class="desc-text">{{ currentDrive.job_description }}</p></div>
              <div class="detail-row"><label>Min CGPA</label><span>{{ currentDrive.min_cgpa }}</span></div>
              <div class="detail-row"><label>Allowed Branches</label><span>{{ currentDrive.allowed_branches || 'All' }}</span></div>
              <div class="detail-row"><label>Deadline</label><span>{{ currentDrive.application_deadline }}</span></div>
              <div class="detail-row"><label>Eligibility</label>
                <span :class="currentDrive.eligible ? 'status-chip chip-yes' : 'status-chip chip-no'">
                  {{ currentDrive.eligibility_message || (currentDrive.eligible ? 'Eligible' : 'Not Eligible') }}
                </span>
              </div>
            </div>
            <div class="drive-logo-box card">
              <div class="company-logo">COMPANY<br>NAME</div>
            </div>
          </div>
          <div class="action-bar">
            <button
              v-if="currentDrive.eligible && !isApplied(currentDrive.id)"
              class="btn-primary"
              @click="applyToDrive(currentDrive.id)"
              :disabled="applying">
              {{ applying ? 'Applying...' : 'Apply' }}
            </button>
            <span v-else-if="isApplied(currentDrive.id)" class="status-chip chip-applied">✓ Already Applied</span>
            <span v-else class="status-chip chip-no">Not Eligible</span>
            <button class="btn-back" @click="navigate('drives')">Go Back</button>
          </div>
        </div>
  
        <!-- ==================== APPLIED DRIVES ==================== -->
        <div v-if="view === 'applications'">
          <div class="page-header"><h1>Applied Drives</h1></div>
          <div v-if="applications.length === 0" class="empty-card">
            <p>No applications yet.</p>
          </div>
          <div v-else class="card">
            <table>
              <thead><tr><th>Sr No.</th><th>Drive Name</th><th>Company</th><th>Date</th><th>Action</th></tr></thead>
              <tbody>
                <tr v-for="(app, idx) in applications" :key="app.id">
                  <td>{{ idx+1 }}</td>
                  <td>{{ app.drive && app.drive.job_title }}</td>
                  <td>{{ app.drive && app.drive.company_name }}</td>
                  <td>{{ fmtDate(app.applied_on) }}</td>
                  <td><button class="btn-sm btn-blue" @click="viewAppDriveDetail(app)">View Details</button></td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
  
        <!-- ==================== APP DRIVE DETAIL ==================== -->
        <div v-if="view === 'app-detail'">
          <div class="page-header">
            <h1>Application Details</h1>
            <button class="btn-back" @click="view='applications'">← Back</button>
          </div>
          <div class="card" v-if="currentApp">
            <div class="detail-row"><label>Drive</label><span>{{ currentApp.drive && currentApp.drive.job_title }}</span></div>
            <div class="detail-row"><label>Company</label><span>{{ currentApp.drive && currentApp.drive.company_name }}</span></div>
            <div class="detail-row"><label>Applied On</label><span>{{ fmtDate(currentApp.applied_on) }}</span></div>
            <div class="detail-row"><label>Status</label>
              <span :class="'status-chip chip-' + (currentApp.status || '').toLowerCase()">{{ currentApp.status }}</span>
            </div>
            <div class="detail-row" v-if="currentApp.notes"><label>Notes</label><span>{{ currentApp.notes }}</span></div>
          </div>
        </div>
  
        <!-- ==================== HISTORY ==================== -->
        <div v-if="view === 'history'">
          <div class="page-header">
            <h1>Application History</h1>
            <button class="btn-back" @click="navigate('dashboard')">← Back</button>
          </div>
          <div class="card history-header-card">
            <p><strong>Student Name:</strong> {{ profile.full_name }}</p>
            <p><strong>Department:</strong> {{ profile.branch }}</p>
          </div>
          <div v-if="history.length === 0" class="empty-card"><p>No history yet.</p></div>
          <div v-else class="card">
            <table>
              <thead><tr><th>Drive No.</th><th>Interview</th><th>Job Title</th><th>Results</th><th>Remark</th></tr></thead>
              <tbody>
                <tr v-for="(h, idx) in history" :key="h.application_id">
                  <td>{{ idx+1 }}</td>
                  <td>In-person</td>
                  <td>{{ h.job_title }}</td>
                  <td><span :class="'status-chip chip-' + h.status.toLowerCase()">{{ h.status }}</span></td>
                  <td>{{ h.notes || 'None' }}</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
  
        <!-- ==================== PROFILE ==================== -->
        <div v-if="view === 'profile'">
          <div class="page-header">
            <h1>My Profile</h1>
            <div class="header-btns">
              <button class="btn-outline btn-sm" @click="navigate('history')">History</button>
              <button class="btn-outline btn-sm red-btn" @click="logout">Logout</button>
            </div>
          </div>
          <div class="two-col">
            <div class="card">
              <h3>Personal Information</h3>
              <div class="form-group"><label>Full Name</label><input v-model="profile.full_name" class="form-inp" /></div>
              <div class="form-row-2">
                <div class="form-group"><label>Branch</label><input v-model="profile.branch" class="form-inp" /></div>
                <div class="form-group"><label>Year</label><input v-model="profile.year" type="number" class="form-inp" /></div>
              </div>
              <div class="form-row-2">
                <div class="form-group"><label>CGPA</label><input v-model="profile.cgpa" type="number" step="0.01" class="form-inp" /></div>
                <div class="form-group"><label>Phone</label><input v-model="profile.phone" class="form-inp" /></div>
              </div>
              <button class="btn-primary" @click="updateProfile">Update Profile</button>
            </div>
            <div class="card">
              <h3>Resume</h3>
              <div class="resume-box">
                <div class="resume-icon">📄</div>
                <p v-if="profile.resume_path" class="resume-status">Resume uploaded ✓</p>
                <p v-else class="muted">No resume uploaded yet</p>
              </div>
              <div class="form-group" style="margin-top:12px">
                <label>Upload Resume (PDF / DOCX)</label>
                <input type="file" ref="fileRef" accept=".pdf,.docx,.doc" @change="onFile" class="file-inp" />
                <div v-if="selectedFile" class="selected-file-name">📎 {{ selectedFile.name }}</div>
              </div>
              <div class="resume-btns">
                <button class="btn-primary" @click="uploadResume" :disabled="!selectedFile || uploading">
                  {{ uploading ? 'Uploading...' : '⬆ Upload' }}
                </button>
                <button class="btn-outline" @click="downloadResume" v-if="profile.resume_path">
                  ⬇ Download
                </button>
              </div>
            </div>
          </div>
        </div>
  
      </main>
  
      <!-- TOAST -->
      <transition name="toast-fade">
        <div v-if="toast" :class="['toast', 'toast-' + toastType]">{{ toast }}</div>
      </transition>
    </div>
  </template>
  
  <script>
  import api from '@/services/api'
  
  export default {
    name: 'StudentDashboard',
    data() {
      return {
        // STATE MACHINE: single view string controls what's shown
        view: 'dashboard',
  
        // Data
        profile: {},
        drives: [],
        applications: [],
        organizations: [],
        history: [],
  
        // Current selected items
        currentOrg: null,
        orgDrives: [],
        currentDrive: null,
        currentApp: null,
  
        // UI state
        driveSearch: '',
        loading: false,
        applying: false,
        uploading: false,
        selectedFile: null,
  
        // Toast
        toast: '',
        toastType: 'success'
      }
    },
  
    mounted() {
      this.init()
    },
  
    methods: {
      async init() {
        // Load all initial data - each independently so one failure doesn't block others
        this.fetchProfile()
        this.fetchApplications()
        this.fetchOrganizations()
        this.fetchDrives()
      },
  
      // ─── NAVIGATION ──────────────────────────────────────────────────
      navigate(target) {
        this.view = target
        if (target === 'orgs') this.fetchOrganizations()
        else if (target === 'drives') this.fetchDrives()
        else if (target === 'applications') this.fetchApplications()
        else if (target === 'history') this.fetchHistory()
      },
  
      // ─── TOAST ───────────────────────────────────────────────────────
      showToast(msg, type = 'success') {
        this.toast = msg
        this.toastType = type
        setTimeout(() => { this.toast = '' }, 3500)
      },
  
      // ─── DATE FORMAT ─────────────────────────────────────────────────
      fmtDate(dt) {
        if (!dt) return '—'
        try { return new Date(dt).toLocaleDateString('en-IN') } catch { return dt }
      },
  
      // ─── PROFILE ─────────────────────────────────────────────────────
      async fetchProfile() {
        try {
          const res = await api.get('/student/profile')
          this.profile = res.data.data || {}
        } catch (e) {
          console.error('fetchProfile:', e)
        }
      },
  
      async updateProfile() {
        try {
          await api.put('/student/profile', {
            full_name: this.profile.full_name,
            branch: this.profile.branch,
            year: Number(this.profile.year),
            cgpa: Number(this.profile.cgpa),
            phone: this.profile.phone
          })
          this.showToast('Profile updated!')
        } catch (e) {
          this.showToast('Failed to update profile', 'error')
        }
      },
  
      // ─── DRIVES ──────────────────────────────────────────────────────
      async fetchDrives() {
        this.loading = true
        try {
          const res = await api.get('/student/drives', { params: { search: this.driveSearch } })
          this.drives = res.data.data || []
        } catch (e) {
          console.error('fetchDrives:', e)
          this.showToast('Failed to load drives', 'error')
        } finally {
          this.loading = false
        }
      },
  
      viewDriveDetail(drive) {
        this.currentDrive = drive
        this.view = 'drive-detail'
      },
  
      // ─── APPLY ───────────────────────────────────────────────────────
      isApplied(driveId) {
        // Compare as numbers to avoid type mismatch
        const id = Number(driveId)
        return this.applications.some(a => {
          const dId = a.drive ? Number(a.drive.id) : null
          return dId === id
        })
      },
  
      async applyToDrive(driveId) {
        if (this.applying) return
        this.applying = true
        try {
          await api.post(`/student/apply/${driveId}`)
          this.showToast('Applied successfully! 🎉')
          await this.fetchApplications()  // Refresh so isApplied() updates
          // Update current drive state
          if (this.currentDrive && Number(this.currentDrive.id) === Number(driveId)) {
            this.currentDrive = { ...this.currentDrive, already_applied: true }
          }
        } catch (e) {
          const msg = e.response?.data?.error || 'Application failed'
          this.showToast(msg, 'error')
        } finally {
          this.applying = false
        }
      },
  
      // ─── APPLICATIONS ─────────────────────────────────────────────────
      async fetchApplications() {
        try {
          const res = await api.get('/student/applications')
          this.applications = res.data.data || []
        } catch (e) {
          console.error('fetchApplications:', e)
        }
      },
  
      viewAppDriveDetail(app) {
        this.currentApp = app
        this.view = 'app-detail'
      },
  
      // ─── ORGANIZATIONS ────────────────────────────────────────────────
      async fetchOrganizations() {
        this.loading = true
        try {
          const res = await api.get('/student/companies')
          this.organizations = res.data.data || []
        } catch (e) {
          console.error('fetchOrganizations:', e)
          this.showToast('Failed to load organizations', 'error')
        } finally {
          this.loading = false
        }
      },
  
      async viewOrgDetail(org) {
        this.currentOrg = org
        this.orgDrives = []
        this.view = 'org-detail'
        // Fetch drives for this org
        try {
          const res = await api.get(`/student/companies/${org.id}`)
          this.orgDrives = (res.data.data && res.data.data.drives) || []
        } catch (e) {
          console.error('viewOrgDetail:', e)
          this.orgDrives = []
        }
      },
  
      viewOrgDriveDetail(drive) {
        this.currentDrive = drive
        this.view = 'org-drive-detail'
      },
  
      // ─── HISTORY ─────────────────────────────────────────────────────
      async fetchHistory() {
        try {
          const res = await api.get('/student/history')
          this.history = res.data.data || []
        } catch (e) {
          this.showToast('Failed to load history', 'error')
        }
      },
  
      // ─── RESUME ──────────────────────────────────────────────────────
      onFile(e) {
        this.selectedFile = e.target.files[0] || null
      },
  
      async uploadResume() {
        if (!this.selectedFile || this.uploading) return
        this.uploading = true
        try {
          const formData = new FormData()
          formData.append('resume', this.selectedFile)
          const token = localStorage.getItem('token')
          const res = await fetch('/api/student/resume/upload', {
            method: 'POST',
            headers: { Authorization: `Bearer ${token}` },
            body: formData
          })
          const data = await res.json()
          if (!res.ok) throw new Error(data.error || 'Upload failed')
          this.showToast('Resume uploaded!')
          this.selectedFile = null
          if (this.$refs.fileRef) this.$refs.fileRef.value = ''
          await this.fetchProfile()
        } catch (e) {
          this.showToast(e.message || 'Upload failed', 'error')
        } finally {
          this.uploading = false
        }
      },
  
      async downloadResume() {
        try {
          const token = localStorage.getItem('token')
          const res = await fetch('/api/student/resume/download', {
            headers: { Authorization: `Bearer ${token}` }
          })
          if (!res.ok) throw new Error('Not found')
          const blob = await res.blob()
          const url = URL.createObjectURL(blob)
          const a = document.createElement('a')
          a.href = url
          a.download = 'my_resume'
          document.body.appendChild(a)
          a.click()
          document.body.removeChild(a)
          URL.revokeObjectURL(url)
        } catch (e) {
          this.showToast('No resume found', 'error')
        }
      },
  
      logout() {
        localStorage.removeItem('token')
        localStorage.removeItem('user')
        window.location.href = '/login'
      }
    }
  }
  </script>
  
  <style scoped>
  * { box-sizing: border-box; }
  
  .layout {
    display: flex;
    height: 100vh;
    font-family: 'Inter', 'Segoe UI', sans-serif;
    background: #f1f5f9;
    overflow: hidden;
  }
  
  /* ── SIDEBAR ── */
  .sidebar {
    width: 230px;
    background: linear-gradient(180deg, #1e293b 0%, #0f172a 100%);
    color: white;
    display: flex;
    flex-direction: column;
    flex-shrink: 0;
    overflow-y: auto;
  }
  
  .sidebar-header {
    padding: 22px 16px 18px;
    border-bottom: 1px solid rgba(255,255,255,0.08);
    text-align: center;
  }
  .sidebar-logo { font-size: 30px; margin-bottom: 6px; }
  .sidebar-header h2 { font-size: 13px; font-weight: 600; color: #e2e8f0; margin: 0 0 6px; word-break: break-word; line-height: 1.4; }
  .dept-badge { background: rgba(99,102,241,0.3); color: #a5b4fc; padding: 2px 10px; border-radius: 20px; font-size: 11px; font-weight: 600; }
  
  .sidebar ul { list-style: none; padding: 14px 10px; margin: 0; flex: 1; }
  .sidebar li {
    padding: 10px 12px;
    cursor: pointer;
    border-radius: 8px;
    margin-bottom: 3px;
    font-size: 13px;
    font-weight: 500;
    color: #94a3b8;
    transition: all 0.18s;
    display: flex;
    align-items: center;
    gap: 9px;
    user-select: none;
  }
  .sidebar li:hover { background: rgba(255,255,255,0.07); color: #e2e8f0; }
  .sidebar li.active { background: #3b82f6; color: white; }
  .sidebar li.logout { color: #f87171; margin-top: 8px; }
  .sidebar li.logout:hover { background: rgba(248,113,113,0.12); }
  .icon { font-size: 15px; }
  
  /* ── CONTENT ── */
  .content { flex: 1; padding: 26px 30px; overflow-y: auto; }
  
  .page-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 22px;
  }
  .page-header h1 { font-size: 20px; font-weight: 700; color: #1e293b; margin: 0; }
  .header-btns { display: flex; gap: 8px; }
  
  /* ── STAT BOXES ── */
  .stats-row { display: flex; gap: 14px; margin-bottom: 22px; flex-wrap: wrap; }
  .stat-box {
    flex: 1; min-width: 120px;
    background: white;
    border-radius: 12px;
    padding: 16px;
    box-shadow: 0 1px 4px rgba(0,0,0,0.06);
    border-left: 4px solid transparent;
    display: flex; flex-direction: column;
  }
  .stat-box.blue { border-left-color: #3b82f6; }
  .stat-box.green { border-left-color: #22c55e; }
  .stat-box.purple { border-left-color: #a855f7; }
  .stat-box.orange { border-left-color: #f97316; }
  .stat-num { font-size: 28px; font-weight: 700; color: #1e293b; line-height: 1; }
  .stat-lbl { font-size: 12px; color: #64748b; margin-top: 4px; }
  
  /* ── CARDS ── */
  .card {
    background: white;
    border-radius: 12px;
    padding: 20px;
    box-shadow: 0 1px 4px rgba(0,0,0,0.06);
    margin-bottom: 18px;
  }
  .card h3 { font-size: 15px; font-weight: 600; color: #1e293b; margin: 0 0 14px; }
  .card-header { margin-bottom: 14px; }
  .card-header h3 { margin: 0; }
  
  .empty-card {
    background: white;
    border-radius: 12px;
    padding: 40px;
    text-align: center;
    color: #94a3b8;
    box-shadow: 0 1px 4px rgba(0,0,0,0.06);
  }
  
  .history-header-card { margin-bottom: 14px; }
  .history-header-card p { margin: 4px 0; font-size: 14px; color: #374151; }
  
  /* ── TABLE ── */
  table { width: 100%; border-collapse: collapse; }
  thead tr { background: #f8fafc; }
  th {
    padding: 10px 13px;
    text-align: left;
    font-size: 11px;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.04em;
    color: #64748b;
  }
  td {
    padding: 11px 13px;
    font-size: 13px;
    color: #374151;
    border-bottom: 1px solid #f1f5f9;
  }
  tbody tr:last-child td { border-bottom: none; }
  tbody tr:hover { background: #f8fafc; }
  
  /* ── STATUS CHIPS ── */
  .status-chip {
    padding: 3px 10px;
    border-radius: 20px;
    font-size: 12px;
    font-weight: 600;
    display: inline-block;
  }
  .chip-yes, .chip-approved { background: #dcfce7; color: #16a34a; }
  .chip-no, .chip-rejected { background: #fee2e2; color: #dc2626; }
  .chip-applied, .chip-pending { background: #dbeafe; color: #1d4ed8; }
  .chip-shortlisted { background: #ede9fe; color: #6d28d9; }
  .chip-selected { background: #dcfce7; color: #16a34a; }
  .chip-waiting { background: #fef3c7; color: #d97706; }
  
  /* ── BUTTONS ── */
  .btn-primary {
    background: #3b82f6; color: white; border: none;
    padding: 9px 18px; border-radius: 8px;
    cursor: pointer; font-size: 14px; font-weight: 600;
    transition: background 0.18s;
  }
  .btn-primary:hover { background: #2563eb; }
  .btn-primary:disabled { background: #93c5fd; cursor: not-allowed; }
  
  .btn-outline {
    background: white; color: #374151;
    border: 1px solid #e2e8f0;
    padding: 7px 14px; border-radius: 7px;
    cursor: pointer; font-size: 13px; font-weight: 500;
  }
  .btn-outline:hover { background: #f8fafc; }
  .red-btn { color: #dc2626; border-color: #fecaca; }
  .red-btn:hover { background: #fff1f2; }
  
  .btn-back {
    background: white; color: #374151;
    border: 1px solid #e2e8f0;
    padding: 7px 14px; border-radius: 7px;
    cursor: pointer; font-size: 13px; font-weight: 500;
  }
  .btn-back:hover { background: #f8fafc; }
  
  .btn-sm { padding: 5px 12px; font-size: 12px; border-radius: 6px; cursor: pointer; font-weight: 500; white-space: nowrap; border: none; }
  .btn-blue { background: #eff6ff; color: #1d4ed8; border: 1px solid #bfdbfe; }
  .btn-blue:hover { background: #dbeafe; }
  
  .link-btn { background: none; border: none; color: #3b82f6; cursor: pointer; font-size: 14px; padding: 0; text-decoration: underline; }
  
  /* ── TOOLBAR ── */
  .toolbar { display: flex; gap: 10px; margin-bottom: 16px; align-items: center; }
  .search-inp {
    padding: 8px 12px; border: 1px solid #e2e8f0; border-radius: 8px;
    font-size: 14px; outline: none; background: white; min-width: 220px;
  }
  .search-inp:focus { border-color: #3b82f6; box-shadow: 0 0 0 3px rgba(59,130,246,0.1); }
  
  /* ── TWO COLUMN ── */
  .two-col { display: grid; grid-template-columns: 1fr 1fr; gap: 18px; }
  
  /* ── ORG DETAIL ── */
  .overview-text { font-size: 14px; color: #374151; line-height: 1.6; margin: 0 0 14px; }
  .detail-row { display: flex; flex-direction: column; gap: 3px; margin-bottom: 12px; }
  .detail-row label { font-size: 11px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.05em; color: #94a3b8; }
  .detail-row span, .detail-row p { font-size: 14px; color: #374151; margin: 0; line-height: 1.5; }
  .desc-text { font-size: 14px; color: #374151; line-height: 1.6; margin: 0; white-space: pre-wrap; }
  .text-link { color: #3b82f6; font-size: 14px; text-decoration: none; }
  .text-link:hover { text-decoration: underline; }
  
  .drive-row {
    display: flex; align-items: center; justify-content: space-between;
    padding: 12px 14px; border: 1px solid #e2e8f0; border-radius: 8px;
    margin-bottom: 10px; cursor: pointer; transition: background 0.15s;
  }
  .drive-row:hover { background: #f8fafc; }
  .drive-row-title { font-weight: 600; font-size: 14px; color: #1e293b; flex: 1; }
  .drive-row-meta { font-size: 12px; color: #64748b; flex: 1; }
  
  /* ── DRIVE DETAIL LAYOUT ── */
  .drive-detail-layout { display: grid; grid-template-columns: 1fr 160px; gap: 18px; margin-bottom: 18px; }
  .drive-detail-info { }
  .drive-logo-box { display: flex; align-items: center; justify-content: center; }
  .company-logo {
    width: 110px; height: 80px;
    background: linear-gradient(135deg, #e0e7ff, #c7d2fe);
    border-radius: 10px;
    display: flex; align-items: center; justify-content: center;
    font-size: 11px; font-weight: 700; color: #4338ca;
    text-align: center; border: 1px solid #a5b4fc;
  }
  .action-bar { display: flex; align-items: center; gap: 12px; padding: 14px 0; }
  
  /* ── FORMS ── */
  .form-group { display: flex; flex-direction: column; gap: 5px; margin-bottom: 13px; }
  .form-group label { font-size: 12px; font-weight: 600; color: #374151; }
  .form-inp {
    padding: 8px 11px; border: 1px solid #e2e8f0; border-radius: 7px;
    font-size: 14px; outline: none; width: 100%; font-family: inherit;
  }
  .form-inp:focus { border-color: #3b82f6; box-shadow: 0 0 0 3px rgba(59,130,246,0.1); }
  .form-row-2 { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; }
  
  /* ── RESUME ── */
  .resume-box {
    background: #f8fafc; border: 2px dashed #e2e8f0; border-radius: 10px;
    padding: 22px; text-align: center;
  }
  .resume-icon { font-size: 32px; margin-bottom: 6px; }
  .resume-status { font-size: 14px; color: #16a34a; font-weight: 600; margin: 0; }
  .file-inp { font-size: 13px; width: 100%; margin-top: 4px; }
  .selected-file-name { font-size: 12px; color: #64748b; margin-top: 5px; }
  .resume-btns { display: flex; gap: 10px; margin-top: 10px; flex-wrap: wrap; }
  
  /* ── LOADING ── */
  .loading-box {
    display: flex; align-items: center; gap: 10px;
    padding: 40px; color: #94a3b8; font-size: 14px;
    justify-content: center;
  }
  .spinner {
    width: 18px; height: 18px;
    border: 2px solid #e2e8f0;
    border-top-color: #3b82f6;
    border-radius: 50%;
    animation: spin 0.7s linear infinite;
  }
  @keyframes spin { to { transform: rotate(360deg); } }
  .muted { color: #94a3b8; font-size: 13px; }
  
  /* ── TOAST ── */
  .toast {
    position: fixed; bottom: 22px; right: 22px;
    padding: 11px 18px; border-radius: 8px;
    font-size: 14px; font-weight: 500; z-index: 9999;
    box-shadow: 0 4px 12px rgba(0,0,0,0.15);
  }
  .toast-success { background: #1e293b; color: white; }
  .toast-error { background: #ef4444; color: white; }
  .toast-fade-enter-active, .toast-fade-leave-active { transition: all 0.3s ease; }
  .toast-fade-enter-from, .toast-fade-leave-to { opacity: 0; transform: translateY(8px); }
  
  @media (max-width: 800px) {
    .two-col { grid-template-columns: 1fr; }
    .drive-detail-layout { grid-template-columns: 1fr; }
    .stats-row { flex-direction: column; }
  }
  </style>
  