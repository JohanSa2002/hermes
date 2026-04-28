import { useState, useEffect } from 'react'
import { format } from 'date-fns'
import { es } from 'date-fns/locale'
import {
  CalendarCheck, Clock, XCircle, Users, TrendingUp, MessageCircle,
} from 'lucide-react'
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
} from 'recharts'
import { dashboardApi } from '@/lib/api'
import { STATUS_BADGE, STATUS_LABELS, formatTime } from '@/lib/utils'
import { cn } from '@/lib/utils'

function StatCard({ icon: Icon, label, value, color, delay }) {
  return (
    <div className={cn('card p-5 flex items-center gap-4', `animate-stagger-${delay}`)}>
      <div className={cn('w-11 h-11 rounded-xl flex items-center justify-center flex-shrink-0', color)}>
        <Icon size={20} />
      </div>
      <div>
        <p className="text-2xl font-display font-bold text-slate-900">{value ?? '—'}</p>
        <p className="text-sm text-slate-500">{label}</p>
      </div>
    </div>
  )
}

function SkeletonCard() {
  return (
    <div className="card p-5 flex items-center gap-4">
      <div className="skeleton w-11 h-11 rounded-xl" />
      <div className="flex-1 flex flex-col gap-2">
        <div className="skeleton h-6 w-16 rounded" />
        <div className="skeleton h-4 w-28 rounded" />
      </div>
    </div>
  )
}

