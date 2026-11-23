import { useCallback, useEffect, useState } from 'react'
import { ArrowDownUp, BriefcaseBusiness, ChevronLeft, ChevronRight, CirclePlus, LogOut, Search, Trash2, UserRoundPen, X } from 'lucide-react'
import { useAuth } from '../context/AuthContext'
import { getErrorMessage } from '../services/api'
import { leadService } from '../services/leadService'

const STATUS_OPTIONS = ['New', 'Contacted', 'Qualified', 'Lost']
const SOURCES = ['Website', 'Referral', 'Social Media', 'Advertisement', 'Cold Call', 'Other']
const EMPTY_FORM = { name: '', email: '', phone: '', company: '', source: 'Website', status: 'New' }

function Stat({ label, value, tone }) {
  return <div className={`stat-card ${tone}`}><span>{label}</span><strong>{value}</strong></div>
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
          <div><p className="eyebrow">{lead ? 'LEAD DETAILS' : 'NEW OPPORTUNITY'}</p>
            <h2 id="lead-form-title">{lead ? 'Edit lead' : 'Add a lead'}</h2></div>
          <button className="icon-button" aria-label="Close form" onClick={onClose}><X size={19} /></button>
        </div>
        <form onSubmit={submit} className="lead-form">
          <label>Full name<input required minLength="2" maxLength="100" value={form.name} onChange={(event) => set('name', event.target.value)} /></label>
          <div className="form-grid">
            <label>Email<input type="email" required value={form.email} onChange={(event) => set('email', event.target.value)} /></label>
            <label>Phone<input type="tel" required minLength="7" maxLength="32" placeholder="+1 415 555 2671" value={form.phone} onChange={(event) => set('phone', event.target.value)} /></label>
          </div>
          <label>Company<input required maxLength="120" value={form.company} onChange={(event) => set('company', event.target.value)} /></label>
          <div className="form-grid">
            <label>Source<select value={form.source} onChange={(event) => set('source', event.target.value)}>{SOURCES.map((source) => <option key={source}>{source}</option>)}</select></label>
            <label>Status<select value={form.status} onChange={(event) => set('status', event.target.value)}>{STATUS_OPTIONS.map((status) => <option key={status}>{status}</option>)}</select></label>
          </div>
          {error && <div role="alert" className="alert">{error}</div>}
          <div className="modal-actions">
            <button type="button" className="button button-quiet" onClick={onClose}>Cancel</button>
            <button className="button button-primary" disabled={busy}>{busy ? 'Saving…' : lead ? 'Save changes' : 'Create lead'}</button>
          </div>
        </form>
      </section>
    </div>
  )
}

