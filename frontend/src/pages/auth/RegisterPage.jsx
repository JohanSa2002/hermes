import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import {
  MessageCircle, Building2, UserCircle, CheckCircle2,
  Eye, EyeOff, AlertCircle, ChevronRight, ChevronLeft, Info,
} from 'lucide-react'
import { useAuth } from '@/contexts/AuthContext'
import { cn, BUSINESS_TYPES, TIMEZONES } from '@/lib/utils'

const STEPS = [
  { id: 1, label: 'Tu negocio', description: 'Datos básicos del negocio' },
  { id: 2, label: 'Tu cuenta', description: 'Credenciales de acceso' },
  { id: 3, label: 'Listo', description: 'Confirmar registro' },
]

const INITIAL = {
  business_name: '',
  business_type: '',
  timezone: 'America/Bogota',
  email: '',
  password: '',
  confirm_password: '',
}

export default function RegisterPage() {
  const { register } = useAuth()
  const navigate = useNavigate()

  const [step, setStep] = useState(1)
  const [form, setForm] = useState(INITIAL)
  const [errors, setErrors] = useState({})
  const [showPwd, setShowPwd] = useState(false)
  const [showConfirm, setShowConfirm] = useState(false)
  const [loading, setLoading] = useState(false)
  const [globalError, setGlobalError] = useState('')

  function handleChange(e) {
    const { name, value } = e.target
    setForm((f) => ({ ...f, [name]: value }))
    setErrors((e) => ({ ...e, [name]: '' }))
    setGlobalError('')
  }

  function validateStep1() {
    const e = {}
    if (!form.business_name.trim()) e.business_name = 'Ingresa el nombre de tu negocio.'
    if (form.business_name.trim().length > 0 && form.business_name.trim().length < 3)
      e.business_name = 'El nombre debe tener al menos 3 caracteres.'
    if (!form.business_type) e.business_type = 'Selecciona el tipo de negocio.'
    return e
  }

  function validateStep2() {
    const e = {}
    if (!form.email) e.email = 'Ingresa tu correo electrónico.'
    else if (!/\S+@\S+\.\S+/.test(form.email)) e.email = 'El correo no tiene un formato válido.'
    if (!form.password) e.password = 'Crea una contraseña.'
    else if (form.password.length < 8) e.password = 'La contraseña debe tener al menos 8 caracteres.'
    if (form.password !== form.confirm_password) e.confirm_password = 'Las contraseñas no coinciden.'
    return e
  }

  function handleNext() {
    const errs = step === 1 ? validateStep1() : validateStep2()
    if (Object.keys(errs).length) { setErrors(errs); return }
    setStep((s) => s + 1)
  }

  async function handleSubmit() {
    setLoading(true)
    setGlobalError('')
    try {
      await register({
        business_name: form.business_name.trim(),
        business_type: form.business_type,
        timezone: form.timezone,
        email: form.email,
        password: form.password,
      })
      navigate('/dashboard')
    } catch (err) {
      const detail = err.response?.data?.detail
      if (detail === 'El correo ya está registrado') {
        setGlobalError('Este correo ya tiene una cuenta. ¿Quieres iniciar sesión?')
        setStep(2)
      } else {
        setGlobalError('Ocurrió un error al crear tu cuenta. Intenta de nuevo.')
      }
    } finally {
      setLoading(false)
    }
  }

  const businessTypeLabel = BUSINESS_TYPES.find((t) => t.value === form.business_type)?.label

  return (
    <div className="auth-bg min-h-screen flex items-center justify-center p-4">
      <div className="w-full max-w-md animate-slide-up">
        {/* Logo */}
        <div className="flex flex-col items-center gap-3 mb-6">
          <div className="w-12 h-12 rounded-2xl bg-primary-600 flex items-center justify-center shadow-lg">
            <MessageCircle size={24} className="text-white" />
          </div>
          <h1 className="font-display text-2xl font-bold text-slate-900">
            Hermes<span className="text-primary-600">Messages</span>
          </h1>
        </div>

        {/* Stepper */}
        <div className="flex items-center gap-0 mb-6 px-2">
          {STEPS.map((s, i) => (
            <div key={s.id} className="flex items-center flex-1">
              <div className="flex flex-col items-center gap-1 flex-shrink-0">
                <div
                  className={cn(
                    'w-8 h-8 rounded-full flex items-center justify-center text-sm font-semibold transition-all duration-200',
                    step > s.id
                      ? 'bg-primary-600 text-white'
                      : step === s.id
                        ? 'bg-primary-600 text-white ring-4 ring-primary-100'
                        : 'bg-white border-2 border-border text-slate-400',
                  )}
                >
                  {step > s.id ? <CheckCircle2 size={16} /> : s.id}
                </div>
                <span
                  className={cn(
                    'text-xs font-medium transition-colors duration-200 whitespace-nowrap',
                    step >= s.id ? 'text-primary-600' : 'text-slate-400',
                  )}
                >
                  {s.label}
                </span>
              </div>
              {i < STEPS.length - 1 && (
                <div
                  className={cn(
                    'flex-1 h-0.5 mx-2 mb-4 rounded-full transition-all duration-300',
                    step > s.id ? 'bg-primary-500' : 'bg-border',
                  )}
                />
              )}
            </div>
          ))}
        </div>

        {/* Card */}
        <div className="card p-6 shadow-dialog">
          {globalError && (
            <div className="flex items-start gap-2.5 bg-danger-50 border border-danger-100 rounded-lg px-3.5 py-3 mb-5 text-sm text-danger-700">
              <AlertCircle size={16} className="flex-shrink-0 mt-0.5" />
              <span>
                {globalError}{' '}
                {globalError.includes('iniciar sesión') && (
                  <Link to="/login" className="font-medium underline">Ingresar</Link>
                )}
              </span>
            </div>
          )}

          {/* ── Step 1: Negocio ── */}
          {step === 1 && (
            <div className="animate-fade-in">
              <div className="flex items-center gap-2 mb-1">
                <Building2 size={18} className="text-primary-600" />
                <h2 className="font-display text-lg font-semibold text-slate-900">
                  Datos de tu negocio
                </h2>
              </div>
              <p className="text-sm text-slate-500 mb-5">
                Esta información aparecerá en las conversaciones de tu bot de WhatsApp.
              </p>

              <div className="flex flex-col gap-4">
                <div className="field">
                  <label htmlFor="business_name" className="field-label field-label-required">
                    Nombre del negocio
                  </label>
                  <input
                    id="business_name"
                    name="business_name"
                    type="text"
                    autoComplete="organization"
                    placeholder="Ej: Restaurante La Terraza, Clínica Salud Plus…"
                    value={form.business_name}
                    onChange={handleChange}
                    className={cn('field-input', errors.business_name && 'field-input-error')}
                  />
                  {errors.business_name
                    ? <span className="field-error"><AlertCircle size={12} />{errors.business_name}</span>
                    : <span className="field-helper">Usa el nombre comercial tal como lo conocen tus clientes.</span>
                  }
                </div>

                <div className="field">
                  <label htmlFor="business_type" className="field-label field-label-required">
                    Tipo de negocio
                  </label>
                  <select
                    id="business_type"
                    name="business_type"
                    value={form.business_type}
                    onChange={handleChange}
                    className={cn('field-input', errors.business_type && 'field-input-error')}
                  >
                    <option value="" disabled>Selecciona una categoría…</option>
                    {BUSINESS_TYPES.map((t) => (
                      <option key={t.value} value={t.value}>{t.label}</option>
                    ))}
                  </select>
                  {errors.business_type
                    ? <span className="field-error"><AlertCircle size={12} />{errors.business_type}</span>
                    : <span className="field-helper">Ayuda al bot a personalizar las respuestas según tu industria.</span>
                  }
                </div>

                <div className="field">
                  <label htmlFor="timezone" className="field-label field-label-required">
                    Zona horaria
                  </label>
                  <select
                    id="timezone"
                    name="timezone"
                    value={form.timezone}
                    onChange={handleChange}
                    className="field-input"
                  >
                    {TIMEZONES.map((t) => (
                      <option key={t.value} value={t.value}>{t.label}</option>
                    ))}
                  </select>
                  <span className="field-helper">
                    Usada para mostrar y gestionar los horarios de reserva correctamente.
                  </span>
                </div>
              </div>
            </div>
          )}

          {/* ── Step 2: Cuenta ── */}
          {step === 2 && (
            <div className="animate-fade-in">
              <div className="flex items-center gap-2 mb-1">
                <UserCircle size={18} className="text-primary-600" />
                <h2 className="font-display text-lg font-semibold text-slate-900">
                  Crea tu cuenta
                </h2>
              </div>
              <p className="text-sm text-slate-500 mb-5">
                Estas credenciales son solo tuyas para acceder al panel de control.
              </p>

              <div className="flex flex-col gap-4">
                <div className="field">
                  <label htmlFor="email" className="field-label field-label-required">
                    Correo electrónico
                  </label>
                  <input
                    id="email"
                    name="email"
                    type="email"
                    autoComplete="email"
                    placeholder="tu@negocio.com"
                    value={form.email}
                    onChange={handleChange}
                    className={cn('field-input', errors.email && 'field-input-error')}
                  />
                  {errors.email
                    ? <span className="field-error"><AlertCircle size={12} />{errors.email}</span>
                    : <span className="field-helper">Aquí recibirás notificaciones importantes de la plataforma.</span>
                  }
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
                      autoComplete="new-password"
                      placeholder="Mínimo 8 caracteres"
                      value={form.password}
                      onChange={handleChange}
                      className={cn('field-input pr-10', errors.password && 'field-input-error')}
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
                  {errors.password
                    ? <span className="field-error"><AlertCircle size={12} />{errors.password}</span>
                    : (
                      <span className="field-helper">
                        Usa al menos 8 caracteres. Combina letras y números para mayor seguridad.
                      </span>
                    )
                  }
                </div>

                <div className="field">
                  <label htmlFor="confirm_password" className="field-label field-label-required">
                    Confirmar contraseña
                  </label>
                  <div className="relative">
                    <input
                      id="confirm_password"
                      name="confirm_password"
                      type={showConfirm ? 'text' : 'password'}
                      autoComplete="new-password"
                      placeholder="Repite tu contraseña"
                      value={form.confirm_password}
                      onChange={handleChange}
                      className={cn('field-input pr-10', errors.confirm_password && 'field-input-error')}
                    />
                    <button
                      type="button"
                      onClick={() => setShowConfirm((v) => !v)}
                      className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-600 transition-colors"
                      aria-label={showConfirm ? 'Ocultar' : 'Mostrar'}
                    >
                      {showConfirm ? <EyeOff size={16} /> : <Eye size={16} />}
                    </button>
                  </div>
                  {errors.confirm_password
                    ? <span className="field-error"><AlertCircle size={12} />{errors.confirm_password}</span>
                    : <span className="field-helper">Escribe exactamente la misma contraseña para confirmarla.</span>
                  }
                </div>
              </div>
            </div>
          )}

          {/* ── Step 3: Confirmar ── */}
          {step === 3 && (
            <div className="animate-fade-in">
              <div className="flex items-center gap-2 mb-1">
                <CheckCircle2 size={18} className="text-primary-600" />
                <h2 className="font-display text-lg font-semibold text-slate-900">
                  Confirma tu registro
                </h2>
              </div>
              <p className="text-sm text-slate-500 mb-5">
                Revisa los datos antes de crear tu cuenta.
              </p>

              <div className="bg-slate-50 rounded-xl border border-border divide-y divide-border mb-2">
                <div className="px-4 py-3 flex items-center justify-between gap-3">
                  <span className="text-sm text-slate-500">Negocio</span>
                  <span className="text-sm font-medium text-slate-900 text-right">{form.business_name}</span>
                </div>
                <div className="px-4 py-3 flex items-center justify-between gap-3">
                  <span className="text-sm text-slate-500">Tipo</span>
                  <span className="text-sm font-medium text-slate-900">{businessTypeLabel}</span>
                </div>
                <div className="px-4 py-3 flex items-center justify-between gap-3">
                  <span className="text-sm text-slate-500">Zona horaria</span>
                  <span className="text-sm font-medium text-slate-900">
                    {TIMEZONES.find((t) => t.value === form.timezone)?.label}
                  </span>
                </div>
                <div className="px-4 py-3 flex items-center justify-between gap-3">
                  <span className="text-sm text-slate-500">Correo</span>
                  <span className="text-sm font-medium text-slate-900 truncate max-w-[180px]">{form.email}</span>
                </div>
              </div>

              <div className="flex items-start gap-2 bg-primary-50 rounded-lg px-3.5 py-3 text-xs text-primary-700 mt-3">
                <Info size={13} className="flex-shrink-0 mt-0.5" />
                <span>
                  Tu cuenta se crea en plan gratuito. Podrás conectar WhatsApp y configurar
                  horarios desde el panel de control.
                </span>
              </div>
            </div>
          )}

          {/* Botones de navegación */}
          <div className={cn('flex gap-3 mt-6', step > 1 ? 'justify-between' : 'justify-end')}>
            {step > 1 && (
              <button
                type="button"
                onClick={() => setStep((s) => s - 1)}
                disabled={loading}
                className="btn-secondary flex items-center gap-1.5"
              >
                <ChevronLeft size={15} />
                Atrás
              </button>
            )}

            {step < 3 ? (
              <button
                type="button"
                onClick={handleNext}
                className="btn-primary flex items-center gap-1.5"
              >
                Siguiente
                <ChevronRight size={15} />
              </button>
            ) : (
              <button
                type="button"
                onClick={handleSubmit}
                disabled={loading}
                className="btn-primary flex-1 flex items-center justify-center gap-2"
              >
                {loading ? (
                  <span className="w-4 h-4 rounded-full border-2 border-white border-t-transparent animate-spin" />
                ) : (
                  <>
                    <CheckCircle2 size={15} />
                    Crear mi cuenta
                  </>
                )}
              </button>
            )}
          </div>
        </div>

        <p className="text-center text-sm text-slate-500 mt-5">
          ¿Ya tienes cuenta?{' '}
          <Link to="/login" className="text-primary-600 font-medium hover:underline">
            Iniciar sesión
          </Link>
        </p>
      </div>
    </div>
  )
}
