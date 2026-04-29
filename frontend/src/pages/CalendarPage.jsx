import { useState, useEffect } from 'react'
import {
  format, addMonths, startOfMonth, endOfMonth,
  startOfWeek, endOfWeek, eachDayOfInterval,
  isSameDay, isToday, isSameMonth,
} from 'date-fns'
import { es } from 'date-fns/locale'
import { ChevronLeft, ChevronRight, Lock, Unlock, Clock } from 'lucide-react'
import { calendarApi } from '@/lib/api'
import { cn } from '@/lib/utils'

const WEEK_DAYS = ['Lun', 'Mar', 'Mié', 'Jue', 'Vie', 'Sáb', 'Dom']

function buildMonthGrid(date) {
  const start = startOfWeek(startOfMonth(date), { weekStartsOn: 1 })
  const end = endOfWeek(endOfMonth(date), { weekStartsOn: 1 })
  return eachDayOfInterval({ start, end })
}

export default function CalendarPage() {
  const [currentMonth, setCurrentMonth] = useState(new Date())
  const [selectedDate, setSelectedDate] = useState(new Date())
  const [slots, setSlots] = useState([])
  const [blockedDates, setBlockedDates] = useState([])
  const [loadingSlots, setLoadingSlots] = useState(false)
  const [togglingDate, setTogglingDate] = useState(false)

  const monthDays = buildMonthGrid(currentMonth)
  const selectedStr = format(selectedDate, 'yyyy-MM-dd')
  const isBlocked = blockedDates.includes(selectedStr)

  useEffect(() => {
    async function loadSlots() {
      setLoadingSlots(true)
      try {
        const { data } = await calendarApi.getAvailability(selectedStr)
        setSlots(data.slots ?? [])
      } catch {
        setSlots([])
      } finally {
        setLoadingSlots(false)
      }
    }
    loadSlots()
  }, [selectedStr])

  async function toggleBlockDate() {
    setTogglingDate(true)
    try {
      if (isBlocked) {
        await calendarApi.unblockDate(selectedStr)
        setBlockedDates((d) => d.filter((x) => x !== selectedStr))
      } else {
        await calendarApi.blockDate(selectedStr)
        setBlockedDates((d) => [...d, selectedStr])
      }
    } finally {
      setTogglingDate(false)
    }
  }

  return (
    <div className="flex flex-col gap-6 max-w-4xl animate-fade-in">
      <div className="grid lg:grid-cols-3 gap-5 items-start">
        {/* Calendario mensual */}
        <div className="lg:col-span-2 card p-5">
          {/* Nav mes */}
          <div className="flex items-center justify-between mb-5">
            <h3 className="font-display text-base font-semibold text-slate-800 capitalize">
              {format(currentMonth, "MMMM yyyy", { locale: es })}
            </h3>
            <div className="flex gap-1">
              <button
                onClick={() => setCurrentMonth((d) => addMonths(d, -1))}
                className="btn-ghost p-1.5"
                aria-label="Mes anterior"
              >
                <ChevronLeft size={16} />
              </button>
              <button
                onClick={() => { setCurrentMonth(new Date()); setSelectedDate(new Date()) }}
                className="btn-secondary px-3 py-1.5 text-xs"
              >
                Hoy
              </button>
              <button
                onClick={() => setCurrentMonth((d) => addMonths(d, 1))}
                className="btn-ghost p-1.5"
                aria-label="Mes siguiente"
              >
                <ChevronRight size={16} />
              </button>
            </div>
          </div>

          {/* Cabecera días */}
          <div className="grid grid-cols-7 gap-1 mb-1">
            {WEEK_DAYS.map((d) => (
              <div key={d} className="text-center text-xs font-medium text-slate-400 pb-1">{d}</div>
            ))}
          </div>

          {/* Días del mes */}
          <div className="grid grid-cols-7 gap-1">
            {monthDays.map((day) => {
              const dayStr = format(day, 'yyyy-MM-dd')
              const selected = isSameDay(day, selectedDate)
              const today = isToday(day)
              const blocked = blockedDates.includes(dayStr)
              const otherMonth = !isSameMonth(day, currentMonth)

              return (
                <button
                  key={dayStr}
                  onClick={() => setSelectedDate(day)}
                  className={cn(
                    'relative flex flex-col items-center justify-center rounded-lg aspect-square text-sm font-medium transition-all duration-150',
                    'focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary-500',
                    otherMonth && 'opacity-25 pointer-events-none',
                    selected
                      ? 'bg-primary-600 text-white shadow-sm'
                      : blocked
                        ? 'bg-slate-100 text-slate-400 line-through'
                        : today
                          ? 'bg-primary-50 text-primary-700 ring-1 ring-primary-300'
                          : 'hover:bg-slate-50 text-slate-700',
                  )}
                  aria-pressed={selected}
                  aria-label={`${format(day, 'd MMMM', { locale: es })}${blocked ? ', bloqueado' : ''}`}
                >
                  <span className="leading-none">{format(day, 'd')}</span>
                  {blocked && !selected && (
                    <Lock size={8} className="mt-0.5 opacity-50" />
                  )}
                </button>
              )
            })}
          </div>
        </div>

        {/* Panel del día seleccionado */}
        <div className="card p-5 flex flex-col gap-4">
          <div>
            <p className="text-xs text-slate-400 uppercase tracking-wide font-medium">Día seleccionado</p>
            <p className="font-display text-lg font-semibold text-slate-900 capitalize mt-0.5">
              {format(selectedDate, "EEEE d 'de' MMMM", { locale: es })}
            </p>
          </div>

          {/* Bloquear/Desbloquear */}
          <div className={cn(
            'flex items-center gap-3 rounded-xl px-4 py-3.5 border transition-colors',
            isBlocked
              ? 'bg-danger-50 border-danger-100'
              : 'bg-slate-50 border-border',
          )}>
            <div className={cn('flex-1', isBlocked ? 'text-danger-700' : 'text-slate-700')}>
              <p className="text-sm font-medium">{isBlocked ? 'Día bloqueado' : 'Día disponible'}</p>
              <p className="text-xs mt-0.5 opacity-70">
                {isBlocked
                  ? 'El bot no acepta reservas este día'
                  : 'El bot acepta reservas según tu horario'}
              </p>
            </div>
            <button
              onClick={toggleBlockDate}
              disabled={togglingDate}
              className={cn(
                'btn flex-shrink-0 px-3 py-2 text-xs gap-1.5',
                isBlocked
                  ? 'bg-white border border-border text-slate-700 hover:bg-slate-50 shadow-card'
                  : 'bg-danger-600 text-white hover:bg-red-700',
              )}
              aria-label={isBlocked ? 'Desbloquear fecha' : 'Bloquear fecha'}
            >
              {togglingDate
                ? <span className="w-3.5 h-3.5 rounded-full border-2 border-current border-t-transparent animate-spin block" />
                : isBlocked
                  ? <><Unlock size={12} />Desbloquear</>
                  : <><Lock size={12} />Bloquear</>
              }
            </button>
          </div>

          {/* Slots */}
          <div className="flex-1">
            <div className="flex items-center gap-1.5 mb-3">
              <Clock size={14} className="text-slate-400" />
              <p className="text-xs font-semibold text-slate-500 uppercase tracking-wide">
                Horarios disponibles
              </p>
            </div>

            {loadingSlots ? (
              <div className="flex flex-col gap-2">
                {Array.from({ length: 5 }).map((_, i) => (
                  <div key={i} className="skeleton h-9 rounded-lg" />
                ))}
              </div>
            ) : isBlocked ? (
              <div className="flex flex-col items-center justify-center py-8 text-center">
                <Lock size={24} className="text-slate-200 mb-2" />
                <p className="text-sm text-slate-400">Día bloqueado</p>
              </div>
            ) : slots.length === 0 ? (
              <div className="flex flex-col items-center justify-center py-8 text-center">
                <Clock size={24} className="text-slate-200 mb-2" />
                <p className="text-sm text-slate-400">Sin horarios disponibles</p>
                <p className="text-xs text-slate-300 mt-1">Verifica tu configuración de horarios</p>
              </div>
            ) : (
              <div className="flex flex-col gap-1.5 max-h-56 overflow-y-auto pr-1">
                {slots.map((slot) => (
                  <div
                    key={slot.time_start}
                    className={cn(
                      'flex items-center justify-between px-3.5 py-2.5 rounded-lg text-sm border transition-colors',
                      slot.available > 0
                        ? 'bg-primary-50 border-primary-100 text-primary-700'
                        : 'bg-slate-50 border-border text-slate-400',
                    )}
                  >
                    <span className="font-medium">{slot.time_start?.slice(0, 5)}</span>
                    <span className="text-xs">
                      {slot.available > 0
                        ? `${slot.available} libre${slot.available > 1 ? 's' : ''}`
                        : 'Lleno'}
                    </span>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}
