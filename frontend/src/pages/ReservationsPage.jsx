import { useState, useEffect, useCallback } from 'react'
import { Search, Plus, Filter, Trash2, CheckCircle, XCircle, AlertCircle } from 'lucide-react'
import { reservationsApi } from '@/lib/api'
import { STATUS_BADGE, STATUS_LABELS, formatDate, formatTime, cn } from '@/lib/utils'

const STATUS_OPTIONS = [
  { value: '', label: 'Todos los estados' },
  { value: 'pending', label: 'Pendiente' },
  { value: 'confirmed', label: 'Confirmada' },
  { value: 'cancelled', label: 'Cancelada' },
  { value: 'no_show', label: 'No asistió' },
]

function SkeletonRow() {
  return (
    <tr>
      {Array.from({ length: 6 }).map((_, i) => (
        <td key={i} className="px-4 py-3.5">
          <div className="skeleton h-4 rounded w-full max-w-[120px]" />
        </td>
      ))}
    </tr>
  )
}

export default function ReservationsPage() {
  const [reservations, setReservations] = useState([])
  const [loading, setLoading] = useState(true)
  const [search, setSearch] = useState('')
  const [statusFilter, setStatusFilter] = useState('')
  const [dateFilter, setDateFilter] = useState('')
  const [updatingId, setUpdatingId] = useState(null)

  const load = useCallback(async () => {
    setLoading(true)
    try {
      const params = {}
      if (dateFilter) params.date = dateFilter
      if (statusFilter) params.status = statusFilter
      const { data } = await reservationsApi.list(params)
      setReservations(data)
    } catch {
      setReservations([])
    } finally {
      setLoading(false)
    }
  }, [dateFilter, statusFilter])

  useEffect(() => { load() }, [load])

  async function updateStatus(id, status) {
    setUpdatingId(id)
    try {
      await reservationsApi.updateStatus(id, status)
      setReservations((rs) =>
        rs.map((r) => (r.id === id ? { ...r, status } : r))
      )
    } finally {
      setUpdatingId(null)
    }
  }

  async function deleteReservation(id) {
    if (!confirm('¿Eliminar esta reserva?')) return
    try {
      await reservationsApi.delete(id)
      setReservations((rs) => rs.filter((r) => r.id !== id))
    } catch {}
  }

  const filtered = reservations.filter((r) => {
    if (!search) return true
    const q = search.toLowerCase()
    return (
      r.customer_name?.toLowerCase().includes(q) ||
      r.customer_phone?.toLowerCase().includes(q)
    )
  })

  return (
    <div className="flex flex-col gap-5 max-w-6xl animate-fade-in">
      {/* Barra de herramientas */}
      <div className="flex flex-col sm:flex-row gap-3 items-start sm:items-center justify-between">
        <div className="flex flex-wrap gap-2 flex-1">
          {/* Búsqueda */}
          <div className="relative flex-1 min-w-[200px] max-w-sm">
            <Search size={15} className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400 pointer-events-none" />
            <input
              type="text"
              placeholder="Buscar por nombre o teléfono…"
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="field-input pl-9 h-9 text-sm"
              aria-label="Buscar reservas"
            />
          </div>

          {/* Filtro estado */}
          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            className="field-input h-9 text-sm w-auto"
            aria-label="Filtrar por estado"
          >
            {STATUS_OPTIONS.map((o) => (
              <option key={o.value} value={o.value}>{o.label}</option>
            ))}
          </select>

          {/* Filtro fecha */}
          <input
            type="date"
            value={dateFilter}
            onChange={(e) => setDateFilter(e.target.value)}
            className="field-input h-9 text-sm w-auto"
            aria-label="Filtrar por fecha"
          />
        </div>
      </div>

      {/* Tabla */}
      <div className="card overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-sm" role="table" aria-label="Lista de reservas">
            <thead>
              <tr className="border-b border-border bg-slate-50/60">
                {['Cliente', 'Teléfono', 'Fecha', 'Hora', 'Estado', 'Acciones'].map((h) => (
                  <th
                    key={h}
                    className="px-4 py-3 text-left text-xs font-semibold text-slate-500 uppercase tracking-wide"
                  >
                    {h}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody className="divide-y divide-border">
              {loading
                ? Array.from({ length: 6 }).map((_, i) => <SkeletonRow key={i} />)
                : filtered.length === 0
                  ? (
                    <tr>
                      <td colSpan={6} className="py-16 text-center">
                        <div className="flex flex-col items-center gap-2">
                          <Filter size={28} className="text-slate-200" />
                          <p className="text-sm text-slate-400">
                            {search || statusFilter || dateFilter
                              ? 'Sin resultados para este filtro'
                              : 'Aún no hay reservas registradas'}
                          </p>
                        </div>
                      </td>
                    </tr>
                  )
                  : filtered.map((r, i) => (
                    <tr
                      key={r.id}
                      className="hover:bg-slate-50/50 transition-colors"
                      style={{ animationDelay: `${i * 30}ms` }}
                    >
                      <td className="px-4 py-3.5">
                        <span className="font-medium text-slate-900">{r.customer_name}</span>
                      </td>
                      <td className="px-4 py-3.5 text-slate-500">{r.customer_phone}</td>
                      <td className="px-4 py-3.5 text-slate-600">{formatDate(r.date)}</td>
                      <td className="px-4 py-3.5 text-slate-600">{formatTime(r.time_start)}</td>
                      <td className="px-4 py-3.5">
                        <span className={STATUS_BADGE[r.status]}>{STATUS_LABELS[r.status]}</span>
                      </td>
                      <td className="px-4 py-3.5">
                        <div className="flex items-center gap-1">
                          {r.status === 'pending' && (
                            <button
                              onClick={() => updateStatus(r.id, 'confirmed')}
                              disabled={updatingId === r.id}
                              className="btn-ghost p-1.5 text-primary-600 hover:bg-primary-50"
                              title="Confirmar"
                              aria-label="Confirmar reserva"
                            >
                              {updatingId === r.id
                                ? <span className="w-3.5 h-3.5 rounded-full border-2 border-primary-500 border-t-transparent animate-spin block" />
                                : <CheckCircle size={15} />
                              }
                            </button>
                          )}
                          {(r.status === 'pending' || r.status === 'confirmed') && (
                            <button
                              onClick={() => updateStatus(r.id, 'cancelled')}
                              disabled={updatingId === r.id}
                              className="btn-ghost p-1.5 text-slate-400 hover:text-danger-600 hover:bg-danger-50"
                              title="Cancelar"
                              aria-label="Cancelar reserva"
                            >
                              <XCircle size={15} />
                            </button>
                          )}
                          <button
                            onClick={() => deleteReservation(r.id)}
                            className="btn-ghost p-1.5 text-slate-300 hover:text-danger-600 hover:bg-danger-50"
                            title="Eliminar"
                            aria-label="Eliminar reserva"
                          >
                            <Trash2 size={14} />
                          </button>
                        </div>
                      </td>
                    </tr>
                  ))
              }
            </tbody>
          </table>
        </div>

        {/* Contador */}
        {!loading && filtered.length > 0 && (
          <div className="px-4 py-3 border-t border-border bg-slate-50/50">
            <p className="text-xs text-slate-400">
              {filtered.length} reserva{filtered.length !== 1 ? 's' : ''} encontrada{filtered.length !== 1 ? 's' : ''}
            </p>
          </div>
        )}
      </div>
    </div>
  )
}
