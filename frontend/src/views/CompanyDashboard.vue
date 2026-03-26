<template>
    <div class="layout">
      <!-- SIDEBAR -->
      <aside class="sidebar">
        <div class="sidebar-header">
          <div class="sidebar-logo">🏢</div>
          <h2>{{ companyName || 'Company' }}</h2>
          <span class="status-dot" :class="'dot-' + approvalStatus.toLowerCase()">
            {{ approvalStatus }}
          </span>
        </div>
        <ul>
          <li :class="{active: view==='dashboard'}" @click="navigate('dashboard')">
            <span class="icon">📊</span> Dashboard
          </li>
          <li :class="{active: view==='create'}" @click="navigate('create')">
            <span class="icon">➕</span> Create Drive
          </li>
          <li :class="{active: view.startsWith('drive')}" @click="navigate('drives')">
            <span class="icon">📋</span> Manage Drives
          </li>
          <li class="logout" @click="logout"><span class="icon">🚪</span> Logout</li>
        </ul>
      </aside>
  
      <!-- MAIN CONTENT -->
      <main class="content">
  
        <!-- ==================== DASHBOARD ==================== -->
        <div v-if="view === 'dashboard'">
          <div class="page-header">
            <div>
              <h1>Welcome {{ companyName }}</h1>
              <span class="sub">Organization Dashboard</span>
            </div>
            <button class="btn-outline btn-sm" @click="logout">Logout</button>
          </div>
  
          <div v-if="approvalStatus === 'Pending'" class="notice notice-warn">
            ⏳ Your company is pending admin approval. Drives can be created once approved.
          </div>
          <div v-if="approvalStatus === 'Rejected'" class="notice notice-error">
            ❌ Your company registration was rejected. Contact admin for support.
          </div>
  
          <div class="stats-row">
            <div class="stat-box blue"><div class="stat-num">{{ upcomingDrives.length }}</div><div class="stat-lbl">Upcoming Drives</div></div>
            <div class="stat-box green"><div class="stat-num">{{ closedDrives.length }}</div><div class="stat-lbl">Closed Drives</div></div>
            <div class="stat-box purple"><div class="stat-num">{{ totalApps }}</div><div class="stat-lbl">Total Applications</div></div>
          </div>
  
          <!-- Upcoming drives preview -->
          <div class="card" v-if="upcomingDrives.length">
            <div class="card-header"><h3>Upcoming Drives</h3></div>
            <table>
              <thead><tr><th>Sr No.</th><th>Drive Name</th><th>Actions</th></tr></thead>
              <tbody>
                <tr v-for="(d, idx) in upcomingDrives" :key="d.id">
                  <td>{{ 1001 + idx }}</td>
                  <td>{{ d.job_title }}</td>
                  <td class="action-cell">
                    <button class="btn-sm btn-blue" @click="viewDriveDetail(d)">View Details</button>
                    <button class="btn-sm btn-orange" @click="markComplete(d.id)">Mark Complete</button>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
  
        <!-- ==================== CREATE DRIVE ==================== -->
        <div v-if="view === 'create'">
          <div class="page-header"><h1>Create New Drive</h1></div>
          <div v-if="approvalStatus !== 'Approved'" class="notice notice-warn">
            ⚠️ Your company must be approved by admin before creating drives.
          </div>
          <div v-else class="card" style="max-width:680px">
            <div class="form-group">
              <label>Drive Name *</label>
              <input v-model="form.job_title" placeholder="e.g. Senior Software Developer" class="form-inp" />
            </div>
            <div class="form-group">
              <label>Job Description *</label>
              <textarea v-model="form.job_description" placeholder="Describe the role and responsibilities..." class="form-inp" rows="4"></textarea>
            </div>
            <div class="form-row-2">
              <div class="form-group">
                <label>Minimum CGPA</label>
                <input v-model="form.min_cgpa" type="number" step="0.1" min="0" max="10" placeholder="e.g. 7.5" class="form-inp" />
              </div>
              <div class="form-group">
                <label>Application Deadline *</label>
                <input v-model="form.application_deadline" type="date" class="form-inp" />
              </div>
            </div>
            <div class="form-row-2">
              <div class="form-group">
                <label>Allowed Branches</label>
                <input v-model="form.allowed_branches" placeholder="CSE,ECE,IT (blank = all)" class="form-inp" />
              </div>
              <div class="form-group">
                <label>Allowed Years</label>
                <input v-model="form.allowed_years" placeholder="3,4 (blank = all)" class="form-inp" />
              </div>
            </div>
            <div class="form-group">
              <label>Eligibility Criteria</label>
              <input v-model="form.eligibility_criteria" placeholder="Any additional criteria" class="form-inp" />
            </div>
            <div v-if="createError" class="notice notice-error">{{ createError }}</div>
            <div class="action-bar">
              <button class="btn-primary" @click="createDrive" :disabled="creating">
                {{ creating ? 'Saving...' : '💾 Save Drive' }}
              </button>
              <button class="btn-outline" @click="navigate('drives')">Cancel</button>
            </div>
          </div>
        </div>
  
        <!-- ==================== DRIVES LIST ==================== -->
        <div v-if="view === 'drives'">
          <div class="page-header">
            <h1>Manage Drives</h1>
            <button class="btn-primary" @click="navigate('create')">+ Create Drive</button>
          </div>
          <div v-if="loading" class="loading-box"><div class="spinner"></div> Loading...</div>
          <div v-else>
            <!-- Upcoming -->
            <div class="card">
              <div class="card-header"><h3>Upcoming Drives <span class="count-badge">{{ upcomingDrives.length }}</span></h3></div>
              <div v-if="upcomingDrives.length === 0" class="muted" style="padding:10px 0">No upcoming drives.</div>
              <table v-else>
                <thead><tr><th>Sr No.</th><th>Drive Name</th><th>Deadline</th><th>Apps</th><th>Status</th><th>Actions</th></tr></thead>
                <tbody>
                  <tr v-for="(d, idx) in upcomingDrives" :key="d.id">
                    <td>{{ 1001 + idx }}</td>
                    <td><strong>{{ d.job_title }}</strong></td>
                    <td>{{ d.application_deadline }}</td>
                    <td>{{ d.total_applications }}</td>
                    <td><span class="status-chip chip-approved">{{ d.status }}</span></td>
                    <td class="action-cell">
                      <button class="btn-sm btn-blue" @click="viewDriveDetail(d)">View Details</button>
                      <button class="btn-sm btn-orange" @click="markComplete(d.id)">Mark Complete</button>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
  
            <!-- Closed -->
            <div class="card">
              <div class="card-header"><h3>Closed Drives <span class="count-badge">{{ closedDrives.length }}</span></h3></div>
              <div v-if="closedDrives.length === 0" class="muted" style="padding:10px 0">No closed drives.</div>
              <table v-else>
                <thead><tr><th>Sr No.</th><th>Drive Name</th><th>Deadline</th><th>Status</th><th>Actions</th></tr></thead>
                <tbody>
                  <tr v-for="(d, idx) in closedDrives" :key="d.id">
                    <td>{{ 1011 + idx }}</td>
                    <td><strong>{{ d.job_title }}</strong></td>
                    <td>{{ d.application_deadline }}</td>
                    <td><span class="status-chip chip-closed">{{ d.status }}</span></td>
                    <td><button class="btn-sm btn-blue" @click="viewDriveDetail(d)">Update</button></td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>
  
        <!-- ==================== DRIVE DETAIL ==================== -->
        <div v-if="view === 'drive-detail'">
          <div class="page-header">
            <h1>{{ currentDrive && currentDrive.job_title }}</h1>
            <button class="btn-back" @click="navigate('drives')">← Back</button>
          </div>
          <div class="two-col">
            <div class="card">
              <h3>Drive Information</h3>
              <div class="detail-row"><label>Job Title</label><span>{{ currentDrive && currentDrive.job_title }}</span></div>
              <div class="detail-row"><label>Status</label>
                <span :class="'status-chip chip-' + ((currentDrive && currentDrive.status) || '').toLowerCase()">
                  {{ currentDrive && currentDrive.status }}
                </span>
              </div>
              <div class="detail-row"><label>Min CGPA</label><span>{{ currentDrive && currentDrive.min_cgpa }}</span></div>
              <div class="detail-row"><label>Deadline</label><span>{{ currentDrive && currentDrive.application_deadline }}</span></div>
              <div class="detail-row"><label>Allowed Branches</label><span>{{ (currentDrive && currentDrive.allowed_branches) || 'All' }}</span></div>
              <div class="detail-row"><label>Description</label><p class="desc-text">{{ currentDrive && currentDrive.job_description }}</p></div>
            </div>
            <div class="card">
              <h3>Actions</h3>
              <div class="drive-actions-panel">
                <button
                  class="btn-primary full-btn"
                  @click="loadApplicationsForDrive(currentDrive.id)">
                  📋 View Applications ({{ currentDrive && currentDrive.total_applications }})
                </button>
                <button
                  v-if="currentDrive && currentDrive.status === 'Approved'"
                  class="btn-orange full-btn"
                  @click="markComplete(currentDrive.id)">
                  ✓ Mark as Complete
                </button>
              </div>
            </div>
          </div>
  
          <!-- Applications section - shown when loaded -->
          <div class="card" v-if="showApps">
            <div class="card-header">
              <h3>Update Applications for the Drive</h3>
              <div class="drive-title-sub">Job Title: {{ currentDrive && currentDrive.job_title }}</div>
            </div>
  
            <div v-if="appsLoading" class="loading-box"><div class="spinner"></div> Loading applications...</div>
            <div v-else-if="driveApps.length === 0" class="muted" style="padding:14px 0">No applications received yet.</div>
            <div v-else>
              <div class="sub-heading">Received Applications</div>
              <div v-for="app in driveApps" :key="app.id" class="app-row">
                <div class="app-row-left">
                  <div class="app-name">{{ app.student && app.student.full_name }}</div>
                  <div class="app-meta">{{ app.student && app.student.branch }} · CGPA {{ app.student && app.student.cgpa }}</div>
                </div>
                <div class="app-row-right">
                  <button class="btn-sm btn-blue" @click="reviewApplication(app)">Review Application</button>
                </div>
              </div>
              <div class="save-row">
                <button class="btn-primary" @click="saveAllStatuses">Save Changes</button>
              </div>
            </div>
          </div>
        </div>
  
        <!-- ==================== REVIEW APPLICATION ==================== -->
        <div v-if="view === 'review-app'">
          <div class="page-header">
            <h1>Student Application</h1>
            <button class="btn-back" @click="view='drive-detail'">← Back</button>
          </div>
          <div class="two-col" v-if="currentApp">
            <div class="card">
              <div class="student-avatar-row">
                <div class="student-avatar">🎓</div>
                <div>
                  <div class="student-name">{{ currentApp.student && currentApp.student.full_name }}</div>
                  <div class="student-dept">Department: {{ currentApp.student && currentApp.student.branch }}</div>
                </div>
              </div>
              <div class="detail-row"><label>Drive</label><span>{{ currentApp.drive && currentApp.drive.job_title }}</span></div>
              <div class="detail-row"><label>Job Title</label><span>{{ currentApp.drive && currentApp.drive.job_title }}</span></div>
              <div class="detail-row"><label>Email</label><span>{{ currentApp.student && currentApp.student.email }}</span></div>
              <div class="detail-row"><label>CGPA</label><span>{{ currentApp.student && currentApp.student.cgpa }}</span></div>
              <div class="detail-row"><label>Year</label><span>{{ currentApp.student && currentApp.student.year }}</span></div>
              <div class="detail-row"><label>Phone</label><span>{{ (currentApp.student && currentApp.student.phone) || '—' }}</span></div>
              <div class="resume-action">
                <button
                  v-if="currentApp.student && currentApp.student.resume_url"
                  class="btn-outline"
                  @click="downloadResume(currentApp.student.id)">
                  📄 View Resume
                </button>
                <span v-else class="muted">No resume uploaded</span>
              </div>
            </div>
            <div class="card">
              <h3>Update Status</h3>
              <div class="form-group" style="margin-top:8px">
                <label>Application Status</label>
                <select v-model="currentApp.status" class="form-inp form-select">
                  <option value="Applied">Applied</option>
                  <option value="Shortlisted">Short Listed</option>
                  <option value="Waiting">Waiting</option>
                  <option value="Rejected">Reject</option>
                  <option value="Selected">Selected</option>
                </select>
              </div>
              <div class="form-group">
                <label>Remarks / Notes</label>
                <textarea v-model="currentApp.notes" class="form-inp" rows="3" placeholder="Optional remarks..."></textarea>
              </div>
              <button class="btn-primary" @click="saveStatus(currentApp)">Save Status</button>
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
    name: 'CompanyDashboard',
    data() {
      return {
        view: 'dashboard',
  
        // Company info
        companyName: '',
        approvalStatus: 'Pending',
  
        // Drives
        upcomingDrives: [],
        closedDrives: [],
  
        // Current drive detail
        currentDrive: null,
        showApps: false,
        driveApps: [],
        appsLoading: false,
  
        // Current app review
        currentApp: null,
  
        // Create form
        form: {
          job_title: '',
          job_description: '',
          min_cgpa: '',
          application_deadline: '',
          allowed_branches: '',
          allowed_years: '',
          eligibility_criteria: ''
        },
        createError: '',
        creating: false,
  
        loading: false,
        toast: '',
        toastType: 'success'
      }
    },
  
    computed: {
      totalApps() {
        const all = [...this.upcomingDrives, ...this.closedDrives]
        return all.reduce((s, d) => s + (d.total_applications || 0), 0)
      }
    },
  
    mounted() {
      this.loadProfile()
      this.loadDrives()
    },
  
    methods: {
      showToast(msg, type = 'success') {
        this.toast = msg
        this.toastType = type
        setTimeout(() => { this.toast = '' }, 3500)
      },
  
      navigate(target) {
        if (target === 'drives') {
          this.view = 'drives'
          this.showApps = false
          this.loadDrives()
        } else if (target === 'create') {
          this.view = 'create'
        } else if (target === 'dashboard') {
          this.view = 'dashboard'
          this.loadDrives()
        }
      },
  
      async loadProfile() {
        try {
          const res = await api.get('/company/profile')
          const d = res.data.data
          this.companyName = d.company_name || 'Company'
          this.approvalStatus = d.approval_status || 'Pending'
        } catch (e) {
          console.error('loadProfile:', e)
        }
      },
  
      async loadDrives() {
        this.loading = true
        try {
          const res = await api.get('/company/drives')
          const d = res.data.data || {}
          this.upcomingDrives = d.upcoming || []
          this.closedDrives = d.closed || []
        } catch (e) {
          console.error('loadDrives:', e)
          this.showToast('Failed to load drives', 'error')
        } finally {
          this.loading = false
        }
      },
  
      async createDrive() {
        this.createError = ''
        if (!this.form.job_title.trim()) { this.createError = 'Drive Name is required.'; return }
        if (!this.form.job_description.trim()) { this.createError = 'Job Description is required.'; return }
        if (!this.form.application_deadline) { this.createError = 'Application Deadline is required.'; return }
  
        this.creating = true
        try {
          await api.post('/company/drives', {
            job_title: this.form.job_title,
            job_description: this.form.job_description,
            min_cgpa: parseFloat(this.form.min_cgpa) || 0,
            application_deadline: this.form.application_deadline,
            allowed_branches: this.form.allowed_branches,
            allowed_years: this.form.allowed_years
          })
          this.showToast('Drive created successfully!')
          this.form = { job_title:'', job_description:'', min_cgpa:'', application_deadline:'', allowed_branches:'', allowed_years:'', eligibility_criteria:'' }
          await this.loadDrives()
          this.view = 'drives'
        } catch (e) {
          this.createError = e.response?.data?.error || 'Failed to create drive'
        } finally {
          this.creating = false
        }
      },
  
      viewDriveDetail(drive) {
        this.currentDrive = drive
        this.showApps = false
        this.driveApps = []
        this.view = 'drive-detail'
      },
  
      async markComplete(driveId) {
        try {
          await api.put(`/company/drives/${driveId}/complete`)
          this.showToast('Drive marked as complete')
          await this.loadDrives()
          // Update current drive if viewing it
          if (this.currentDrive && Number(this.currentDrive.id) === Number(driveId)) {
            this.currentDrive = { ...this.currentDrive, status: 'Closed' }
          }
        } catch (e) {
          this.showToast(e.response?.data?.error || 'Failed to mark complete', 'error')
        }
      },
  
      async loadApplicationsForDrive(driveId) {
        this.showApps = true
        this.appsLoading = true
        this.driveApps = []
        try {
          const res = await api.get(`/company/drives/${driveId}/applications`)
          this.driveApps = res.data.data || []
        } catch (e) {
          console.error('loadApplicationsForDrive:', e)
          this.showToast('Failed to load applications', 'error')
          this.driveApps = []
        } finally {
          this.appsLoading = false
        }
      },
  
      reviewApplication(app) {
        this.currentApp = { ...app }  // Clone to avoid reactivity issues
        this.view = 'review-app'
      },
  
      async saveStatus(app) {
        try {
          await api.put(`/company/applications/${app.id}/status`, {
            status: app.status,
            notes: app.notes || ''
          })
          this.showToast('Status updated!')
          // Update in list
          const idx = this.driveApps.findIndex(a => a.id === app.id)
          if (idx >= 0) {
            this.driveApps[idx].status = app.status
            this.driveApps[idx].notes = app.notes
          }
        } catch (e) {
          this.showToast(e.response?.data?.error || 'Failed to update status', 'error')
        }
      },
  
      async saveAllStatuses() {
        this.showToast('All changes have been saved')
      },
  
      async downloadResume(studentId) {
        try {
          const token = localStorage.getItem('token')
          const res = await fetch(`/api/company/resume/${studentId}`, {
            headers: { Authorization: `Bearer ${token}` }
          })
          if (!res.ok) throw new Error('Resume not found')
          const blob = await res.blob()
          const url = URL.createObjectURL(blob)
          const a = document.createElement('a')
          a.href = url
          a.target = '_blank'
          a.rel = 'noopener noreferrer'
          document.body.appendChild(a)
          a.click()
          document.body.removeChild(a)
          setTimeout(() => URL.revokeObjectURL(url), 1000)
        } catch (e) {
          this.showToast('Resume not available', 'error')
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
    display: flex; height: 100vh;
    font-family: 'Inter', 'Segoe UI', sans-serif;
    background: #f1f5f9; overflow: hidden;
  }
  
  /* ── SIDEBAR ── */
  .sidebar {
    width: 230px;
    background: linear-gradient(180deg, #1e293b 0%, #0f172a 100%);
    color: white; display: flex; flex-direction: column; flex-shrink: 0; overflow-y: auto;
  }
  .sidebar-header {
    padding: 20px 16px 16px; border-bottom: 1px solid rgba(255,255,255,0.08); text-align: center;
  }
  .sidebar-logo { font-size: 30px; margin-bottom: 6px; }
  .sidebar-header h2 { font-size: 13px; font-weight: 600; color: #e2e8f0; margin: 0 0 8px; word-break: break-word; line-height: 1.4; }
  .status-dot {
    padding: 2px 10px; border-radius: 20px; font-size: 11px; font-weight: 600; display: inline-block;
  }
  .dot-pending { background: rgba(251,191,36,0.2); color: #fbbf24; }
  .dot-approved { background: rgba(34,197,94,0.2); color: #4ade80; }
  .dot-rejected { background: rgba(239,68,68,0.2); color: #f87171; }
  
  .sidebar ul { list-style: none; padding: 14px 10px; margin: 0; flex: 1; }
  .sidebar li {
    padding: 10px 12px; cursor: pointer; border-radius: 8px; margin-bottom: 3px;
    font-size: 13px; font-weight: 500; color: #94a3b8; transition: all 0.18s;
    display: flex; align-items: center; gap: 9px; user-select: none;
  }
  .sidebar li:hover { background: rgba(255,255,255,0.07); color: #e2e8f0; }
  .sidebar li.active { background: #3b82f6; color: white; }
  .sidebar li.logout { color: #f87171; margin-top: 8px; }
  .sidebar li.logout:hover { background: rgba(248,113,113,0.12); }
  .icon { font-size: 15px; }
  
  /* ── CONTENT ── */
  .content { flex: 1; padding: 26px 30px; overflow-y: auto; }
  
  .page-header { display: flex; align-items: flex-start; justify-content: space-between; margin-bottom: 22px; }
  .page-header h1 { font-size: 20px; font-weight: 700; color: #1e293b; margin: 0 0 2px; }
  .sub { font-size: 13px; color: #64748b; }
  
  /* ── STATS ── */
  .stats-row { display: flex; gap: 14px; margin-bottom: 22px; flex-wrap: wrap; }
  .stat-box {
    flex: 1; min-width: 120px; background: white; border-radius: 12px;
    padding: 16px; box-shadow: 0 1px 4px rgba(0,0,0,0.06); border-left: 4px solid transparent;
  }
  .stat-box.blue { border-left-color: #3b82f6; }
  .stat-box.green { border-left-color: #22c55e; }
  .stat-box.purple { border-left-color: #a855f7; }
  .stat-num { font-size: 28px; font-weight: 700; color: #1e293b; line-height: 1; }
  .stat-lbl { font-size: 12px; color: #64748b; margin-top: 4px; }
  
  /* ── NOTICE ── */
  .notice {
    padding: 11px 16px; border-radius: 8px; font-size: 14px; margin-bottom: 18px;
  }
  .notice-warn { background: #fef3c7; color: #92400e; border: 1px solid #fde68a; }
  .notice-error { background: #fee2e2; color: #991b1b; border: 1px solid #fecaca; }
  
  /* ── CARDS ── */
  .card {
    background: white; border-radius: 12px; padding: 20px;
    box-shadow: 0 1px 4px rgba(0,0,0,0.06); margin-bottom: 18px;
  }
  .card h3 { font-size: 15px; font-weight: 600; color: #1e293b; margin: 0 0 14px; }
  .card-header { display: flex; align-items: center; gap: 10px; margin-bottom: 14px; }
  .card-header h3 { margin: 0; }
  .drive-title-sub { font-size: 13px; color: #64748b; }
  
  .two-col { display: grid; grid-template-columns: 1fr 1fr; gap: 18px; }
  
  /* ── TABLE ── */
  table { width: 100%; border-collapse: collapse; }
  thead tr { background: #f8fafc; }
  th { padding: 10px 13px; text-align: left; font-size: 11px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.04em; color: #64748b; }
  td { padding: 11px 13px; font-size: 13px; color: #374151; border-bottom: 1px solid #f1f5f9; }
  tbody tr:last-child td { border-bottom: none; }
  tbody tr:hover { background: #f8fafc; }
  .action-cell { display: flex; gap: 7px; flex-wrap: wrap; align-items: center; }
  
  /* ── STATUS CHIPS ── */
  .status-chip { padding: 3px 10px; border-radius: 20px; font-size: 12px; font-weight: 600; display: inline-block; }
  .chip-approved { background: #dcfce7; color: #15803d; }
  .chip-pending { background: #fef3c7; color: #d97706; }
  .chip-rejected { background: #fee2e2; color: #dc2626; }
  .chip-closed { background: #f1f5f9; color: #64748b; }
  .chip-applied { background: #dbeafe; color: #1d4ed8; }
  .chip-shortlisted { background: #ede9fe; color: #6d28d9; }
  .chip-selected { background: #dcfce7; color: #15803d; }
  .chip-waiting { background: #fef3c7; color: #d97706; }
  
  .count-badge { background: #e0e7ff; color: #4338ca; padding: 1px 8px; border-radius: 20px; font-size: 12px; font-weight: 600; margin-left: 6px; }
  
  /* ── BUTTONS ── */
  .btn-primary { background: #3b82f6; color: white; border: none; padding: 9px 18px; border-radius: 8px; cursor: pointer; font-size: 14px; font-weight: 600; transition: background 0.18s; }
  .btn-primary:hover { background: #2563eb; }
  .btn-primary:disabled { background: #93c5fd; cursor: not-allowed; }
  .full-btn { width: 100%; margin-bottom: 10px; }
  .btn-orange { background: #f97316; color: white; border: none; padding: 9px 18px; border-radius: 8px; cursor: pointer; font-size: 14px; font-weight: 600; }
  .btn-orange:hover { background: #ea580c; }
  .btn-outline { background: white; color: #374151; border: 1px solid #e2e8f0; padding: 7px 14px; border-radius: 7px; cursor: pointer; font-size: 13px; font-weight: 500; }
  .btn-outline:hover { background: #f8fafc; }
  .btn-back { background: white; color: #374151; border: 1px solid #e2e8f0; padding: 7px 14px; border-radius: 7px; cursor: pointer; font-size: 13px; font-weight: 500; }
  .btn-back:hover { background: #f8fafc; }
  .btn-sm { padding: 5px 12px; font-size: 12px; border-radius: 6px; cursor: pointer; font-weight: 500; white-space: nowrap; border: none; }
  .btn-blue { background: #eff6ff; color: #1d4ed8; border: 1px solid #bfdbfe; }
  .btn-blue:hover { background: #dbeafe; }
  .btn-sm.btn-orange { padding: 5px 12px; font-size: 12px; }
  
  /* ── DETAIL ROWS ── */
  .detail-row { display: flex; flex-direction: column; gap: 3px; margin-bottom: 13px; }
  .detail-row label { font-size: 11px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.05em; color: #94a3b8; }
  .detail-row span { font-size: 14px; color: #374151; }
  .detail-row p { font-size: 14px; color: #374151; margin: 0; line-height: 1.6; }
  .desc-text { white-space: pre-wrap; }
  
  /* ── DRIVE ACTIONS ── */
  .drive-actions-panel { display: flex; flex-direction: column; gap: 0; padding-top: 4px; }
  
  /* ── APPLICATIONS LIST ── */
  .sub-heading { font-size: 13px; font-weight: 600; color: #64748b; margin-bottom: 10px; text-transform: uppercase; letter-spacing: 0.04em; }
  .app-row {
    display: flex; align-items: center; justify-content: space-between;
    padding: 12px 14px; border: 1px solid #f1f5f9; border-radius: 8px;
    margin-bottom: 8px; transition: background 0.15s;
  }
  .app-row:hover { background: #f8fafc; }
  .app-row-left { flex: 1; }
  .app-name { font-weight: 600; font-size: 14px; color: #1e293b; }
  .app-meta { font-size: 12px; color: #64748b; margin-top: 2px; }
  .app-row-right { flex-shrink: 0; }
  .save-row { display: flex; justify-content: flex-end; margin-top: 14px; }
  
  /* ── STUDENT REVIEW ── */
  .student-avatar-row { display: flex; align-items: center; gap: 14px; margin-bottom: 18px; padding-bottom: 16px; border-bottom: 1px solid #f1f5f9; }
  .student-avatar { width: 50px; height: 50px; background: linear-gradient(135deg, #dbeafe, #ede9fe); border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 22px; flex-shrink: 0; }
  .student-name { font-weight: 700; font-size: 16px; color: #1e293b; }
  .student-dept { font-size: 13px; color: #64748b; margin-top: 2px; }
  .resume-action { margin-top: 14px; padding-top: 14px; border-top: 1px solid #f1f5f9; }
  
  /* ── FORMS ── */
  .form-group { display: flex; flex-direction: column; gap: 5px; margin-bottom: 14px; }
  .form-group label { font-size: 12px; font-weight: 600; color: #374151; }
  .form-inp { padding: 8px 11px; border: 1px solid #e2e8f0; border-radius: 7px; font-size: 14px; outline: none; width: 100%; font-family: inherit; }
  .form-inp:focus { border-color: #3b82f6; box-shadow: 0 0 0 3px rgba(59,130,246,0.1); }
  textarea.form-inp { resize: vertical; }
  .form-select { background: white; cursor: pointer; }
  .form-row-2 { display: grid; grid-template-columns: 1fr 1fr; gap: 14px; }
  .action-bar { display: flex; align-items: center; gap: 10px; margin-top: 8px; }
  
  /* ── LOADING ── */
  .loading-box { display: flex; align-items: center; gap: 10px; padding: 40px; color: #94a3b8; font-size: 14px; justify-content: center; }
  .spinner { width: 18px; height: 18px; border: 2px solid #e2e8f0; border-top-color: #3b82f6; border-radius: 50%; animation: spin 0.7s linear infinite; }
  @keyframes spin { to { transform: rotate(360deg); } }
  .muted { color: #94a3b8; font-size: 13px; }
  
  /* ── TOAST ── */
  .toast { position: fixed; bottom: 22px; right: 22px; padding: 11px 18px; border-radius: 8px; font-size: 14px; font-weight: 500; z-index: 9999; box-shadow: 0 4px 12px rgba(0,0,0,0.15); }
  .toast-success { background: #1e293b; color: white; }
  .toast-error { background: #ef4444; color: white; }
  .toast-fade-enter-active, .toast-fade-leave-active { transition: all 0.3s ease; }
  .toast-fade-enter-from, .toast-fade-leave-to { opacity: 0; transform: translateY(8px); }
  
  @media (max-width: 800px) {
    .two-col { grid-template-columns: 1fr; }
    .form-row-2 { grid-template-columns: 1fr; }
  }
  </style>
  