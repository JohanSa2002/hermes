import { useState, useEffect } from 'react'
import { Save, CheckCircle, AlertCircle, Wifi, WifiOff, Phone, Unplug, UtensilsCrossed, Plus, Trash2, Pencil, Tag } from 'lucide-react'
import { businessApi, whatsappApi, tableApi, serviceApi } from '@/lib/api'
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

const WA_EMPTY = { phone_number_id: '', access_token: '', meta_business_id: '' }

export default function ConfigPage() {
  const [business, setBusiness] = useState(null)
  const [config, setConfig] = useState(null)
  const [waStatus, setWaStatus] = useState(null)
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)
  const [saved, setSaved] = useState(false)
  const [error, setError] = useState('')

  const [waForm, setWaForm] = useState(WA_EMPTY)
  const [waConnecting, setWaConnecting] = useState(false)
  const [waDisconnecting, setWaDisconnecting] = useState(false)
  const [waError, setWaError] = useState('')
  const [waShowForm, setWaShowForm] = useState(false)

  const SERVICE_EMPTY = { name: '', description: '', price: '', duration_minutes: '' }
  const [svcList, setSvcList] = useState([])
  const [svcForm, setSvcForm] = useState(SERVICE_EMPTY)
  const [editingSvc, setEditingSvc] = useState(null)
  const [svcError, setSvcError] = useState('')
  const [svcSaving, setSvcSaving] = useState(false)
  const [showSvcForm, setShowSvcForm] = useState(false)

  const TABLE_EMPTY = { capacity: '', quantity: '', label: '' }
  const [tables, setTables] = useState([])
  const [tableForm, setTableForm] = useState(TABLE_EMPTY)
  const [editingTable, setEditingTable] = useState(null)
  const [tableError, setTableError] = useState('')
  const [tableSaving, setTableSaving] = useState(false)
  const [showTableForm, setShowTableForm] = useState(false)

  useEffect(() => {
    async function load() {
      try {
        const [bRes, cRes, wRes, tRes, sRes] = await Promise.all([
          businessApi.getMe(),
          businessApi.getConfig(),
          whatsappApi.getStatus().catch(() => ({ data: null })),
          tableApi.list().catch(() => ({ data: [] })),
          serviceApi.list().catch(() => ({ data: [] })),
        ])
        setBusiness(bRes.data)
        setConfig(cRes.data)
        setWaStatus(wRes.data)
        setTables(tRes.data ?? [])
        setSvcList(sRes.data ?? [])
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

  function startEditSvc(svc) {
    setEditingSvc(svc.id)
    setSvcForm({
      name: svc.name,
      description: svc.description ?? '',
      price: svc.price != null ? svc.price : '',
      duration_minutes: svc.duration_minutes ?? '',
    })
    setShowSvcForm(true)
    setSvcError('')
  }

  function cancelSvcForm() {
    setEditingSvc(null)
    setSvcForm(SERVICE_EMPTY)
    setShowSvcForm(false)
    setSvcError('')
  }

  async function handleSvcSubmit(e) {
    e.preventDefault()
    if (!svcForm.name.trim()) { setSvcError('El nombre es requerido.'); return }
    setSvcSaving(true)
    setSvcError('')
    try {
      const payload = {
        name: svcForm.name.trim(),
        description: svcForm.description.trim() || null,
        price: svcForm.price !== '' ? Number(svcForm.price) : null,
        duration_minutes: svcForm.duration_minutes !== '' ? Number(svcForm.duration_minutes) : null,
      }
      if (editingSvc) {
        const { data } = await serviceApi.update(editingSvc, payload)
        setSvcList((l) => l.map((x) => (x.id === editingSvc ? data : x)))
      } else {
        const { data } = await serviceApi.create(payload)
        setSvcList((l) => [...l, data].sort((a, b) => a.name.localeCompare(b.name)))
      }
      cancelSvcForm()
    } catch {
      setSvcError('No se pudo guardar. Intenta de nuevo.')
    } finally {
      setSvcSaving(false)
    }
  }

  async function handleDeleteSvc(id) {
    if (!confirm('¿Eliminar este servicio?')) return
    try {
      await serviceApi.remove(id)
      setSvcList((l) => l.filter((x) => x.id !== id))
    } catch {
      // silencioso
    }
  }

  function startEditTable(table) {
    setEditingTable(table.id)
    setTableForm({ capacity: table.capacity, quantity: table.quantity, label: table.label ?? '' })
    setShowTableForm(true)
    setTableError('')
  }

  function cancelTableForm() {
    setEditingTable(null)
    setTableForm(TABLE_EMPTY)
    setShowTableForm(false)
    setTableError('')
  }

  async function handleTableSubmit(e) {
    e.preventDefault()
    if (!tableForm.capacity || !tableForm.quantity) {
      setTableError('Capacidad y cantidad son requeridas.')
      return
    }
    setTableSaving(true)
    setTableError('')
    try {
      const payload = {
        capacity: Number(tableForm.capacity),
        quantity: Number(tableForm.quantity),
        label: tableForm.label || null,
      }
      if (editingTable) {
        const { data } = await tableApi.update(editingTable, payload)
        setTables((t) => t.map((x) => (x.id === editingTable ? data : x)))
      } else {
        const { data } = await tableApi.create(payload)
        setTables((t) => [...t, data].sort((a, b) => a.capacity - b.capacity))
      }
      cancelTableForm()
    } catch {
      setTableError('No se pudo guardar. Intenta de nuevo.')
    } finally {
      setTableSaving(false)
    }
  }

  async function handleDeleteTable(id) {
    if (!confirm('¿Eliminar este tipo de mesa?')) return
    try {
      await tableApi.remove(id)
      setTables((t) => t.filter((x) => x.id !== id))
    } catch {
      // silencioso
    }
  }

  async function handleWaConnect(e) {
    e.preventDefault()
    setWaConnecting(true)
    setWaError('')
    try {
      await whatsappApi.connect(waForm)
      const { data } = await whatsappApi.getStatus()
      setWaStatus(data)
      setWaForm(WA_EMPTY)
      setWaShowForm(false)
    } catch {
      setWaError('No se pudo conectar. Verifica los datos e intenta de nuevo.')
    } finally {
      setWaConnecting(false)
    }
  }

  async function handleWaDisconnect() {
    if (!confirm('¿Desconectar WhatsApp? El bot dejará de responder mensajes.')) return
    setWaDisconnecting(true)
    try {
      await whatsappApi.disconnect()
      setWaStatus({ connected: false, phone_number_id: null, meta_business_id: null })
    } finally {
      setWaDisconnecting(false)
    }
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
      {/* WhatsApp */}
      <Section
        title="WhatsApp Business"
        description="Conecta tu número para que el bot reciba y responda reservas."
      >
        {/* Estado */}
        <div className={cn(
          'flex items-center gap-4 rounded-xl px-4 py-3.5 border',
          isWaConnected ? 'bg-primary-50 border-primary-200' : 'bg-warning-50 border-warning-200',
        )}>
          <div className={cn(
            'w-9 h-9 rounded-lg flex items-center justify-center flex-shrink-0',
            isWaConnected ? 'bg-primary-100' : 'bg-warning-100',
          )}>
            {isWaConnected
              ? <Wifi size={16} className="text-primary-600" />
              : <WifiOff size={16} className="text-warning-600" />
            }
          </div>
          <div className="flex-1">
            <p className={cn('text-sm font-semibold', isWaConnected ? 'text-primary-800' : 'text-warning-800')}>
              {isWaConnected ? 'Conectado' : 'Sin conectar'}
            </p>
            <p className={cn('text-xs mt-0.5', isWaConnected ? 'text-primary-600' : 'text-warning-600')}>
              {isWaConnected
                ? `Phone Number ID: ${waStatus.phone_number_id}`
                : 'El bot no puede recibir mensajes hasta que conectes un número.'}
            </p>
          </div>
          {isWaConnected ? (
            <button
              onClick={handleWaDisconnect}
              disabled={waDisconnecting}
              className="btn border border-border bg-white text-slate-700 hover:bg-slate-50 px-3 py-2 text-xs gap-1.5 flex-shrink-0"
            >
              {waDisconnecting
                ? <span className="w-3.5 h-3.5 rounded-full border-2 border-current border-t-transparent animate-spin block" />
                : <Unplug size={13} />
              }
              Desconectar
            </button>
          ) : (
            <button
              onClick={() => setWaShowForm((v) => !v)}
              className="btn-primary px-3 py-2 text-xs gap-1.5 flex-shrink-0"
            >
              <Phone size={13} />
              {waShowForm ? 'Cancelar' : 'Conectar'}
            </button>
          )}
        </div>

        {/* Formulario de conexión */}
        {!isWaConnected && waShowForm && (
          <form onSubmit={handleWaConnect} className="flex flex-col gap-4 pt-1 animate-fade-in">
            <div className="field">
              <label className="field-label field-label-required">Phone Number ID</label>
              <input
                type="text"
                required
                value={waForm.phone_number_id}
                onChange={(e) => setWaForm((f) => ({ ...f, phone_number_id: e.target.value }))}
                className="field-input font-mono"
                placeholder="123456789012345"
              />
              <span className="field-helper">
                Encuéntralo en Meta for Developers → Tu app → WhatsApp → Configuración de API.
              </span>
            </div>

            <div className="field">
              <label className="field-label field-label-required">Meta Business ID</label>
              <input
                type="text"
                required
                value={waForm.meta_business_id}
                onChange={(e) => setWaForm((f) => ({ ...f, meta_business_id: e.target.value }))}
                className="field-input font-mono"
                placeholder="987654321098765"
              />
              <span className="field-helper">
                ID de tu cuenta de Meta Business Suite.
              </span>
            </div>

            <div className="field">
              <label className="field-label field-label-required">Access Token</label>
              <input
                type="password"
                required
                value={waForm.access_token}
                onChange={(e) => setWaForm((f) => ({ ...f, access_token: e.target.value }))}
                className="field-input font-mono"
                placeholder="EAAxxxxxxxxx…"
              />
              <span className="field-helper">
                Token de acceso permanente generado en Meta for Developers.
              </span>
            </div>

            {waError && (
              <div className="flex items-center gap-2 text-sm text-danger-700 bg-danger-50 border border-danger-100 rounded-lg px-4 py-3">
                <AlertCircle size={14} />
                {waError}
              </div>
            )}

            <div className="flex justify-end">
              <button type="submit" disabled={waConnecting} className="btn-primary gap-2">
                {waConnecting
                  ? <span className="w-4 h-4 rounded-full border-2 border-white border-t-transparent animate-spin" />
                  : <Wifi size={15} />
                }
                {waConnecting ? 'Conectando…' : 'Conectar WhatsApp'}
              </button>
            </div>
          </form>
        )}
      </Section>

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

      {/* Mesas — solo restaurantes */}
      {business?.type === 'restaurant' && (
        <Section
          title="Configuración de mesas"
          description="Define los tipos de mesa disponibles. El bot usará esta información para asignar la mesa correcta según el tamaño del grupo."
        >
          {/* Lista de mesas */}
          {tables.length > 0 && (
            <div className="flex flex-col gap-2">
              {tables.map((t) => (
                <div
                  key={t.id}
                  className="flex items-center gap-3 px-4 py-3 rounded-xl border border-border bg-slate-50"
                >
                  <UtensilsCrossed size={16} className="text-slate-400 flex-shrink-0" />
                  <div className="flex-1">
                    <p className="text-sm font-medium text-slate-800">
                      {t.quantity} mesa{t.quantity > 1 ? 's' : ''} para {t.capacity} persona{t.capacity > 1 ? 's' : ''}
                    </p>
                    {t.label && <p className="text-xs text-slate-400 mt-0.5">{t.label}</p>}
                  </div>
                  <button
                    onClick={() => startEditTable(t)}
                    className="btn-ghost p-1.5 text-slate-400 hover:text-slate-600"
                    aria-label="Editar"
                  >
                    <Pencil size={14} />
                  </button>
                  <button
                    onClick={() => handleDeleteTable(t.id)}
                    className="btn-ghost p-1.5 text-slate-400 hover:text-danger-600"
                    aria-label="Eliminar"
                  >
                    <Trash2 size={14} />
                  </button>
                </div>
              ))}
            </div>
          )}

          {tables.length === 0 && !showTableForm && (
            <div className="flex flex-col items-center justify-center py-6 text-center border border-dashed border-border rounded-xl">
              <UtensilsCrossed size={24} className="text-slate-200 mb-2" />
              <p className="text-sm text-slate-400">No hay tipos de mesa configurados</p>
              <p className="text-xs text-slate-300 mt-0.5">Agrega tus mesas para un control preciso de reservas</p>
            </div>
          )}

          {/* Formulario */}
          {showTableForm && (
            <form onSubmit={handleTableSubmit} className="flex flex-col gap-4 p-4 rounded-xl border border-primary-200 bg-primary-50 animate-fade-in">
              <p className="text-sm font-semibold text-primary-800">
                {editingTable ? 'Editar tipo de mesa' : 'Agregar tipo de mesa'}
              </p>
              <div className="grid grid-cols-2 gap-3">
                <div className="field">
                  <label className="field-label field-label-required">Capacidad (personas)</label>
                  <input
                    type="number"
                    min={1}
                    max={50}
                    required
                    value={tableForm.capacity}
                    onChange={(e) => setTableForm((f) => ({ ...f, capacity: e.target.value }))}
                    className="field-input"
                    placeholder="Ej: 4"
                  />
                </div>
                <div className="field">
                  <label className="field-label field-label-required">Cantidad de mesas</label>
                  <input
                    type="number"
                    min={1}
                    max={200}
                    required
                    value={tableForm.quantity}
                    onChange={(e) => setTableForm((f) => ({ ...f, quantity: e.target.value }))}
                    className="field-input"
                    placeholder="Ej: 5"
                  />
                </div>
              </div>
              <div className="field">
                <label className="field-label">Etiqueta (opcional)</label>
                <input
                  type="text"
                  value={tableForm.label}
                  onChange={(e) => setTableForm((f) => ({ ...f, label: e.target.value }))}
                  className="field-input"
                  placeholder="Ej: Mesa familiar, Mesa terraza…"
                />
              </div>
              {tableError && (
                <div className="flex items-center gap-2 text-sm text-danger-700 bg-danger-50 border border-danger-100 rounded-lg px-3 py-2">
                  <AlertCircle size={13} />
                  {tableError}
                </div>
              )}
              <div className="flex gap-2 justify-end">
                <button type="button" onClick={cancelTableForm} className="btn-secondary text-sm">
                  Cancelar
                </button>
                <button type="submit" disabled={tableSaving} className="btn-primary text-sm gap-1.5">
                  {tableSaving
                    ? <span className="w-3.5 h-3.5 rounded-full border-2 border-white border-t-transparent animate-spin" />
                    : null
                  }
                  {editingTable ? 'Guardar cambios' : 'Agregar mesa'}
                </button>
              </div>
            </form>
          )}

          {!showTableForm && (
            <button
              onClick={() => { setShowTableForm(true); setEditingTable(null); setTableForm(TABLE_EMPTY) }}
              className="btn-secondary gap-2 self-start"
            >
              <Plus size={15} />
              Agregar tipo de mesa
            </button>
          )}
        </Section>
      )}

      {/* Servicios */}
      <Section
        title="Servicios y precios"
        description="El bot usará esta lista para informar a los clientes sobre tus servicios cuando pregunten."
      >
        {svcList.length > 0 && (
          <div className="flex flex-col gap-2">
            {svcList.map((s) => (
              <div
                key={s.id}
                className={cn(
                  'flex items-center gap-3 px-4 py-3 rounded-xl border',
                  s.is_active ? 'bg-slate-50 border-border' : 'bg-slate-50 border-border opacity-50',
                )}
              >
                <Tag size={15} className="text-slate-400 flex-shrink-0" />
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-medium text-slate-800 truncate">{s.name}</p>
                  <div className="flex items-center gap-3 mt-0.5">
                    {s.description && (
                      <p className="text-xs text-slate-400 truncate">{s.description}</p>
                    )}
                    <div className="flex items-center gap-2 flex-shrink-0">
                      {s.price != null && (
                        <span className="text-xs font-semibold text-primary-600">
                          ${Number(s.price).toLocaleString()}
                        </span>
                      )}
                      {s.duration_minutes && (
                        <span className="text-xs text-slate-400">{s.duration_minutes} min</span>
                      )}
                    </div>
                  </div>
                </div>
                <button
                  onClick={() => startEditSvc(s)}
                  className="btn-ghost p-1.5 text-slate-400 hover:text-slate-600 flex-shrink-0"
                  aria-label="Editar"
                >
                  <Pencil size={14} />
                </button>
                <button
                  onClick={() => handleDeleteSvc(s.id)}
                  className="btn-ghost p-1.5 text-slate-400 hover:text-danger-600 flex-shrink-0"
                  aria-label="Eliminar"
                >
                  <Trash2 size={14} />
                </button>
              </div>
            ))}
          </div>
        )}

        {svcList.length === 0 && !showSvcForm && (
          <div className="flex flex-col items-center justify-center py-6 text-center border border-dashed border-border rounded-xl">
            <Tag size={24} className="text-slate-200 mb-2" />
            <p className="text-sm text-slate-400">No hay servicios configurados</p>
            <p className="text-xs text-slate-300 mt-0.5">Agrega tus servicios para que el bot pueda informar a los clientes</p>
          </div>
        )}

        {showSvcForm && (
          <form onSubmit={handleSvcSubmit} className="flex flex-col gap-4 p-4 rounded-xl border border-primary-200 bg-primary-50 animate-fade-in">
            <p className="text-sm font-semibold text-primary-800">
              {editingSvc ? 'Editar servicio' : 'Agregar servicio'}
            </p>
            <div className="field">
              <label className="field-label field-label-required">Nombre del servicio</label>
              <input
                type="text"
                required
                value={svcForm.name}
                onChange={(e) => setSvcForm((f) => ({ ...f, name: e.target.value }))}
                className="field-input"
                placeholder="Ej: Corte de cabello, Consulta general, Masaje relajante…"
              />
            </div>
            <div className="field">
              <label className="field-label">Descripción</label>
              <input
                type="text"
                value={svcForm.description}
                onChange={(e) => setSvcForm((f) => ({ ...f, description: e.target.value }))}
                className="field-input"
                placeholder="Descripción breve (opcional)"
              />
            </div>
            <div className="grid grid-cols-2 gap-3">
              <div className="field">
                <label className="field-label">Precio</label>
                <input
                  type="number"
                  min={0}
                  step="0.01"
                  value={svcForm.price}
                  onChange={(e) => setSvcForm((f) => ({ ...f, price: e.target.value }))}
                  className="field-input"
                  placeholder="Ej: 25000"
                />
              </div>
              <div className="field">
                <label className="field-label">Duración (minutos)</label>
                <input
                  type="number"
                  min={1}
                  value={svcForm.duration_minutes}
                  onChange={(e) => setSvcForm((f) => ({ ...f, duration_minutes: e.target.value }))}
                  className="field-input"
                  placeholder="Ej: 30"
                />
              </div>
            </div>
            {svcError && (
              <div className="flex items-center gap-2 text-sm text-danger-700 bg-danger-50 border border-danger-100 rounded-lg px-3 py-2">
                <AlertCircle size={13} />
                {svcError}
              </div>
            )}
            <div className="flex gap-2 justify-end">
              <button type="button" onClick={cancelSvcForm} className="btn-secondary text-sm">
                Cancelar
              </button>
              <button type="submit" disabled={svcSaving} className="btn-primary text-sm gap-1.5">
                {svcSaving && <span className="w-3.5 h-3.5 rounded-full border-2 border-white border-t-transparent animate-spin" />}
                {editingSvc ? 'Guardar cambios' : 'Agregar servicio'}
              </button>
            </div>
          </form>
        )}

        {!showSvcForm && (
          <button
            onClick={() => { setShowSvcForm(true); setEditingSvc(null); setSvcForm(SERVICE_EMPTY) }}
            className="btn-secondary gap-2 self-start"
          >
            <Plus size={15} />
            Agregar servicio
          </button>
        )}
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
