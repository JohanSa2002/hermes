import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { MessageCircle, Eye, EyeOff, AlertCircle } from 'lucide-react'
import { useAuth } from '@/contexts/AuthContext'
import { cn } from '@/lib/utils'

export default function LoginPage() {
  const { login } = useAuth()
  const navigate = useNavigate()

  const [form, setForm] = useState({ email: '', password: '' })
  const [showPwd, setShowPwd] = useState(false)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  function handleChange(e) {
    setForm((f) => ({ ...f, [e.target.name]: e.target.value }))
    setError('')
  }

  async function handleSubmit(e) {
    e.preventDefault()
    setLoading(true)
    setError('')
    try {
      await login(form.email, form.password)
      navigate('/dashboard')
    } catch (err) {
      setError(
        err.response?.data?.detail === 'Credenciales incorrectas'
          ? 'Correo o contraseña incorrectos. Verifica e intenta de nuevo.'
          : 'Ocurrió un error. Intenta de nuevo.'
      )
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="auth-bg min-h-screen flex items-center justify-center p-4">
      <div className="w-full max-w-sm animate-slide-up">
        {/* Logo */}
        <div className="flex flex-col items-center gap-3 mb-8">
          <div className="w-12 h-12 rounded-2xl bg-primary-600 flex items-center justify-center shadow-lg">
            <MessageCircle size={24} className="text-white" />
          </div>
          <div className="text-center">
            <h1 className="font-display text-2xl font-bold text-slate-900">
              Hermes<span className="text-primary-600">Messages</span>
            </h1>
            <p className="text-sm text-slate-500 mt-1">Reservas automáticas por WhatsApp</p>
          </div>
        </div>

        {/* Card */}
        <div className="card p-6 shadow-dialog">
          <h2 className="font-display text-lg font-semibold text-slate-900 mb-1">
            Bienvenido de vuelta
          </h2>
          <p className="text-sm text-slate-500 mb-6">Ingresa a tu panel de control</p>

          {error && (
            <div className="flex items-start gap-2.5 bg-danger-50 border border-danger-100 rounded-lg px-3.5 py-3 mb-5 text-sm text-danger-700">
              <AlertCircle size={16} className="flex-shrink-0 mt-0.5" />
              <span>{error}</span>
            </div>
          )}

          <form onSubmit={handleSubmit} className="flex flex-col gap-4" noValidate>
            <div className="field">
              <label htmlFor="email" className="field-label field-label-required">
                Correo electrónico
              </label>
              <input
                id="email"
                name="email"
                type="email"
                autoComplete="email"
                required
                placeholder="tu@negocio.com"
                value={form.email}
                onChange={handleChange}
                className="field-input"
              />
            </div>

            <div className="field">
              <label htmlFor="password" className="field-label field-label-required">
                Contraseña
              </label>
              <div className="relative">
                <input
                  id="password"
                  name="password"
                  type={showPwd ? 'text' : 'password'}
                  autoComplete="current-password"
                  required
                  placeholder="Tu contraseña"
                  value={form.password}
                  onChange={handleChange}
                  className="field-input pr-10"
                />
                <button
                  type="button"
                  onClick={() => setShowPwd((v) => !v)}
                  className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-600 transition-colors"
                  aria-label={showPwd ? 'Ocultar contraseña' : 'Mostrar contraseña'}
                >
                  {showPwd ? <EyeOff size={16} /> : <Eye size={16} />}
                </button>
              </div>
            </div>

            <button
              type="submit"
              disabled={loading || !form.email || !form.password}
              className="btn-primary w-full mt-1"
            >
              {loading ? (
                <span className="w-4 h-4 rounded-full border-2 border-white border-t-transparent animate-spin" />
              ) : (
                'Ingresar'
              )}
            </button>
          </form>
        </div>

        <p className="text-center text-sm text-slate-500 mt-5">
          ¿No tienes cuenta?{' '}
          <Link to="/register" className="text-primary-600 font-medium hover:underline">
            Regístrate gratis
          </Link>
        </p>
      </div>
    </div>
  )
}
