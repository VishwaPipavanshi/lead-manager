import { useCallback, useEffect, useMemo, useState } from 'react'
import {
  ArrowDownUp, Bell, Check, ChevronLeft, ChevronRight, CirclePlus,
  Command, LayoutDashboard, LogOut, Menu, Moon, MoreHorizontal, Pencil, Plus, Search,
  Settings, Sparkles, Sun, Trash2, TrendingUp, UserRound, Users, X,
} from 'lucide-react'
import { useAuth } from '../context/AuthContext'
import { useTheme } from '../context/ThemeContext'
import { getErrorMessage } from '../services/api'
import { leadService } from '../services/leadService'

const STATUS_OPTIONS = ['New', 'Contacted', 'Qualified', 'Lost']
const SOURCES = ['Website', 'Referral', 'Social Media', 'Advertisement', 'Cold Call', 'Other']
const EMPTY_FORM = { name: '', email: '', phone: '', company: '', source: 'Website', status: 'New' }

function Stat({ label, value, tone, icon: Icon, detail }) {
  return (
    <article className={`metric-card ${tone}`}>
      <div className="metric-top"><span className="metric-icon"><Icon size={17} /></span><span className="metric-label">{label}</span><MoreHorizontal size={17} className="metric-more" /></div>
      <strong>{value}</strong>
      <span className="metric-detail">{detail}</span>
    </article>
  )
}

function LeadForm({ lead, onClose, onSaved }) {
  const [form, setForm] = useState(lead ? { ...lead } : { ...EMPTY_FORM })
  const [error, setError] = useState('')
  const [busy, setBusy] = useState(false)

  async function submit(event) {
    event.preventDefault()
    setError('')
    setBusy(true)
    try {
      if (lead) await leadService.update(lead.id, form)
      else await leadService.create(form)
      await onSaved()
      onClose()
    } catch (requestError) {
      setError(getErrorMessage(requestError))
    } finally {
      setBusy(false)
    }
  }

  function set(field, value) {
    setForm((current) => ({ ...current, [field]: value }))
  }

  return (
    <div className="modal-backdrop" role="presentation" onMouseDown={(event) => event.target === event.currentTarget && onClose()}>
      <section className="modal" role="dialog" aria-modal="true" aria-labelledby="lead-form-title">
        <div className="modal-heading">
          <div><p className="eyebrow">{lead ? 'LEAD DETAILS' : 'NEW OPPORTUNITY'}</p><h2 id="lead-form-title">{lead ? 'Edit lead' : 'Add a lead'}</h2></div>
          <button className="icon-button" aria-label="Close form" onClick={onClose}><X size={19} /></button>
        </div>
        <form onSubmit={submit} className="lead-form">
          <label>Full name<input required minLength="2" maxLength="100" value={form.name} onChange={(event) => set('name', event.target.value)} /></label>
          <div className="form-grid"><label>Email<input type="email" required value={form.email} onChange={(event) => set('email', event.target.value)} /></label><label>Phone<input type="tel" required minLength="7" maxLength="32" placeholder="+1 415 555 2671" value={form.phone} onChange={(event) => set('phone', event.target.value)} /></label></div>
          <label>Company<input required maxLength="120" value={form.company} onChange={(event) => set('company', event.target.value)} /></label>
          <div className="form-grid"><label>Source<select value={form.source} onChange={(event) => set('source', event.target.value)}>{SOURCES.map((source) => <option key={source}>{source}</option>)}</select></label><label>Status<select value={form.status} onChange={(event) => set('status', event.target.value)}>{STATUS_OPTIONS.map((status) => <option key={status}>{status}</option>)}</select></label></div>
          {error && <div role="alert" className="alert">{error}</div>}
          <div className="modal-actions"><button type="button" className="button button-quiet" onClick={onClose}>Cancel</button><button className="button button-primary" disabled={busy}>{busy ? 'Saving…' : lead ? 'Save changes' : 'Create lead'}</button></div>
        </form>
      </section>
    </div>
  )
}

