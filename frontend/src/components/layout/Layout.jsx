import { Outlet, useLocation } from 'react-router-dom'
import Sidebar from './Sidebar'

const PAGE_TITLES = {
  '/dashboard': 'Dashboard',
  '/reservations': 'Reservas',
  '/calendar': 'Disponibilidad',
  '/config': 'Configuración',
  '/billing': 'Plan y Facturación',
}

export default function Layout() {
  const { pathname } = useLocation()
  const title = PAGE_TITLES[pathname] ?? 'HermesMessages'

  return (
    <div className="flex min-h-screen">
      <Sidebar />
      <div className="flex-1 flex flex-col min-w-0">
        <header className="sticky top-0 z-10 bg-bg/80 backdrop-blur border-b border-border px-8 py-4">
          <h1 className="font-display text-xl font-semibold text-slate-900">{title}</h1>
        </header>
        <main className="flex-1 px-8 py-6">
          <Outlet />
        </main>
      </div>
    </div>
  )
}