export default function DashboardPage() {
  const { user, signOut } = useAuth()
  const [stats, setStats] = useState(null)
  const [pageData, setPageData] = useState(null)
  const [page, setPage] = useState(1)
  const [search, setSearch] = useState('')
  const [status, setStatus] = useState('')
  const [sortOrder, setSortOrder] = useState('desc')
  const [modalLead, setModalLead] = useState(null)
  const [showForm, setShowForm] = useState(false)
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
    try {
      await leadService.updateStatus(lead.id, nextStatus)
      await loadData()
    } catch (requestError) {
      setError(getErrorMessage(requestError))
    }
  }

  async function deleteLead(lead) {
    if (!window.confirm(`Delete ${lead.name}'s lead? This cannot be undone.`)) return
    try {
      await leadService.remove(lead.id)
      await loadData()
    } catch (requestError) {
      setError(getErrorMessage(requestError))
    }
  }

  function closeForm() {
    setShowForm(false)
    setModalLead(null)
  }

  return (
    <div className="app-shell">
      <header className="topbar">
        <a href="/dashboard" className="brand-mark"><BriefcaseBusiness size={20} /> Leadflow</a>
        <div className="topbar-right">
          <div className="user-chip"><span className="avatar">{user?.name?.slice(0, 1).toUpperCase()}</span><span>{user?.name}</span></div>
          <button className="icon-button" aria-label="Sign out" title="Sign out" onClick={signOut}><LogOut size={18} /></button>
        </div>
      </header>
      <main className="workspace">
        <div className="page-heading">
          <div><p className="eyebrow">YOUR PIPELINE</p><h1>Good work starts here.</h1>
            <p className="muted">A clear view of your relationships and what comes next.</p></div>
          <button className="button button-primary" onClick={() => { setModalLead(null); setShowForm(true) }}><CirclePlus size={17} /> Add lead</button>
        </div>
        {error && <div role="alert" className="alert page-alert">{error}</div>}
        <section className="stats-grid" aria-label="Lead statistics">
          <Stat label="Total leads" value={stats?.total ?? '—'} tone="stat-total" />
          <Stat label="New" value={stats?.new ?? '—'} tone="stat-new" />
          <Stat label="Contacted" value={stats?.contacted ?? '—'} tone="stat-contacted" />
          <Stat label="Qualified" value={stats?.qualified ?? '—'} tone="stat-qualified" />
          <Stat label="Lost" value={stats?.lost ?? '—'} tone="stat-lost" />
        </section>
        <section className="leads-panel">
          <div className="panel-heading">
            <div><h2>Leads</h2><p className="muted">Manage and follow up on your opportunities.</p></div>
          </div>
          <div className="toolbar">
            <label className="search-field"><Search size={17} /><input value={search} placeholder="Search leads by name…" onChange={(event) => { setPage(1); setSearch(event.target.value) }} /></label>
            <select aria-label="Filter by status" className="filter-select" value={status} onChange={(event) => { setPage(1); setStatus(event.target.value) }}>
              <option value="">All statuses</option>{STATUS_OPTIONS.map((item) => <option key={item}>{item}</option>)}
            </select>
            <button className="button button-quiet sort-button" onClick={() => setSortOrder((current) => current === 'desc' ? 'asc' : 'desc')}><ArrowDownUp size={16} /> Date {sortOrder === 'desc' ? 'newest' : 'oldest'}</button>
          </div>
          <div className="table-wrap">
            <table>
              <thead><tr><th>Lead</th><th>Company</th><th>Source</th><th>Status</th><th>Added</th><th aria-label="Actions" /></tr></thead>
              <tbody>
                {loading ? <tr><td colSpan="6" className="table-state">Loading your leads…</td></tr>
                  : pageData?.items.length ? pageData.items.map((lead) => (
                    <tr key={lead.id}>
                      <td><div className="lead-identity"><span className="lead-avatar">{lead.name.slice(0, 1).toUpperCase()}</span><div><strong>{lead.name}</strong><span>{lead.email}</span></div></div></td>
                      <td>{lead.company}</td><td>{lead.source}</td>
                      <td><select aria-label={`Status for ${lead.name}`} className={`status-select status-${lead.status.toLowerCase()}`} value={lead.status} onChange={(event) => changeStatus(lead, event.target.value)}>{STATUS_OPTIONS.map((item) => <option key={item}>{item}</option>)}</select></td>
                      <td className="date-cell">{new Date(lead.created_at).toLocaleDateString()}</td>
                      <td><div className="row-actions">
                        <button className="icon-button" aria-label={`Edit ${lead.name}`} onClick={() => { setModalLead(lead); setShowForm(true) }}><UserRoundPen size={17} /></button>
                        <button className="icon-button danger-icon" aria-label={`Delete ${lead.name}`} onClick={() => deleteLead(lead)}><Trash2 size={17} /></button>
                      </div></td>
                    </tr>
                  )) : <tr><td colSpan="6" className="table-state"><strong>No leads found</strong><span>{search || status ? 'Try adjusting your search or filters.' : 'Add your first lead to get started.'}</span></td></tr>}
              </tbody>
            </table>
          </div>
          {pageData?.total > 0 && <div className="pagination">
            <span>Showing {((page - 1) * pageData.limit) + 1}–{Math.min(page * pageData.limit, pageData.total)} of {pageData.total}</span>
            <div><button className="icon-button" aria-label="Previous page" disabled={page <= 1} onClick={() => setPage((current) => current - 1)}><ChevronLeft size={18} /></button>
              <span>Page {page} of {Math.max(pageData.pages, 1)}</span>
              <button className="icon-button" aria-label="Next page" disabled={page >= pageData.pages} onClick={() => setPage((current) => current + 1)}><ChevronRight size={18} /></button></div>
          </div>}
        </section>
        <footer className="workspace-footer">Your pipeline, thoughtfully organized.</footer>
      </main>
      {showForm && <LeadForm lead={modalLead} onClose={closeForm} onSaved={loadData} />}
    </div>
  )
}
