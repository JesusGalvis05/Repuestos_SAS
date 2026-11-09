import { useQuery } from '@tanstack/react-query'
import { ArrowRight, Check, Database, LockKeyhole, Users, ShieldCheck } from 'lucide-react'
import { Link } from 'react-router-dom'
import { useAuth } from '../auth'
import { api } from '../lib/api'

export default function Home() {
  const { user } = useAuth()
  const health = useQuery({
    queryKey: ['ready'],
    queryFn: async () => (await api.get<{ status: string }>('/ready')).data,
    retry: 1,
  })
  const canManage = user?.permissions.includes('users.manage')
  return (
    <>
      <div className="page-heading">
        <div>
          <span className="eyebrow">TU CENTRO DE TRABAJO</span>
          <h1>Todo empieza con orden.</h1>
          <p>Hola, {user?.full_name.split(' ')[0]}. Este es tu espacio en JG Repuestos.</p>
        </div>
        <span className="phase-tag">Fase 01 · Fundamentos</span>
      </div>
      <section className="welcome-panel">
        <div>
          <span className="eyebrow">UNA BASE PARA CRECER</span>
          <h2>
            El control comienza
            <br />
            con un acceso seguro.
          </h2>
          <p>
            Gestiona quién forma parte de tu equipo y qué puede hacer.
            <br />
            La operación comercial se incorporará por etapas.
          </p>
          <Link className="light-button" to={canManage ? '/usuarios' : '/perfil'}>
            {canManage ? 'Administrar equipo' : 'Ver mi perfil'}
            <ArrowRight size={17} />
          </Link>
        </div>
        <div className="welcome-art" aria-hidden="true">
          <ShieldCheck size={120} strokeWidth={1} />
          <span>JG / ESPACIO PROTEGIDO</span>
        </div>
      </section>
      <div className="section-title">
        <h2>Tu sistema, en marcha</h2>
        <span>Estado actual</span>
      </div>
      <div className="status-grid">
        <article className="card">
          <span className="card-icon">
            <Database size={21} />
          </span>
          <span className={`status-pill ${health.isError ? 'warning' : ''}`}>
            {health.isPending ? 'Verificando' : health.isError ? 'Revisar conexión' : 'Conectada'}
          </span>
          <h3>Base de datos</h3>
          <p>
            {health.isError
              ? 'No se pudo comprobar PostgreSQL. Revisa la conexión con el servidor.'
              : 'Conexión de la API con PostgreSQL y esquema de usuarios.'}
          </p>
        </article>
        <article className="card">
          <span className="card-icon">
            <LockKeyhole size={21} />
          </span>
          <span className="status-pill">Sesión activa</span>
          <h3>Acceso personal</h3>
          <p>Tu sesión está protegida. Puedes consultar y revocar tus accesos desde el perfil.</p>
          <Link to="/perfil">
            Revisar mi cuenta <ArrowRight size={15} />
          </Link>
        </article>
        <article className="card">
          <span className="card-icon">
            <Users size={21} />
          </span>
          <span className="status-pill">Por permisos</span>
          <h3>Equipo y roles</h3>
          <p>
            {canManage
              ? 'Invita a tu equipo creando sus cuentas y asignando el rol adecuado.'
              : 'Tu cuenta muestra las herramientas autorizadas por el administrador.'}
          </p>
          {canManage && (
            <Link to="/usuarios">
              Ver usuarios <ArrowRight size={15} />
            </Link>
          )}
        </article>
      </div>
      <section className="next-panel">
        <div>
          <span className="eyebrow">EL CAMINO QUE SIGUE</span>
          <h3>Construido paso a paso.</h3>
          <p>Los módulos comerciales se habilitarán al completar y validar cada fase.</p>
        </div>
        <ol className="roadmap">
          <li className="done">
            <Check size={15} />
            <span>
              01<small>Fundamentos</small>
            </span>
          </li>
          <li>
            <span>
              02<small>Catálogos</small>
            </span>
          </li>
          <li>
            <span>
              03<small>Proveedores</small>
            </span>
          </li>
          <li>
            <span>
              04–07<small>Operación y calidad</small>
            </span>
          </li>
        </ol>
      </section>
    </>
  )
}