export default function DashboardPage() {
  const [stats, setStats] = useState(null)
  const [agenda, setAgenda] = useState([])
  const [peakHours, setPeakHours] = useState([])
  const [loading, setLoading] = useState(true)

  const today = format(new Date(), 'yyyy-MM-dd')
  const todayLabel = format(new Date(), "EEEE d 'de' MMMM", { locale: es })

  useEffect(() => {
    async function load() {
      try {
        const [statsRes, agendaRes, peakRes] = await Promise.all([
          dashboardApi.getStats(),
          dashboardApi.getAgenda(today),
          dashboardApi.getPeakHours(),
        ])
        setStats(statsRes.data)
        setAgenda(agendaRes.data)
        setPeakHours(peakRes.data)
      } catch {
        // datos simulados para preview
        setStats({ total: 24, confirmed: 18, pending: 4, cancelled: 2 })
        setAgenda([])
        setPeakHours([
          { hour: '09:00', count: 3 }, { hour: '10:00', count: 5 }, { hour: '11:00', count: 4 },
          { hour: '14:00', count: 6 }, { hour: '15:00', count: 8 }, { hour: '16:00', count: 3 },
        ])
      } finally {
        setLoading(false)
      }
    }
    load()
  }, [today])

  const statCards = stats ? [
    { icon: CalendarCheck, label: 'Confirmadas', value: stats.confirmed, color: 'bg-primary-100 text-primary-600', delay: 1 },
    { icon: Clock, label: 'Pendientes', value: stats.pending, color: 'bg-warning-100 text-warning-600', delay: 2 },
    { icon: XCircle, label: 'Canceladas', value: stats.cancelled, color: 'bg-danger-100 text-danger-500', delay: 3 },
    { icon: Users, label: 'Total este mes', value: stats.total, color: 'bg-slate-100 text-slate-600', delay: 4 },
  ] : []

  return (
    <div className="flex flex-col gap-7 max-w-5xl">
      {/* Header con fecha */}
      <div className="animate-stagger-1">
        <p className="text-sm text-slate-500 capitalize">{todayLabel}</p>
        <h2 className="font-display text-2xl font-bold text-slate-900 mt-0.5">
          Resumen de tu negocio
        </h2>
      </div>

      {/* Stat cards */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        {loading
          ? Array.from({ length: 4 }).map((_, i) => <SkeletonCard key={i} />)
          : statCards.map((s) => <StatCard key={s.label} {...s} />)
        }
      </div>

      {/* Gráfica + Agenda */}
      <div className="grid lg:grid-cols-3 gap-5">
        {/* Gráfica horas pico */}
        <div className="lg:col-span-2 card p-5 animate-stagger-3">
          <div className="flex items-center gap-2 mb-4">
            <TrendingUp size={16} className="text-primary-600" />
            <h3 className="font-display text-sm font-semibold text-slate-800">Horas pico de reservas</h3>
          </div>
          {loading ? (
            <div className="skeleton h-48 rounded-lg" />
          ) : peakHours.length ? (
            <ResponsiveContainer width="100%" height={200}>
              <BarChart data={peakHours} margin={{ top: 0, right: 0, left: -24, bottom: 0 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" vertical={false} />
                <XAxis
                  dataKey="hour"
                  tick={{ fontSize: 11, fill: '#94a3b8', fontFamily: 'DM Sans' }}
                  axisLine={false}
                  tickLine={false}
                />
                <YAxis
                  tick={{ fontSize: 11, fill: '#94a3b8', fontFamily: 'DM Sans' }}
                  axisLine={false}
                  tickLine={false}
                  allowDecimals={false}
                />
                <Tooltip
                  contentStyle={{
                    background: '#fff', border: '1px solid #e1e7ef',
                    borderRadius: '8px', fontSize: '12px', fontFamily: 'DM Sans',
                    boxShadow: '0 4px 12px rgb(0 0 0 / 0.08)',
                  }}
                  cursor={{ fill: '#f1f5f9' }}
                  formatter={(v) => [`${v} reservas`, 'Reservas']}
                />
                <Bar dataKey="count" fill="#059669" radius={[4, 4, 0, 0]} maxBarSize={40} />
              </BarChart>
            </ResponsiveContainer>
          ) : (
            <div className="h-48 flex items-center justify-center text-sm text-slate-400">
              Sin datos suficientes todavía
            </div>
          )}
        </div>

        {/* Agenda del día */}
        <div className="card p-5 animate-stagger-4">
          <div className="flex items-center gap-2 mb-4">
            <MessageCircle size={16} className="text-primary-600" />
            <h3 className="font-display text-sm font-semibold text-slate-800">Agenda de hoy</h3>
          </div>
          {loading ? (
            <div className="flex flex-col gap-3">
              {Array.from({ length: 4 }).map((_, i) => (
                <div key={i} className="skeleton h-12 rounded-lg" />
              ))}
            </div>
          ) : agenda.length ? (
            <div className="flex flex-col gap-2 overflow-y-auto max-h-52">
              {agenda.map((r, i) => (
                <div
                  key={r.id ?? i}
                  className="flex items-center gap-3 p-2.5 rounded-lg hover:bg-slate-50 transition-colors"
                >
                  <div className="text-xs font-medium text-slate-500 w-10 flex-shrink-0">
                    {formatTime(r.time_start)}
                  </div>
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-medium text-slate-900 truncate">{r.customer_name}</p>
                    <p className="text-xs text-slate-400 truncate">{r.notes || 'Sin notas'}</p>
                  </div>
                  <span className={STATUS_BADGE[r.status]}>{STATUS_LABELS[r.status]}</span>
                </div>
              ))}
            </div>
          ) : (
            <div className="flex flex-col items-center justify-center h-36 text-center">
              <CalendarCheck size={28} className="text-slate-200 mb-2" />
              <p className="text-sm text-slate-400">Sin reservas para hoy</p>
            </div>
          )}
        </div>
      </div>

      {/* Tip de integración WhatsApp si no está conectado */}
      <div className="card p-5 border-primary-100 bg-primary-50 flex items-start gap-4 animate-stagger-5">
        <div className="w-10 h-10 rounded-xl bg-primary-100 flex items-center justify-center flex-shrink-0">
          <MessageCircle size={18} className="text-primary-600" />
        </div>
        <div className="flex-1 min-w-0">
          <p className="text-sm font-semibold text-primary-800">Conecta tu WhatsApp</p>
          <p className="text-xs text-primary-600 mt-0.5">
            Ve a <strong>Configuración</strong> para vincular tu número de WhatsApp Business
            y comenzar a recibir reservas automáticamente.
          </p>
        </div>
      </div>
    </div>
  )
}