function Donut({ stats }) {
  const total = stats?.total || 0
  const values = [stats?.qualified || 0, stats?.contacted || 0, stats?.new || 0, stats?.lost || 0]
  const colors = ['#7c6cff', '#3fd6c7', '#f3b35d', '#ef7180']
  let offset = 0
  const segments = values.map((value, index) => {
    const segment = total ? (value / total) * 100 : 0
    const result = { segment, offset, color: colors[index] }
    offset += segment
    return result
  })
  return <div className="donut" style={{ background: total ? `conic-gradient(${segments.map(({ color, segment, offset: start }) => `${color} ${start}% ${start + segment}%`).join(', ')})` : 'conic-gradient(#263149 0 100%)' }}><div><strong>{total}</strong><span>Total leads</span></div></div>
}

export default function DashboardPage() {
  const { user, signOut } = useAuth()
  const { theme, toggleTheme } = useTheme()
  const [stats, setStats] = useState(null)
  const [pageData, setPageData] = useState(null)
  const [page, setPage] = useState(1)
  const [search, setSearch] = useState('')
  const [status, setStatus] = useState('')
  const [sortOrder, setSortOrder] = useState('desc')
  const [modalLead, setModalLead] = useState(null)
  const [showForm, setShowForm] = useState(false)
  const [mobileNav, setMobileNav] = useState(false)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  const loadData = useCallback(async () => {
    setLoading(true)
    setError('')
    try {
      const params = { page, limit: 8, sort_by: 'created_at', order: sortOrder }
      if (search.trim()) params.search = search.trim()
      if (status) params.status = status
      const [leads, dashboardStats] = await Promise.all([leadService.list(params), leadService.stats()])
      setPageData(leads)
      if (leads.pages > 0 && page > leads.pages) setPage(leads.pages)
      setStats(dashboardStats)
    } catch (requestError) {
      setError(getErrorMessage(requestError))
    } finally {
      setLoading(false)
    }
  }, [page, search, sortOrder, status])

  useEffect(() => { loadData() }, [loadData])

  async function changeStatus(lead, nextStatus) {
    try { await leadService.updateStatus(lead.id, nextStatus); await loadData() } catch (requestError) { setError(getErrorMessage(requestError)) }
  }

  async function deleteLead(lead) {
    if (!window.confirm(`Delete ${lead.name}'s lead? This cannot be undone.`)) return
    try { await leadService.remove(lead.id); await loadData() } catch (requestError) { setError(getErrorMessage(requestError)) }
  }

  const conversionRate = stats?.total ? Math.round((stats.qualified / stats.total) * 100) : 0
  const initials = user?.name?.slice(0, 1).toUpperCase()
  const leadCountLabel = useMemo(() => `${stats?.total || 0} ${stats?.total === 1 ? 'lead' : 'leads'} in your workspace`, [stats?.total])

  return (
    <div className="app-shell">
      <aside className={`sidebar ${mobileNav ? 'sidebar-open' : ''}`}>
        <div className="sidebar-brand"><img src="/assets/branding/logo-icon.svg" alt="" /><span>Leadflow</span></div>
        <div className="nav-label">Workspace</div>
        <nav className="side-nav" aria-label="Main navigation">
          <a className="nav-item active" href="#dashboard"><LayoutDashboard size={18} /><span>Overview</span></a>
          <a className="nav-item" href="#leads"><Users size={18} /><span>All leads</span><span className="nav-count">{stats?.total || 0}</span></a>
          <button className="nav-item" onClick={() => { setModalLead(null); setShowForm(true); setMobileNav(false) }}><CirclePlus size={18} /><span>Add lead</span></button>
        </nav>
        <div className="nav-label">Account</div>
        <nav className="side-nav">
          <button className="nav-item"><Settings size={18} /><span>Settings</span></button>
          <button className="nav-item"><UserRound size={18} /><span>Profile</span></button>
        </nav>
        <div className="sidebar-bottom">
          <div className="sidebar-promo"><Sparkles size={17} /><strong>Make every lead count</strong><span>Stay focused on what moves the pipeline.</span></div>
          <button className="nav-item logout-item" onClick={signOut}><LogOut size={18} /><span>Sign out</span></button>
          <div className="sidebar-user"><span className="avatar">{initials}</span><div><strong>{user?.name}</strong><span>{user?.email}</span></div><MoreHorizontal size={16} /></div>
        </div>
      </aside>
      {mobileNav && <button className="mobile-nav-backdrop" aria-label="Close navigation" onClick={() => setMobileNav(false)} />}
      <div className="main-shell">
        <header className="topbar">
          <button className="mobile-menu icon-button" aria-label="Open navigation" onClick={() => setMobileNav(true)}><Menu size={20} /></button>
          <div className="breadcrumb"><span>Workspace</span><ChevronRight size={14} /><strong>Overview</strong></div>
          <div className="topbar-right">
            <button className="header-search" aria-label="Search leads" onClick={() => document.querySelector('.search-field input')?.focus()}><Search size={17} /><span>Search</span><kbd><Command size={11} /> K</kbd></button>
            <button className="icon-button header-icon" aria-label="Notifications"><Bell size={18} /><i /></button>
            <button className="icon-button header-icon" aria-label={`Switch to ${theme === 'dark' ? 'light' : 'dark'} theme`} onClick={toggleTheme}>{theme === 'dark' ? <Sun size={18} /> : <Moon size={18} />}</button>
            <span className="avatar topbar-avatar">{initials}</span>
          </div>
        </header>
        <main className="workspace" id="dashboard">
          <div className="page-heading"><div><p className="eyebrow">MONDAY, OCTOBER 28, 2024</p><h1>Good morning, {user?.name?.split(' ')[0]} <span className="heading-wave">✦</span></h1><p className="muted">Here is what is happening with your pipeline today.</p></div><button className="button button-primary" onClick={() => { setModalLead(null); setShowForm(true) }}><Plus size={17} /> Add lead</button></div>
          {error && <div role="alert" className="alert page-alert">{error}</div>}
          <section className="stats-grid" aria-label="Lead statistics">
            <Stat label="Total leads" value={stats?.total ?? '—'} tone="metric-total" icon={Users} detail={leadCountLabel} />
            <Stat label="New leads" value={stats?.new ?? '—'} tone="metric-new" icon={Sparkles} detail="Ready for outreach" />
            <Stat label="Contacted" value={stats?.contacted ?? '—'} tone="metric-contacted" icon={TrendingUp} detail="In active conversation" />
            <Stat label="Qualified" value={stats?.qualified ?? '—'} tone="metric-qualified" icon={Check} detail={`${conversionRate}% conversion rate`} />
          </section>
          <section className="insights-grid">
            <article className="insight-card conversion-card"><div className="card-title-row"><div><p className="eyebrow">PIPELINE HEALTH</p><h2>Conversion overview</h2></div><span className="trend-pill"><TrendingUp size={13} /> {conversionRate}%</span></div><div className="conversion-content"><Donut stats={stats} /><div className="legend">{[['Qualified', stats?.qualified || 0, '#7c6cff'], ['Contacted', stats?.contacted || 0, '#3fd6c7'], ['New', stats?.new || 0, '#f3b35d'], ['Lost', stats?.lost || 0, '#ef7180']].map(([label, value, color]) => <div key={label}><i style={{ background: color }} /><span>{label}</span><strong>{value}</strong></div>)}</div></div></article>
            <article className="insight-card focus-card"><div className="focus-glow" /><div className="card-title-row"><div><p className="eyebrow">TODAY'S FOCUS</p><h2>Keep the momentum</h2></div><Sparkles size={20} /></div><p className="focus-copy">You have <strong>{stats?.new || 0} new {stats?.new === 1 ? 'lead' : 'leads'}</strong> waiting for a first touch. A quick response can make all the difference.</p><button className="button button-quiet" onClick={() => { setStatus('New'); setPage(1) }}>View new leads <ArrowDownUp size={15} /></button></article>
          </section>
          <section className="leads-panel" id="leads">
            <div className="panel-heading"><div><div className="section-title"><h2>Recent leads</h2><span className="live-dot" /></div><p className="muted">Manage and follow up on your opportunities.</p></div><button className="text-button" onClick={() => { setStatus(''); setSearch('') }}>View all <ChevronRight size={15} /></button></div>
            <div className="toolbar"><label className="search-field"><Search size={17} /><input value={search} placeholder="Search leads by name…" onChange={(event) => { setPage(1); setSearch(event.target.value) }} /></label><select aria-label="Filter by status" className="filter-select" value={status} onChange={(event) => { setPage(1); setStatus(event.target.value) }}><option value="">All statuses</option>{STATUS_OPTIONS.map((item) => <option key={item}>{item}</option>)}</select><button className="button button-quiet sort-button" onClick={() => setSortOrder((current) => current === 'desc' ? 'asc' : 'desc')}><ArrowDownUp size={16} /> {sortOrder === 'desc' ? 'Newest' : 'Oldest'}</button></div>
            <div className="table-wrap"><table><thead><tr><th>Lead</th><th>Company</th><th>Source</th><th>Status</th><th>Added</th><th aria-label="Actions" /></tr></thead><tbody>
              {loading ? <tr><td colSpan="6" className="table-state"><span className="loading-pulse">Loading your leads…</span></td></tr> : pageData?.items.length ? pageData.items.map((lead) => <tr key={lead.id}><td><div className="lead-identity"><span className="lead-avatar">{lead.name.slice(0, 1).toUpperCase()}</span><div><strong>{lead.name}</strong><span>{lead.email}</span></div></div></td><td>{lead.company}</td><td>{lead.source}</td><td><select aria-label={`Status for ${lead.name}`} className={`status-select status-${lead.status.toLowerCase()}`} value={lead.status} onChange={(event) => changeStatus(lead, event.target.value)}>{STATUS_OPTIONS.map((item) => <option key={item}>{item}</option>)}</select></td><td className="date-cell">{new Date(lead.created_at).toLocaleDateString()}</td><td><div className="row-actions"><button className="icon-button" aria-label={`Edit ${lead.name}`} onClick={() => { setModalLead(lead); setShowForm(true) }}><Pencil size={16} /></button><button className="icon-button danger-icon" aria-label={`Delete ${lead.name}`} onClick={() => deleteLead(lead)}><Trash2 size={16} /></button></div></td></tr>) : <tr><td colSpan="6" className="table-state"><strong>No leads found</strong><span>{search || status ? 'Try adjusting your search or filters.' : 'Add your first lead to get started.'}</span></td></tr>}
            </tbody></table></div>
            {pageData?.total > 0 && <div className="pagination"><span>Showing {((page - 1) * pageData.limit) + 1}–{Math.min(page * pageData.limit, pageData.total)} of {pageData.total}</span><div><button className="icon-button" aria-label="Previous page" disabled={page <= 1} onClick={() => setPage((current) => current - 1)}><ChevronLeft size={18} /></button><span>Page {page} of {Math.max(pageData.pages, 1)}</span><button className="icon-button" aria-label="Next page" disabled={page >= pageData.pages} onClick={() => setPage((current) => current + 1)}><ChevronRight size={18} /></button></div></div>}
          </section>
          <footer className="workspace-footer">Built for better conversations <span>·</span> Leadflow</footer>
        </main>
      </div>
      {showForm && <LeadForm lead={modalLead} onClose={() => { setShowForm(false); setModalLead(null) }} onSaved={loadData} />}
    </div>
  )
}
