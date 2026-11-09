import { lazy, Suspense, useState } from 'react'
import { NavLink, Navigate, Outlet, Route, Routes, useLocation } from 'react-router-dom'
import {
  ArrowUpRight,
  LayoutDashboard,
  Users,
  UserRound,
  LogOut,
  Menu,
  X,
  ShieldCheck,
} from 'lucide-react'
import { useAuth } from './auth'
import { errorMessage } from './lib/api'
import { ErrorBox, Modal, Spinner } from './components/ui'
const Home = lazy(() => import('./pages/Home'))
const Login = lazy(() => import('./pages/Login'))
const Profile = lazy(() => import('./pages/Profile'))
const UsersPage = lazy(() => import('./pages/Users'))

function Protected() {
  const { user, loading } = useAuth()
  if (loading) return <Spinner />
  return user ? <Layout /> : <Navigate to="/ingresar" replace />
}

function Layout() {
  const { user, logout } = useAuth()
  const [open, setOpen] = useState(false)
  const [leaving, setLeaving] = useState(false)
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState('')
  const location = useLocation()
  return (
    <div className="app-shell">
      <aside className={`sidebar ${open ? 'is-open' : ''}`}>
        <NavLink className="brand" to="/" onClick={() => setOpen(false)}>
          <span className="brand-mark">
            JG<span>↗</span>
          </span>
          <span>
            REPUESTOS<small>GESTIÓN COMERCIAL</small>
          </span>
        </NavLink>
        <button
          className="icon-button mobile-close"
          onClick={() => setOpen(false)}
          aria-label="Cerrar navegación"
        >
          <X />
        </button>
        <div className="workspace-label">ESPACIO DE TRABAJO</div>
        <nav aria-label="Navegación principal">
          <NavLink to="/" end onClick={() => setOpen(false)}>
            <LayoutDashboard size={19} /> Inicio <ArrowUpRight className="nav-arrow" size={16} />
          </NavLink>
          {user?.permissions.includes('users.manage') && (
            <NavLink to="/usuarios" onClick={() => setOpen(false)}>
              <Users size={19} /> Equipo y usuarios
            </NavLink>
          )}
          <NavLink to="/perfil" onClick={() => setOpen(false)}>
            <UserRound size={19} /> Mi cuenta
          </NavLink>
        </nav>
        <div className="sidebar-note">
          <ShieldCheck size={24} />
          <strong>Un espacio de confianza</strong>
          <p>Acceso personal y permisos según tu responsabilidad.</p>
        </div>
        <div className="sidebar-bottom">
          <span className="version-dot" />
          JG Repuestos <small>v0.1</small>
        </div>
      </aside>
      {open && (
        <button
          className="mobile-backdrop"
          onClick={() => setOpen(false)}
          aria-label="Cerrar menú"
        />
      )}
      <div className="main-area">
        <header className="topbar">
          <button
            className="icon-button mobile-menu"
            onClick={() => setOpen(true)}
            aria-label="Abrir navegación"
          >
            <Menu />
          </button>
          <div className="breadcrumb">
            Espacio de trabajo <span>/</span>
            <strong>
              {location.pathname === '/usuarios'
                ? 'Equipo y usuarios'
                : location.pathname === '/perfil'
                  ? 'Mi cuenta'
                  : 'Inicio'}
            </strong>
          </div>
          <div className="topbar-right">
            <span className="workspace-badge">JG · Colombia</span>
            <NavLink to="/perfil" className="topbar-user">
              <span className="avatar">{user?.full_name.slice(0, 1).toUpperCase()}</span>
              <span>
                {user?.full_name}
                <small>
                  {user?.roles.includes('admin') ? 'Administrador' : 'Miembro del equipo'}
                </small>
              </span>
            </NavLink>
            <button
              className="icon-button"
              aria-label="Cerrar sesión"
              onClick={() => {
                setError('')
                setLeaving(true)
              }}
            >
              <LogOut size={18} />
            </button>
          </div>
        </header>
        <main className="page-content">
          <Outlet />
        </main>
        <footer className="app-footer">
          <span>JG Repuestos · Gestión comercial</span>
          <span>Colombia / America/Bogota</span>
        </footer>
      </div>
      <Modal
        open={leaving}
        onOpenChange={setLeaving}
        title="¿Cerrar tu sesión?"
        description="Podrás volver a ingresar con tu correo y contraseña."
      >
        <ErrorBox message={error} />
        <button
          className="primary full"
          disabled={busy}
          onClick={async () => {
            setBusy(true)
            try {
              await logout()
            } catch (e) {
              setError(errorMessage(e))
            } finally {
              setBusy(false)
            }
          }}
        >
          {busy ? 'Cerrando…' : 'Confirmar cierre de sesión'}
        </button>
      </Modal>
    </div>
  )
}

function AdminOnly() {
  const { user } = useAuth()
  return user?.permissions.includes('users.manage') ? <UsersPage /> : <Navigate to="/" replace />
}

export default function App() {
  const { loading } = useAuth()
  if (loading) return <Spinner />
  return (
    <Suspense fallback={<Spinner />}>
      <Routes>
        <Route path="/ingresar" element={<Login />} />
        <Route element={<Protected />}>
          <Route index element={<Home />} />
          <Route path="usuarios" element={<AdminOnly />} />
          <Route path="perfil" element={<Profile />} />
        </Route>
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </Suspense>
  )
}
