import { useState, useEffect } from 'react'
import { Save, CheckCircle, AlertCircle, Wifi, WifiOff, ExternalLink } from 'lucide-react'
import { businessApi, whatsappApi } from '@/lib/api'
import { DAYS_FULL, cn } from '@/lib/utils'

const TONE_OPTIONS = [
  { value: 'formal', label: 'Formal', desc: 'Tono profesional y respetuoso' },
  { value: 'casual', label: 'Casual', desc: 'Tono amigable y cercano' },
]

function Section({ title, description, children }) {
  return (
    <div className="card p-6 flex flex-col gap-5">
      <div className="border-b border-border pb-4">
        <h3 className="font-display text-base font-semibold text-slate-900">{title}</h3>
        {description && <p className="text-sm text-slate-500 mt-0.5">{description}</p>}
      </div>
      {children}
    </div>
  )
}

export default function ConfigPage() {
  const [business, setBusiness] = useState(null)
  const [config, setConfig] = useState(null)
  const [waStatus, setWaStatus] = useState(null)
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)
  const [saved, setSaved] = useState(false)
  const [error, setError] = useState('')

  useEffect(() => {
    async function load() {
      try {
        const [bRes, cRes, wRes] = await Promise.all([
          businessApi.getMe(),
          businessApi.getConfig(),
          whatsappApi.getStatus().catch(() => ({ data: null })),
        ])
        setBusiness(bRes.data)
        setConfig(cRes.data)
        setWaStatus(wRes.data)
      } finally {
        setLoading(false)
      }
    }
    load()
  }, [])

  function updateConfig(key, val) {
    setConfig((c) => ({ ...c, [key]: val }))
    setSaved(false)
    setError('')
  }

  function toggleDay(day) {
    const days = config.open_days ?? []
    const next = days.includes(day) ? days.filter((d) => d !== day) : [...days, day].sort()
    updateConfig('open_days', next)
  }

  async function handleSave() {
    setSaving(true)
    setError('')
    try {
      await Promise.all([
        businessApi.updateMe({ name: business.name, timezone: business.timezone }),
        businessApi.updateConfig({
          open_days: config.open_days,
          open_time: config.open_time,
          close_time: config.close_time,
          slot_duration: config.slot_duration,
          max_per_slot: config.max_per_slot,
          assistant_name: config.assistant_name,
          tone: config.tone,
          welcome_message: config.welcome_message,
        }),
      ])
      setSaved(true)
      setTimeout(() => setSaved(false), 3000)
    } catch {
      setError('No se pudo guardar la configuración. Intenta de nuevo.')
    } finally {
      setSaving(false)
    }
  }

  if (loading) {
    return (
      <div className="flex flex-col gap-5 max-w-2xl">
        {Array.from({ length: 3 }).map((_, i) => (
          <div key={i} className="card p-6">
            <div className="skeleton h-5 w-40 rounded mb-4" />
            <div className="flex flex-col gap-3">
              <div className="skeleton h-10 rounded-lg" />
              <div className="skeleton h-10 rounded-lg" />
            </div>
          </div>
        ))}
      </div>
    )
  }

  const isWaConnected = Boolean(waStatus?.whatsapp_phone_number_id)

  return (
    <div className="flex flex-col gap-5 max-w-2xl animate-fade-in">
      {/* WhatsApp status */}
      <div className={cn(
        'card p-5 flex items-center gap-4',
        isWaConnected ? 'border-primary-200 bg-primary-50' : 'border-warning-200 bg-warning-50',
      )}>
        <div className={cn(
          'w-10 h-10 rounded-xl flex items-center justify-center flex-shrink-0',
          isWaConnected ? 'bg-primary-100' : 'bg-warning-100',
        )}>
          {isWaConnected
            ? <Wifi size={18} className="text-primary-600" />
            : <WifiOff size={18} className="text-warning-600" />
          }
        </div>
        <div className="flex-1">
          <p className={cn('text-sm font-semibold', isWaConnected ? 'text-primary-800' : 'text-warning-800')}>
            WhatsApp {isWaConnected ? 'conectado' : 'no conectado'}
          </p>
          <p className={cn('text-xs mt-0.5', isWaConnected ? 'text-primary-600' : 'text-warning-600')}>
            {isWaConnected
              ? `Número: ${waStatus.whatsapp_phone_number_id}`
              : 'Configura tu número de WhatsApp Business para recibir reservas.'}
          </p>
        </div>
      </div>

      {/* Negocio */}
      <Section title="Datos del negocio" description="Nombre y zona horaria visible en el panel.">
        <div className="field">
          <label className="field-label field-label-required">Nombre del negocio</label>
          <input
            type="text"
            value={business?.name ?? ''}
            onChange={(e) => setBusiness((b) => ({ ...b, name: e.target.value }))}
            className="field-input"
            placeholder="Nombre de tu negocio"
          />
          <span className="field-helper">Nombre que ven tus clientes en los mensajes del bot.</span>
        </div>
      </Section>

      {/* Horarios */}
      <Section
        title="Horarios de atención"
        description="Define cuándo está disponible tu negocio para reservas."
      >
        {/* Días de la semana */}
        <div className="field">
          <label className="field-label field-label-required">Días de atención</label>
          <div className="flex flex-wrap gap-2 mt-1">
            {DAYS_FULL.map((day, idx) => {
              const open = config?.open_days?.includes(idx)
              return (
                <button
                  key={idx}
                  type="button"
                  onClick={() => toggleDay(idx)}
                  className={cn(
                    'btn px-3.5 py-2 text-xs font-medium transition-all duration-150',
                    open
                      ? 'bg-primary-600 text-white hover:bg-primary-700'
                      : 'bg-white border border-border text-slate-600 hover:bg-slate-50',
                  )}
                  aria-pressed={open}
                >
                  {day.slice(0, 3)}
                </button>
              )
            })}
          </div>
          <span className="field-helper">El bot solo aceptará reservas en los días marcados.</span>
        </div>

        {/* Horario */}
        <div className="grid grid-cols-2 gap-4">
          <div className="field">
            <label className="field-label field-label-required">Hora de apertura</label>
            <input
              type="time"
              value={config?.open_time ?? '09:00'}
              onChange={(e) => updateConfig('open_time', e.target.value)}
              className="field-input"
            />
            <span className="field-helper">Primera hora disponible para reservas.</span>
          </div>
          <div className="field">
            <label className="field-label field-label-required">Hora de cierre</label>
            <input
              type="time"
              value={config?.close_time ?? '18:00'}
              onChange={(e) => updateConfig('close_time', e.target.value)}
              className="field-input"
            />
            <span className="field-helper">Última hora en que se generan turnos.</span>
          </div>
        </div>

        {/* Duración y máximo */}
        <div className="grid grid-cols-2 gap-4">
          <div className="field">
            <label className="field-label field-label-required">Duración del turno (min)</label>
            <input
              type="number"
              min={15}
              max={240}
              step={15}
              value={config?.slot_duration ?? 60}
              onChange={(e) => updateConfig('slot_duration', Number(e.target.value))}
              className="field-input"
            />
            <span className="field-helper">Tiempo que dura cada cita o reserva.</span>
          </div>
          <div className="field">
            <label className="field-label field-label-required">Máximo por turno</label>
            <input
              type="number"
              min={1}
              max={50}
              value={config?.max_per_slot ?? 1}
              onChange={(e) => updateConfig('max_per_slot', Number(e.target.value))}
              className="field-input"
            />
            <span className="field-helper">Cuántas reservas se aceptan en el mismo horario.</span>
          </div>
        </div>
      </Section>

      {/* Bot */}
      <Section
        title="Configuración del asistente"
        description="Personaliza cómo se presenta el bot a tus clientes."
      >
        <div className="field">
          <label className="field-label field-label-required">Nombre del asistente</label>
          <input
            type="text"
            value={config?.assistant_name ?? ''}
            onChange={(e) => updateConfig('assistant_name', e.target.value)}
            className="field-input"
            placeholder="Ej: Hermes, María, Asistente…"
          />
          <span className="field-helper">
            Nombre con el que el bot se presentará: "Hola, soy <strong>{config?.assistant_name || 'Hermes'}</strong>…"
          </span>
        </div>

        <div className="field">
          <label className="field-label">Tono de comunicación</label>
          <div className="grid grid-cols-2 gap-2 mt-1">
            {TONE_OPTIONS.map((t) => {
              const active = config?.tone === t.value
              return (
                <button
                  key={t.value}
                  type="button"
                  onClick={() => updateConfig('tone', t.value)}
                  className={cn(
                    'flex flex-col items-start px-4 py-3.5 rounded-xl border text-left transition-all duration-150',
                    active
                      ? 'border-primary-500 bg-primary-50 text-primary-700'
                      : 'border-border bg-white text-slate-700 hover:bg-slate-50',
                  )}
                  aria-pressed={active}
                >
                  <span className="text-sm font-semibold">{t.label}</span>
                  <span className="text-xs mt-0.5 opacity-70">{t.desc}</span>
                </button>
              )
            })}
          </div>
        </div>

        <div className="field">
          <label className="field-label">Mensaje de bienvenida</label>
          <textarea
            rows={3}
            value={config?.welcome_message ?? ''}
            onChange={(e) => updateConfig('welcome_message', e.target.value)}
            className="field-input resize-none"
            placeholder="Ej: ¡Bienvenido! ¿En qué fecha y hora te gustaría reservar?"
          />
          <span className="field-helper">
            Primer mensaje que el bot envía al iniciar una conversación. Déjalo vacío para usar el mensaje predeterminado.
          </span>
        </div>
      </Section>

      {/* Footer guardado */}
      {error && (
        <div className="flex items-center gap-2 text-sm text-danger-700 bg-danger-50 border border-danger-100 rounded-lg px-4 py-3">
          <AlertCircle size={15} />
          {error}
        </div>
      )}

      <div className="flex items-center justify-between pb-4">
        {saved && (
          <div className="flex items-center gap-2 text-sm text-primary-700 animate-fade-in">
            <CheckCircle size={15} />
            Configuración guardada
          </div>
        )}
        <div className="ml-auto">
          <button
            onClick={handleSave}
            disabled={saving}
            className="btn-primary gap-2"
          >
            {saving
              ? <span className="w-4 h-4 rounded-full border-2 border-white border-t-transparent animate-spin" />
              : <Save size={15} />
            }
            {saving ? 'Guardando…' : 'Guardar cambios'}
          </button>
        </div>
      </div>
    </div>
  )
}
