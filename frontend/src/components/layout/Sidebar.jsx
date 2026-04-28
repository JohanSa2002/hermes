import { NavLink, useNavigate } from 'react-router-dom'
import {
  LayoutDashboard, CalendarDays, BookOpen, Settings, CreditCard,
  MessageCircle, LogOut, ChevronRight,
} from 'lucide-react'
import { useAuth } from '@/contexts/AuthContext'
import { cn } from '@/lib/utils'

const NAV_ITEMS = [
  { to: '/dashboard', icon: LayoutDashboard, label: 'Dashboard' },
  { to: '/reservations', icon: BookOpen, label: 'Reservas' },
  { to: '/calendar', icon: CalendarDays, label: 'Disponibilidad' },
  { to: '/config', icon: Settings, label: 'Configuración' },
  { to: '/billing', icon: CreditCard, label: 'Plan y Facturación' },
]

export default function Sidebar() {
  const { user, logout } = useAuth()
  const navigate = useNavigate()

  async function handleLogout() {
    await logout()
    navigate('/login')
  }

  return (
    <aside className="flex flex-col w-60 min-h-screen bg-white border-r border-border flex-shrink-0">
      {/* Logo */}
      <div className="flex items-center gap-2.5 px-5 py-5 border-b border-border">
        <div className="w-8 h-8 rounded-lg bg-primary-600 flex items-center justify-center flex-shrink-0">
          <MessageCircle className="w-4.5 h-4.5 text-white" size={18} />
        </div>
        <span className="font-display font-semibold text-slate-900 text-base leading-tight">
          Hermes<span className="text-primary-600">Messages</span>
        </span>
      </div>

      {/* Nav */}
      <nav className="flex-1 px-3 py-4 flex flex-col gap-0.5">
        {NAV_ITEMS.map(({ to, icon: Icon, label }, i) => (
          <NavLink
            key={to}
            to={to}
            className={({ isActive }) =>
              cn(
                'flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-all duration-150',
                'focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary-500',
                isActive
                  ? 'bg-primary-50 text-primary-700'
                  : 'text-slate-600 hover:bg-slate-50 hover:text-slate-900',
              )
            }
            style={{ animationDelay: `${i * 40}ms` }}
          >
            {({ isActive }) => (
              <>
                <Icon
                  size={17}
                  className={cn(
                    'flex-shrink-0 transition-colors duration-150',
                    isActive ? 'text-primary-600' : 'text-slate-400',
                  )}
                />
                <span className="flex-1">{label}</span>
                {isActive && (
                  <ChevronRight size={14} className="text-primary-400 flex-shrink-0" />
                )}
              </>
            )}
          </NavLink>
        ))}
      </nav>

      {/* Footer usuario */}
      <div className="border-t border-border px-3 py-3">
        <div className="flex items-center gap-3 px-3 py-2.5 rounded-lg">
          <div className="w-8 h-8 rounded-full bg-primary-100 flex items-center justify-center flex-shrink-0">
            <span className="text-xs font-semibold text-primary-700">
              {user?.email?.[0]?.toUpperCase() ?? 'U'}
            </span>
          </div>
          <div className="flex-1 min-w-0">
            <p className="text-xs font-medium text-slate-900 truncate">{user?.email}</p>
            <p className="text-xs text-slate-400">Propietario</p>
          </div>
        </div>
        <button
          onClick={handleLogout}
          className="btn-ghost w-full justify-start mt-1 text-slate-500 hover:text-danger-600 hover:bg-danger-50"
        >
          <LogOut size={15} />
          Cerrar sesión
        </button>
      </div>
    </aside>
  )
}
