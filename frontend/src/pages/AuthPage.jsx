import { useState } from 'react'
import { ArrowRight, BriefcaseBusiness } from 'lucide-react'
import { Link, useNavigate } from 'react-router-dom'
import { getErrorMessage } from '../services/api'
import { useAuth } from '../context/AuthContext'

export default function AuthPage({ mode }) {
  const isRegister = mode === 'register'
  const { login, register } = useAuth()
  const navigate = useNavigate()
  const [form, setForm] = useState({ name: '', email: '', password: '' })
  const [error, setError] = useState('')
  const [busy, setBusy] = useState(false)

  async function submit(event) {
    event.preventDefault()
    setError('')
    if (isRegister && form.password.length < 12) {
      setError('Use at least 12 characters for your password.')
      return
    }
    setBusy(true)
    try {
      if (isRegister) await register(form)
      else await login({ email: form.email, password: form.password })
      navigate('/dashboard', { replace: true })
    } catch (requestError) {
      setError(getErrorMessage(requestError))
    } finally {
      setBusy(false)
    }
  }

  return (
    <main className="auth-page">
      <section className="auth-card">
        <div className="brand-mark"><BriefcaseBusiness size={22} /> Leadflow</div>
        <p className="eyebrow">{isRegister ? 'GET STARTED' : 'WELCOME BACK'}</p>
        <h1>{isRegister ? 'Create your account' : 'Sign in to your workspace'}</h1>
        <p className="auth-subtitle">
          {isRegister ? 'Keep every opportunity moving forward.' : 'Your leads and next steps, all in one place.'}
        </p>
        <form onSubmit={submit} className="auth-form">
          {isRegister && (
            <label>
              Full name
              <input autoComplete="name" required minLength="2" maxLength="100" value={form.name}
                onChange={(event) => setForm({ ...form, name: event.target.value })} />
            </label>
          )}
          <label>
            Work email
            <input type="email" autoComplete="email" required value={form.email}
              onChange={(event) => setForm({ ...form, email: event.target.value })} />
          </label>
          <label>
            Password
            <input type="password" autoComplete={isRegister ? 'new-password' : 'current-password'}
              minLength={isRegister ? 12 : 1} maxLength="128" required value={form.password}
              onChange={(event) => setForm({ ...form, password: event.target.value })} />
            {isRegister && <span className="field-note">At least 12 characters</span>}
          </label>
          {error && <div role="alert" className="alert">{error}</div>}
          <button className="button button-primary button-wide" disabled={busy}>
            {busy ? 'Please wait…' : isRegister ? 'Create account' : 'Sign in'}
            {!busy && <ArrowRight size={17} />}
          </button>
        </form>
        <p className="auth-switch">
          {isRegister ? 'Already have an account?' : 'New to Leadflow?'}
          {' '}<Link to={isRegister ? '/login' : '/register'}>{isRegister ? 'Sign in' : 'Create an account'}</Link>
        </p>
      </section>
      <aside className="auth-aside">
        <div>
          <span className="aside-kicker">A clearer path to close</span>
          <h2>Make every lead<br />count.</h2>
          <p>One calm, focused place to understand your pipeline and follow up with confidence.</p>
        </div>
        <span className="aside-footer">Simple pipeline management for growing teams.</span>
      </aside>
    </main>
  )
}
