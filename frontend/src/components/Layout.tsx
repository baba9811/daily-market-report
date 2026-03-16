import { Outlet, NavLink } from 'react-router-dom'
import {
  LayoutDashboard,
  FileText,
  TrendingUp,
  RotateCcw,
  Settings,
} from 'lucide-react'

const navItems = [
  { to: '/', icon: LayoutDashboard, label: 'Dashboard' },
  { to: '/reports', icon: FileText, label: 'Reports' },
  { to: '/performance', icon: TrendingUp, label: 'Performance' },
  { to: '/retrospective', icon: RotateCcw, label: 'Retrospective' },
  { to: '/settings', icon: Settings, label: 'Settings' },
]

export default function Layout() {
  return (
    <div className="flex min-h-screen">
      {/* Sidebar */}
      <aside className="w-64 bg-bg-card border-r border-slate-700 flex flex-col">
        <div className="p-6 border-b border-slate-700">
          <h1 className="text-xl font-bold text-white flex items-center gap-2">
            <TrendingUp className="text-accent-blue" size={24} />
            Daily Scheduler
          </h1>
          <p className="text-xs text-slate-400 mt-1">AI Trading Report System</p>
        </div>
        <nav className="flex-1 p-4 space-y-1">
          {navItems.map(({ to, icon: Icon, label }) => (
            <NavLink
              key={to}
              to={to}
              end={to === '/'}
              className={({ isActive }) =>
                `flex items-center gap-3 px-4 py-2.5 rounded-lg text-sm transition-colors ${
                  isActive
                    ? 'bg-accent-blue/10 text-accent-blue font-medium'
                    : 'text-slate-400 hover:text-white hover:bg-bg-hover'
                }`
              }
            >
              <Icon size={18} />
              {label}
            </NavLink>
          ))}
        </nav>
        <div className="p-4 border-t border-slate-700">
          <p className="text-xs text-slate-500 text-center">v0.1.0 &middot; Apache 2.0</p>
        </div>
      </aside>

      {/* Main content */}
      <main className="flex-1 overflow-auto">
        <div className="max-w-7xl mx-auto p-8">
          <Outlet />
        </div>
      </main>
    </div>
  )
}
