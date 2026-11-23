import { Link } from 'react-router-dom'

export default function NotFoundPage() {
  return (
    <main className="not-found">
      <p className="eyebrow">404 — NOT FOUND</p>
      <h1>This page isn't here.</h1>
      <Link to="/" className="button button-primary">Back to home</Link>
    </main>
  )
}
