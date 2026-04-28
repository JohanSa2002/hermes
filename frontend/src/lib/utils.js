import { clsx } from 'clsx'
import { twMerge } from 'tailwind-merge'

export function cn(...inputs) {
  return twMerge(clsx(inputs))
}

export function formatDate(dateStr, opts = {}) {
  if (!dateStr) return '—'
  const d = new Date(dateStr)
  return d.toLocaleDateString('es-ES', {
    day: '2-digit', month: 'short', year: 'numeric', ...opts,
  })
}

export function formatTime(timeStr) {
  if (!timeStr) return '—'
  return timeStr.slice(0, 5)
}

export function formatDateTime(dateStr) {
  if (!dateStr) return '—'
  const d = new Date(dateStr)
  return d.toLocaleString('es-ES', {
    day: '2-digit', month: 'short', hour: '2-digit', minute: '2-digit',
  })
}

export const STATUS_LABELS = {
  pending: 'Pendiente',
  confirmed: 'Confirmada',
  cancelled: 'Cancelada',
  no_show: 'No asistió',
}

export const STATUS_BADGE = {
  pending: 'badge-yellow',
  confirmed: 'badge-green',
  cancelled: 'badge-red',
  no_show: 'badge-gray',
}

export const BUSINESS_TYPES = [
  { value: 'restaurant', label: 'Restaurante' },
  { value: 'clinic', label: 'Clínica / Consultorio' },
  { value: 'salon', label: 'Salón de belleza' },
  { value: 'spa', label: 'Spa / Bienestar' },
  { value: 'barbershop', label: 'Barbería' },
  { value: 'gym', label: 'Gimnasio / Entrenador' },
  { value: 'other', label: 'Otro' },
]

export const TIMEZONES = [
  { value: 'America/Bogota', label: 'Bogotá (UTC-5)' },
  { value: 'America/Mexico_City', label: 'Ciudad de México (UTC-6)' },
  { value: 'America/Lima', label: 'Lima (UTC-5)' },
  { value: 'America/Santiago', label: 'Santiago (UTC-4)' },
  { value: 'America/Buenos_Aires', label: 'Buenos Aires (UTC-3)' },
  { value: 'America/Caracas', label: 'Caracas (UTC-4)' },
  { value: 'Europe/Madrid', label: 'Madrid (UTC+1/+2)' },
  { value: 'UTC', label: 'UTC' },
]

export const DAYS_ES = ['Lun', 'Mar', 'Mié', 'Jue', 'Vie', 'Sáb', 'Dom']
export const DAYS_FULL = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo']
