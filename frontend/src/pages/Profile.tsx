import { useState } from 'react'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { ShieldCheck, Monitor, KeyRound } from 'lucide-react'
import { useAuth } from '../auth'
import { api, errorMessage } from '../lib/api'
import { ErrorBox, Modal, Spinner } from '../components/ui'
import type { Session } from '../types'

const schema = z
  .object({
    current_password: z.string().min(1, 'Ingrese su contraseña actual.'),
    new_password: z.string().min(12, 'Use al menos 12 caracteres.').max(128),
    confirm: z.string(),
  })
  .refine((data) => data.new_password === data.confirm, {
    path: ['confirm'],
    message: 'Las contraseñas no coinciden.',
  })
type Values = z.infer<typeof schema>
const date = (value: string) =>
  new Intl.DateTimeFormat('es-CO', {
    dateStyle: 'medium',
    timeStyle: 'short',
    timeZone: 'America/Bogota',
  }).format(new Date(value))

export default function Profile() {
  const { user, reload } = useAuth()
  const cache = useQueryClient()
  const [changing, setChanging] = useState(false)
  const [revoking, setRevoking] = useState<string | null>(null)
  const [message, setMessage] = useState('')
  const sessions = useQuery({
    queryKey: ['sessions'],
    queryFn: async () => (await api.get<Session[]>('/auth/sessions')).data,
  })
  const form = useForm<Values>({ resolver: zodResolver(schema) })
  const change = useMutation({
    mutationFn: async ({ current_password, new_password }: Values) =>
      api.post('/auth/change-password', { current_password, new_password }),
    onSuccess: async () => {
      setChanging(false)
      setMessage('Contraseña actualizada. Inicia sesión con tu nueva contraseña.')
      await reload().catch(() => {})
    },
  })
  const revoke = useMutation({
    mutationFn: async () => api.delete(`/auth/sessions/${revoking}`),
    onSuccess: async () => {
      setRevoking(null)
      cache.invalidateQueries({ queryKey: ['sessions'] })
      await reload().catch(() => {})
    },
  })
  return (
    <>
      <div className="page-heading">
        <div>
          <span className="eyebrow">TU ESPACIO PERSONAL</span>
          <h1>Mi cuenta</h1>
          <p>Consulta tu información y mantén protegido tu acceso.</p>
        </div>
      </div>
      {message && <p role="status">{message}</p>}
      <div className="profile-grid">
        <section className="card profile-card">
          <span className="avatar large">{user?.full_name.slice(0, 1).toUpperCase()}</span>
          <h2>{user?.full_name}</h2>
          <p>{user?.email}</p>
          <span className="status-pill">Cuenta activa</span>
          <dl>
            <dt>Roles asignados</dt>
            <dd>
              {user?.roles
                .map(
                  (r) =>
                    ({
                      admin: 'Administrador',
                      partner: 'Socio',
                      seller: 'Vendedor',
                      inventory: 'Inventario',
                    })[r] || r,
                )
                .join(', ')}
            </dd>
            <dt>Último inicio de sesión</dt>
            <dd>{user?.last_login_at ? date(user.last_login_at) : 'Sin registro'}</dd>
            <dt>Zona horaria de visualización</dt>
            <dd>Colombia · America/Bogota</dd>
          </dl>
          <button
            className="secondary full"
            onClick={() => {
              change.reset()
              setChanging(true)
            }}
          >
            <KeyRound size={17} /> Cambiar contraseña
          </button>
        </section>
        <section className="card sessions-card">
          <div className="section-title">
            <h2>Sesiones activas</h2>
            <ShieldCheck size={22} />
          </div>
          <p className="muted">Cierra los accesos que ya no reconozcas o no necesites.</p>
          {sessions.isPending ? (
            <Spinner />
          ) : sessions.isError ? (
            <ErrorBox message={errorMessage(sessions.error)} />
          ) : (
            <ul className="session-list">
              {sessions.data.map((s) => (
                <li key={s.id}>
                  <Monitor size={24} />
                  <div>
                    <strong>Sesión web</strong>
                    <p title={s.user_agent}>{s.user_agent || 'Dispositivo sin identificar'}</p>
                    <small>
                      Inicio: {date(s.created_at)}
                      <br />
                      Vence: {date(s.expires_at)}
                    </small>
                  </div>
                  <button
                    className="text-button danger"
                    onClick={() => {
                      revoke.reset()
                      setRevoking(s.id)
                    }}
                  >
                    Revocar
                  </button>
                </li>
              ))}
            </ul>
          )}
        </section>
      </div>
      <Modal
        open={changing}
        onOpenChange={setChanging}
        title="Cambiar contraseña"
        description="Todas tus sesiones se cerrarán al confirmar. Usa al menos 12 caracteres."
      >
        <form onSubmit={form.handleSubmit((values) => change.mutate(values))} noValidate>
          <label htmlFor="current">Contraseña actual</label>
          <input
            id="current"
            type="password"
            autoComplete="current-password"
            {...form.register('current_password')}
          />
          <span className="field-error">{form.formState.errors.current_password?.message}</span>
          <label htmlFor="next">Nueva contraseña</label>
          <input
            id="next"
            type="password"
            autoComplete="new-password"
            {...form.register('new_password')}
          />
          <span className="field-error">{form.formState.errors.new_password?.message}</span>
          <label htmlFor="confirm">Repetir nueva contraseña</label>
          <input
            id="confirm"
            type="password"
            autoComplete="new-password"
            {...form.register('confirm')}
          />
          <span className="field-error">{form.formState.errors.confirm?.message}</span>
          <ErrorBox message={change.isError ? errorMessage(change.error) : ''} />
          <button className="primary full" disabled={change.isPending}>
            {change.isPending ? 'Actualizando…' : 'Confirmar cambio'}
          </button>
        </form>
      </Modal>
      <Modal
        open={!!revoking}
        onOpenChange={(v) => {
          if (!v) setRevoking(null)
        }}
        title="¿Revocar esta sesión?"
        description="Se cerrará el acceso del dispositivo seleccionado. Si es tu sesión actual, tendrás que ingresar nuevamente."
      >
        <ErrorBox message={revoke.isError ? errorMessage(revoke.error) : ''} />
        <button
          className="primary full"
          onClick={() => revoke.mutate()}
          disabled={revoke.isPending}
        >
          {revoke.isPending ? 'Revocando…' : 'Confirmar revocación'}
        </button>
      </Modal>
    </>
  )
}
