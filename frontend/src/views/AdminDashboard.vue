<template>
    <div class="layout">
      <aside class="sidebar">
        <div class="sidebar-header">
          <div class="sidebar-logo">🎓</div>
          <h2>Admin Panel</h2>
        </div>
        <ul>
          <li :class="{active: section==='dashboard'}" @click="section='dashboard'">
            <span class="icon">📊</span> Dashboard
          </li>
          <li :class="{active: section==='companies'}" @click="goTo('companies')">
            <span class="icon">🏢</span> Companies
          </li>
          <li :class="{active: section==='students'}" @click="goTo('students')">
            <span class="icon">🎓</span> Students
          </li>
          <li :class="{active: section==='drives'}" @click="goTo('drives')">
            <span class="icon">📋</span> Drives
          </li>
          <li class="logout" @click="logout">
            <span class="icon">🚪</span> Logout
          </li>
        </ul>
      </aside>
  
      <main class="content">
        <!-- DASHBOARD -->
        <div v-if="section==='dashboard'">
          <div class="page-header">
            <h1>Welcome, Admin</h1>
            <span class="badge-role">Administrator</span>
          </div>
          <div class="stats-grid">
            <div class="stat-card blue"><div class="stat-icon">🏢</div><div class="stat-info"><span class="stat-val">{{ stats.total_companies||0 }}</span><span class="stat-label">Total Companies</span></div></div>
            <div class="stat-card green"><div class="stat-icon">🎓</div><div class="stat-info"><span class="stat-val">{{ stats.total_students||0 }}</span><span class="stat-label">Total Students</span></div></div>
            <div class="stat-card purple"><div class="stat-icon">📋</div><div class="stat-info"><span class="stat-val">{{ stats.total_drives||0 }}</span><span class="stat-label">Total Drives</span></div></div>
            <div class="stat-card orange"><div class="stat-icon">⏳</div><div class="stat-info"><span class="stat-val">{{ stats.pending_companies||0 }}</span><span class="stat-label">Pending Companies</span></div></div>
            <div class="stat-card teal"><div class="stat-icon">✅</div><div class="stat-info"><span class="stat-val">{{ stats.selected_students||0 }}</span><span class="stat-label">Placed Students</span></div></div>
            <div class="stat-card red"><div class="stat-icon">📝</div><div class="stat-info"><span class="stat-val">{{ stats.total_applications||0 }}</span><span class="stat-label">Applications</span></div></div>
          </div>
          <div class="quick-actions">
            <h3>Quick Actions</h3>
            <div class="action-row">
              <button class="action-btn" @click="goTo('companies')">Manage Companies</button>
              <button class="action-btn" @click="goTo('students')">Manage Students</button>
              <button class="action-btn" @click="goTo('drives')">View All Drives</button>
            </div>
          </div>
        </div>
  
        <!-- COMPANIES -->
        <div v-if="section==='companies'">
          <div class="page-header"><h1>Manage Companies</h1></div>
          <div class="toolbar">
            <input v-model="companySearch" placeholder="Search company..." class="search-input" />
            <select v-model="companyStatus" class="filter-select">
              <option value="">All Status</option>
              <option>Pending</option><option>Approved</option><option>Rejected</option>
            </select>
            <button class="btn-primary" @click="fetchCompanies">Search</button>
          </div>
          <div v-if="loading" class="loading">Loading...</div>
          <div v-else-if="companies.length===0" class="empty-state"><p>No companies found.</p></div>
          <div v-else class="table-wrapper">
            <table>
              <thead><tr><th>Company Name</th><th>HR Contact</th><th>Status</th><th>Actions</th></tr></thead>
              <tbody>
                <tr v-for="c in companies" :key="c.id">
                  <td><strong>{{ c.company_name }}</strong></td>
                  <td>{{ c.hr_contact||'—' }}</td>
                  <td><span :class="'status-badge status-'+c.approval_status.toLowerCase()">{{ c.approval_status }}</span></td>
                  <td class="action-cell">
                    <button v-if="c.approval_status!=='Approved'" class="btn-success btn-sm" @click="approveCompany(c.id)">✓ Approve</button>
                    <button v-if="c.approval_status!=='Rejected'" class="btn-warning btn-sm" @click="rejectCompany(c.id)">✗ Reject</button>
                    <button class="btn-danger btn-sm" @click="blacklist(c.user_id)">🚫 Blacklist</button>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
  
        <!-- STUDENTS -->
        <div v-if="section==='students'">
          <div class="page-header"><h1>Manage Students</h1></div>
          <div class="toolbar">
            <input v-model="studentSearch" placeholder="Search name or email..." class="search-input" />
            <button class="btn-primary" @click="fetchStudents">Search</button>
          </div>
          <div v-if="loading" class="loading">Loading...</div>
          <div v-else-if="students.length===0" class="empty-state"><p>No students found.</p></div>
          <div v-else class="table-wrapper">
            <table>
              <thead><tr><th>Name</th><th>Branch</th><th>Year</th><th>CGPA</th><th>Actions</th></tr></thead>
              <tbody>
                <tr v-for="s in students" :key="s.id">
                  <td><strong>{{ s.full_name }}</strong></td>
                  <td>{{ s.branch }}</td>
                  <td>Year {{ s.year }}</td>
                  <td>{{ s.cgpa }}</td>
                  <td><button class="btn-danger btn-sm" @click="blacklist(s.user_id)">🚫 Blacklist</button></td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
  
        <!-- DRIVES -->
        <div v-if="section==='drives'">
          <div class="page-header"><h1>Placement Drives</h1></div>
  
          <div v-if="selectedDrive" class="detail-panel">
            <div class="panel-header">
              <h2>{{ selectedDrive.job_title }}</h2>
              <button class="btn-secondary btn-sm" @click="selectedDrive=null;applications=[]">← Back</button>
            </div>
            <div class="detail-grid">
              <div class="detail-item"><label>Company</label><span>{{ selectedDrive.company_name }}</span></div>
              <div class="detail-item"><label>Status</label><span :class="'status-badge status-'+selectedDrive.status.toLowerCase()">{{ selectedDrive.status }}</span></div>
              <div class="detail-item"><label>Min CGPA</label><span>{{ selectedDrive.min_cgpa }}</span></div>
              <div class="detail-item"><label>Deadline</label><span>{{ selectedDrive.application_deadline }}</span></div>
              <div class="detail-item full-width"><label>Job Description</label><p>{{ selectedDrive.job_description }}</p></div>
            </div>
            <div class="panel-actions">
              <button class="btn-primary" @click="fetchApplications(selectedDrive.id)">View Applications ({{ selectedDrive.total_applications }})</button>
              <button v-if="selectedDrive.status==='Approved'" class="btn-warning" @click="closeDrive(selectedDrive.id)">Mark Complete</button>
            </div>
            <div v-if="applications.length" class="applications-section">
              <h3>Applications</h3>
              <table>
                <thead><tr><th>Student</th><th>Email</th><th>Branch</th><th>CGPA</th><th>Status</th><th>Actions</th></tr></thead>
                <tbody>
                  <tr v-for="a in applications" :key="a.id">
                    <td>{{ a.student.full_name }}</td>
                    <td>{{ a.student.email }}</td>
                    <td>{{ a.student.branch }}</td>
                    <td>{{ a.student.cgpa }}</td>
                    <td><span :class="'status-badge status-'+a.status.toLowerCase()">{{ a.status }}</span></td>
                    <td>
                      <button class="btn-sm btn-primary" @click="viewApplication(a)" style="margin-right:4px">👁 View</button>
                      <button v-if="a.student.resume_url" class="btn-sm btn-secondary" @click="downloadResume(a.student.id)">📄 Resume</button>
                      <span v-else class="text-muted">No resume</span>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
  
          <div v-else>
            <div class="toolbar">
              <input v-model="driveSearch" placeholder="Search job or company..." class="search-input" />
              <select v-model="driveStatus" class="filter-select">
                <option value="">All Status</option>
                <option>Pending</option><option>Approved</option><option>Rejected</option><option>Closed</option>
              </select>
              <button class="btn-primary" @click="fetchDrives">Search</button>
            </div>
            <div v-if="loading" class="loading">Loading...</div>
            <div v-else-if="drives.length===0" class="empty-state"><p>No drives found.</p></div>
            <div v-else class="table-wrapper">
              <table>
                <thead><tr><th>Job Title</th><th>Company</th><th>Deadline</th><th>Applications</th><th>Status</th><th>Actions</th></tr></thead>
                <tbody>
                  <tr v-for="d in drives" :key="d.id">
                    <td><strong>{{ d.job_title }}</strong></td>
                    <td>{{ d.company_name }}</td>
                    <td>{{ d.application_deadline }}</td>
                    <td>{{ d.total_applications }}</td>
                    <td><span :class="'status-badge status-'+d.status.toLowerCase()">{{ d.status }}</span></td>
                    <td class="action-cell">
                      <button class="btn-sm btn-secondary" @click="viewDrive(d)">Details</button>
                      <button v-if="d.status==='Approved'" class="btn-sm btn-warning" @click="closeDrive(d.id)">Complete</button>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </main>
  
      <div v-if="toast" :class="'toast toast-'+toastType">{{ toast }}</div>
    </div>
      <!-- Application Detail Modal -->
      <div v-if="selectedApp" class="modal-overlay" @click.self="selectedApp=null">
        <div class="modal-box">
          <div class="modal-header">
            <h2>Application Details</h2>
            <button class="modal-close" @click="selectedApp=null">✕</button>
          </div>
          <div class="modal-body">
            <div class="detail-grid">
              <div class="detail-item"><label>Full Name</label><span>{{ selectedApp.student.full_name }}</span></div>
              <div class="detail-item"><label>Email</label><span>{{ selectedApp.student.email }}</span></div>
              <div class="detail-item"><label>Branch</label><span>{{ selectedApp.student.branch }}</span></div>
              <div class="detail-item"><label>Year</label><span>{{ selectedApp.student.year }}</span></div>
              <div class="detail-item"><label>CGPA</label><span>{{ selectedApp.student.cgpa }}</span></div>
              <div class="detail-item"><label>Phone</label><span>{{ selectedApp.student.phone || '—' }}</span></div>
              <div class="detail-item"><label>Status</label><span :class="'status-badge status-'+selectedApp.status.toLowerCase()">{{ selectedApp.status }}</span></div>
              <div class="detail-item"><label>Applied On</label><span>{{ selectedApp.applied_on ? selectedApp.applied_on.split('T')[0] : '—' }}</span></div>
            </div>
            <div class="modal-resume-row">
              <button v-if="selectedApp.student.resume_url" class="btn-primary" @click="downloadResume(selectedApp.student.id)">📄 View Resume</button>
              <span v-else class="text-muted">No resume uploaded</span>
            </div>
          </div>
        </div>
      </div>
  
  </template>
  
  <script>
  import api from '@/services/api'
  
  export default {
    data() {
      return {
        section: 'dashboard',
        stats: {},
        companies: [],
        students: [],
        drives: [],
        applications: [],
        selectedDrive: null,
        selectedApp: null,
        companySearch: '',
        companyStatus: '',
        studentSearch: '',
        driveSearch: '',
        driveStatus: '',
        loading: false,
        toast: '',
        toastType: 'success'
      }
    },
    mounted() { this.fetchDashboard() },
    methods: {
      goTo(sec) {
        this.section = sec
        if (sec === 'companies') this.fetchCompanies()
        else if (sec === 'students') this.fetchStudents()
        else if (sec === 'drives') this.fetchDrives()
      },
      showToast(msg, type='success') {
        this.toast = msg; this.toastType = type
        setTimeout(() => { this.toast = '' }, 3000)
      },
      async fetchDashboard() {
        try { const res = await api.get('/admin/dashboard'); this.stats = res.data.data }
        catch(e) { this.showToast('Failed to load dashboard','error') }
      },
      async fetchCompanies() {
        this.loading = true
        try {
          const res = await api.get('/admin/companies', { params: { search: this.companySearch, status: this.companyStatus } })
          this.companies = res.data.data
        } catch(e) { this.showToast('Failed to load companies','error') }
        finally { this.loading = false }
      },
      async approveCompany(id) {
        try { await api.put(`/admin/companies/${id}/approve`); this.showToast('Company approved'); this.fetchCompanies(); this.fetchDashboard() }
        catch(e) { this.showToast('Failed to approve','error') }
      },
      async rejectCompany(id) {
        try { await api.put(`/admin/companies/${id}/reject`); this.showToast('Company rejected'); this.fetchCompanies() }
        catch(e) { this.showToast('Failed to reject','error') }
      },
      async fetchStudents() {
        this.loading = true
        try { const res = await api.get('/admin/students', { params: { search: this.studentSearch } }); this.students = res.data.data }
        catch(e) { this.showToast('Failed to load students','error') }
        finally { this.loading = false }
      },
      async fetchDrives() {
        this.loading = true
        try { const res = await api.get('/admin/drives', { params: { search: this.driveSearch, status: this.driveStatus } }); this.drives = res.data.data }
        catch(e) { this.showToast('Failed to load drives','error') }
        finally { this.loading = false }
      },
      viewDrive(d) { this.selectedDrive = d; this.applications = [] },
      viewApplication(app) { this.selectedApp = app },
      async closeDrive(id) {
        try {
          await api.put(`/admin/drives/${id}/close`)
          this.showToast('Drive marked complete')
          this.fetchDrives()
          if (this.selectedDrive?.id === id) this.selectedDrive.status = 'Closed'
        } catch(e) { this.showToast('Failed','error') }
      },
      async fetchApplications(id) {
        try { const res = await api.get('/admin/applications', { params: { drive_id: id } }); this.applications = res.data.data }
        catch(e) { this.showToast('Failed to load applications','error') }
      },
      async downloadResume(studentId) {
        try {
          const token = localStorage.getItem('token')
          const response = await fetch(`/api/student/resume/${studentId}`, { headers: { Authorization: `Bearer ${token}` } })
          if (!response.ok) throw new Error()
          const blob = await response.blob()
          const url = window.URL.createObjectURL(blob)
          const a = document.createElement('a')
          a.href = url
          a.target = '_blank'
          a.rel = 'noopener noreferrer'
          document.body.appendChild(a)
          a.click()
          document.body.removeChild(a)
          setTimeout(() => window.URL.revokeObjectURL(url), 1000)
        } catch(e) { this.showToast('Resume not available','error') }
      },
      async blacklist(userId) {
        if (!confirm('Blacklist this user?')) return
        try { await api.put(`/admin/users/${userId}/blacklist`); this.showToast('User blacklisted'); this.fetchCompanies(); this.fetchStudents() }
        catch(e) { this.showToast('Failed','error') }
      },
      logout() { localStorage.removeItem('token'); localStorage.removeItem('user'); window.location.href = '/login' }
    }
  }
  </script>
  
  <style scoped>
  *{box-sizing:border-box}
  .layout{display:flex;height:100vh;font-family:'Inter','Segoe UI',sans-serif;background:#f8fafc}
  .sidebar{width:240px;background:linear-gradient(180deg,#1e293b,#0f172a);color:white;padding:0;display:flex;flex-direction:column;flex-shrink:0}
  .sidebar-header{padding:24px 20px 20px;border-bottom:1px solid rgba(255,255,255,0.1);text-align:center}
  .sidebar-logo{font-size:32px;margin-bottom:8px}
  .sidebar-header h2{font-size:16px;font-weight:600;color:#e2e8f0;margin:0}
  .sidebar ul{list-style:none;padding:16px 12px;margin:0;flex:1}
  .sidebar li{padding:11px 14px;cursor:pointer;border-radius:8px;margin-bottom:4px;font-size:14px;font-weight:500;color:#94a3b8;transition:all .2s;display:flex;align-items:center;gap:10px}
  .sidebar li:hover{background:rgba(255,255,255,.08);color:#e2e8f0}
  .sidebar li.active{background:#3b82f6;color:white}
  .sidebar li.logout{color:#f87171;margin-top:8px}
  .sidebar li.logout:hover{background:rgba(248,113,113,0.1)}
  .icon{font-size:16px}
  .content{flex:1;padding:28px 32px;overflow-y:auto}
  .page-header{display:flex;align-items:center;gap:14px;margin-bottom:24px}
  .page-header h1{font-size:22px;font-weight:700;color:#1e293b;margin:0}
  .badge-role{background:#dbeafe;color:#1d4ed8;padding:4px 12px;border-radius:20px;font-size:12px;font-weight:600}
  .stats-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(175px,1fr));gap:16px;margin-bottom:28px}
  .stat-card{background:white;padding:18px;border-radius:12px;box-shadow:0 1px 3px rgba(0,0,0,.06);display:flex;align-items:center;gap:14px;border-left:4px solid transparent}
  .stat-card.blue{border-left-color:#3b82f6}.stat-card.green{border-left-color:#22c55e}.stat-card.purple{border-left-color:#a855f7}.stat-card.orange{border-left-color:#f97316}.stat-card.teal{border-left-color:#14b8a6}.stat-card.red{border-left-color:#ef4444}
  .stat-icon{font-size:24px}.stat-info{display:flex;flex-direction:column}.stat-val{font-size:26px;font-weight:700;color:#1e293b;line-height:1}.stat-label{font-size:12px;color:#64748b;margin-top:3px}
  .quick-actions{background:white;padding:20px;border-radius:12px;box-shadow:0 1px 3px rgba(0,0,0,.06)}
  .quick-actions h3{margin:0 0 14px;font-size:15px;color:#374151}
  .action-row{display:flex;gap:12px;flex-wrap:wrap}
  .action-btn{background:#f1f5f9;color:#374151;border:1px solid #e2e8f0;padding:8px 16px;border-radius:8px;cursor:pointer;font-size:13px;font-weight:500}
  .action-btn:hover{background:#e2e8f0}
  .toolbar{display:flex;gap:10px;margin-bottom:18px;flex-wrap:wrap;align-items:center}
  .search-input{padding:8px 14px;border:1px solid #e2e8f0;border-radius:8px;font-size:14px;min-width:220px;outline:none;background:white}
  .search-input:focus{border-color:#3b82f6;box-shadow:0 0 0 3px rgba(59,130,246,.1)}
  .filter-select{padding:8px 12px;border:1px solid #e2e8f0;border-radius:8px;font-size:14px;background:white;outline:none;cursor:pointer}
  .table-wrapper{background:white;border-radius:12px;overflow:hidden;box-shadow:0 1px 3px rgba(0,0,0,.06)}
  table{width:100%;border-collapse:collapse}
  thead tr{background:#f1f5f9}
  th{padding:12px 16px;text-align:left;font-size:12px;font-weight:600;text-transform:uppercase;letter-spacing:.05em;color:#64748b}
  td{padding:13px 16px;font-size:14px;color:#374151;border-bottom:1px solid #f1f5f9}
  tbody tr:last-child td{border-bottom:none}
  tbody tr:hover{background:#f8fafc}
  .action-cell{display:flex;gap:6px;flex-wrap:wrap;align-items:center}
  .status-badge{padding:3px 10px;border-radius:20px;font-size:12px;font-weight:600}
  .status-pending{background:#fef3c7;color:#d97706}.status-approved{background:#dcfce7;color:#16a34a}.status-rejected{background:#fee2e2;color:#dc2626}.status-closed{background:#f1f5f9;color:#64748b}.status-applied{background:#dbeafe;color:#2563eb}.status-shortlisted{background:#e0e7ff;color:#4338ca}.status-selected{background:#dcfce7;color:#16a34a}
  .btn-primary{background:#3b82f6;color:white;border:none;padding:9px 18px;border-radius:8px;cursor:pointer;font-size:14px;font-weight:500}
  .btn-primary:hover{background:#2563eb}
  .btn-secondary{background:white;color:#374151;border:1px solid #e2e8f0;padding:9px 18px;border-radius:8px;cursor:pointer;font-size:14px;font-weight:500}
  .btn-secondary:hover{background:#f8fafc}
  .btn-success{background:#22c55e;color:white;border:none;padding:9px 18px;border-radius:8px;cursor:pointer;font-size:14px;font-weight:500}
  .btn-success:hover{background:#16a34a}
  .btn-warning{background:#f97316;color:white;border:none;padding:9px 18px;border-radius:8px;cursor:pointer;font-size:14px;font-weight:500}
  .btn-warning:hover{background:#ea580c}
  .btn-danger{background:#ef4444;color:white;border:none;padding:9px 18px;border-radius:8px;cursor:pointer;font-size:14px;font-weight:500}
  .btn-danger:hover{background:#dc2626}
  .btn-sm{padding:5px 12px;font-size:12px;border-radius:6px;white-space:nowrap;border:none;cursor:pointer;font-weight:500}
  .detail-panel{background:white;border-radius:12px;padding:24px;box-shadow:0 1px 3px rgba(0,0,0,.06)}
  .panel-header{display:flex;justify-content:space-between;align-items:center;margin-bottom:20px;padding-bottom:16px;border-bottom:1px solid #f1f5f9}
  .panel-header h2{font-size:20px;font-weight:700;color:#1e293b;margin:0}
  .detail-grid{display:grid;grid-template-columns:repeat(2,1fr);gap:16px;margin-bottom:20px}
  .detail-item{display:flex;flex-direction:column;gap:4px}
  .detail-item.full-width{grid-column:1/-1}
  .detail-item label{font-size:11px;font-weight:600;text-transform:uppercase;color:#94a3b8}
  .detail-item span,.detail-item p{font-size:14px;color:#374151;margin:0}
  .panel-actions{display:flex;gap:10px;margin-bottom:20px}
  .applications-section{margin-top:20px;padding-top:20px;border-top:1px solid #f1f5f9}
  .applications-section h3{font-size:15px;font-weight:600;color:#374151;margin:0 0 14px}
  .loading{text-align:center;padding:40px;color:#94a3b8;font-size:14px}
  .empty-state{text-align:center;padding:60px;color:#94a3b8}
  .text-muted{color:#94a3b8;font-size:13px}
  .toast{position:fixed;bottom:24px;right:24px;padding:12px 20px;border-radius:8px;font-size:14px;font-weight:500;z-index:9999;animation:slideIn .3s ease}
  .toast-success{background:#1e293b;color:white}.toast-error{background:#ef4444;color:white}
  @keyframes slideIn{from{opacity:0;transform:translateY(10px)}to{opacity:1;transform:translateY(0)}}
  .modal-overlay{position:fixed;inset:0;background:rgba(0,0,0,0.5);display:flex;align-items:center;justify-content:center;z-index:10000}
  .modal-box{background:#fff;border-radius:12px;width:90%;max-width:560px;max-height:90vh;overflow-y:auto;box-shadow:0 20px 60px rgba(0,0,0,0.3)}
  .modal-header{display:flex;align-items:center;justify-content:space-between;padding:20px 24px;border-bottom:1px solid #e2e8f0}
  .modal-header h2{margin:0;font-size:18px;color:#1e293b}
  .modal-close{background:none;border:none;font-size:20px;cursor:pointer;color:#64748b;padding:4px 8px;border-radius:4px}
  .modal-close:hover{background:#f1f5f9}
  .modal-body{padding:20px 24px}
  .modal-resume-row{margin-top:20px;padding-top:16px;border-top:1px solid #f1f5f9}
  </style>
  