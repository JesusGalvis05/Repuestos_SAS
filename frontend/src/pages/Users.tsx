import { useState } from 'react'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { Plus, Search, Users as UsersIcon, ChevronLeft, ChevronRight } from 'lucide-react'
import { api, errorMessage } from '../lib/api'
import { ErrorBox, Modal, Spinner } from '../components/ui'
import type { Role, User, UserPage } from '../types'

const schema = z.object({
  full_name: z.string().trim().min(2, 'Ingrese el nombre completo.').max(120),
  email: z.email('Correo inválido.'),
  password: z.string().min(12, 'Use al menos 12 caracteres.').max(128),
  roles: z.array(z.string()).min(1, 'Seleccione un rol.'),
})
type Values = z.infer<typeof schema>

export default function Users() {
  const cache = useQueryClient()
  const [page, setPage] = useState(1)
  const [search, setSearch] = useState('')
  const [draftSearch, setDraftSearch] = useState('')
  const [creating, setCreating] = useState(false)
  const [editing, setEditing] = useState<User | null>(null)
  const [editRoles, setEditRoles] = useState<string[]>([])
  const [editActive, setEditActive] = useState(true)
  const [confirming, setConfirming] = useState(false)
  const users = useQuery({
    queryKey: ['users', page, search],
    queryFn: async () =>
      (await api.get<UserPage>('/users', { params: { page, search, page_size: 10 } })).data,
  })
  const roles = useQuery({
    queryKey: ['roles'],
    queryFn: async () => (await api.get<Role[]>('/roles')).data,
  })
  const {
    register,
    handleSubmit,
    reset,
    formState: { errors },
  } = useForm<Values>({ resolver: zodResolver(schema), defaultValues: { roles: ['seller'] } })
  const create = useMutation({
    mutationFn: async (data: Values) => api.post('/users', data),
    onSuccess: () => {
      cache.invalidateQueries({ queryKey: ['users'] })
      setCreating(false)
      reset()
    },
  })
  const update = useMutation({
    mutationFn: async () =>
      api.patch(`/users/${editing!.id}`, { active: editActive, roles: editRoles }),
    onSuccess: () => {
      cache.invalidateQueries({ queryKey: ['users'] })
      setEditing(null)
      setConfirming(false)
    },
  })
  const roleName = (code: string) => roles.data?.find((r) => r.code === code)?.name || code
  return (
    <>
      <div className="page-heading">
        <div>
          <span className="eyebrow">PERSONAS Y PERMISOS</span>
          <h1>Tu equipo</h1>
          <p>Cuentas personales, responsabilidades claras.</p>
        </div>
        <button
          className="primary"
          onClick={() => {
            create.reset()
            setCreating(true)
          }}
        >
          <Plus size={18} /> Crear usuario
        </button>
      </div>
      <ErrorBox message={roles.isError ? errorMessage(roles.error) : ''} />
      <section className="table-card">
        <div className="table-toolbar">
          <div>
            <h2>Usuarios del sistema</h2>
            <span className="muted">
              {users.data ? `${users.data.total} cuentas registradas` : 'Consultando cuentas…'}
            </span>
          </div>
          <form
            className="search-field"
            onSubmit={(e) => {
              e.preventDefault()
              setPage(1)
              setSearch(draftSearch)
            }}
          >
            <Search size={18} />
            <input
              aria-label="Buscar por nombre o correo"
              placeholder="Buscar nombre o correo"
              value={draftSearch}
              onChange={(e) => setDraftSearch(e.target.value)}
            />
            <button type="submit">Buscar</button>
          </form>
        </div>
        {users.isPending ? (
          <Spinner />
        ) : users.isError ? (
          <div className="padded">
            <ErrorBox message={errorMessage(users.error)} />
            <button className="secondary" onClick={() => users.refetch()}>
              Reintentar
            </button>
          </div>
        ) : (
          <>
            <div className="table-scroll">
              <table>
                <thead>
                  <tr>
                    <th>Usuario</th>
                    <th>Rol</th>
                    <th>Estado</th>
                    <th>Último acceso</th>
                    <th>
                      <span className="sr-only">Acciones</span>
                    </th>
                  </tr>
                </thead>
                <tbody>
                  {users.data.items.map((u) => (
                    <tr key={u.id}>
                      <td>
                        <div className="user-cell">
                          <span className="avatar">{u.full_name.slice(0, 1).toUpperCase()}</span>
                          <span>
                            <strong>{u.full_name}</strong>
                            <small>{u.email}</small>
                          </span>
                        </div>
                      </td>
                      <td>{u.roles.map(roleName).join(', ')}</td>
                      <td>
                        <span className={`status-pill ${!u.active ? 'inactive' : ''}`}>
                          {u.active ? 'Activo' : 'Inactivo'}
                        </span>
                      </td>
                      <td>
                        {u.last_login_at
                          ? new Intl.DateTimeFormat('es-CO', {
                              timeZone: 'America/Bogota',
                              dateStyle: 'medium',
                            }).format(new Date(u.last_login_at))
                          : 'Sin accesos'}
                      </td>
                      <td>
                        <button
                          className="text-button"
                          onClick={() => {
                            update.reset()
                            setConfirming(false)
                            setEditing(u)
                            setEditRoles(u.roles)
                            setEditActive(u.active)
                          }}
                        >
                          Administrar
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
            {!users.data.items.length && (
              <div className="empty">
                <UsersIcon size={30} />
                <h3>No encontramos usuarios</h3>
                <p>Prueba con otro nombre o correo electrónico.</p>
              </div>
            )}
            <div className="pagination">
              <span>
                Página {page} de {Math.max(1, Math.ceil(users.data.total / 10))}
              </span>
              <div>
                <button
                  className="icon-button"
                  aria-label="Página anterior"
                  disabled={page === 1}
                  onClick={() => setPage(page - 1)}
                >
                  <ChevronLeft size={20} />
                </button>
                <button
                  className="icon-button"
                  aria-label="Página siguiente"
                  disabled={page * 10 >= users.data.total}
                  onClick={() => setPage(page + 1)}
                >
                  <ChevronRight size={20} />
                </button>
              </div>
            </div>
          </>
        )}
      </section>
      <Modal
        open={creating}
        onOpenChange={setCreating}
        title="Crear usuario"
        description="La cuenta será personal. Comparte la contraseña inicial mediante un canal seguro."
      >
        <form onSubmit={handleSubmit((data) => create.mutate(data))} noValidate>
          <label htmlFor="new-name">Nombre completo</label>
          <input id="new-name" {...register('full_name')} autoComplete="name" />
          <span className="field-error">{errors.full_name?.message}</span>
          <label htmlFor="new-email">Correo electrónico</label>
          <input id="new-email" type="email" {...register('email')} autoComplete="off" />
          <span className="field-error">{errors.email?.message}</span>
          <label htmlFor="new-password">Contraseña inicial</label>
          <input
            id="new-password"
            type="password"
            {...register('password')}
            autoComplete="new-password"
          />
          <span className="field-error">{errors.password?.message}</span>
          <label htmlFor="new-role">Rol</label>
          <select
            id="new-role"
            {...register('roles', { setValueAs: (v) => (Array.isArray(v) ? v : [v]) })}
            multiple
          >
            {roles.data?.map((r) => (
              <option key={r.code} value={r.code}>
                {r.name}
              </option>
            ))}
          </select>
          <span className="field-error">{errors.roles?.message}</span>
          <ErrorBox message={create.isError ? errorMessage(create.error) : ''} />
          <button className="primary full" disabled={create.isPending || !roles.data}>
            {create.isPending ? 'Creando…' : 'Crear cuenta'}
          </button>
        </form>
      </Modal>
      <Modal
        open={!!editing}
        onOpenChange={(v) => {
          if (!v) setEditing(null)
        }}
        title={confirming ? 'Confirmar cambio de acceso' : 'Administrar acceso'}
        description={
          confirming
            ? 'Este cambio cerrará todas las sesiones del usuario, incluida la tuya si editas tu cuenta.'
            : `${editing?.full_name || ''} · ${editing?.email || ''}`
        }
      >
        <form
          onSubmit={(e) => {
            e.preventDefault()
            if (!confirming) setConfirming(true)
            else update.mutate()
          }}
        >
          <label htmlFor="edit-role">Rol</label>
          <select
            id="edit-role"
            multiple
            value={editRoles}
            onChange={(e) => {
              setEditRoles(Array.from(e.target.selectedOptions, (option) => option.value))
              setConfirming(false)
            }}
            disabled={confirming}
          >
            {roles.data?.map((r) => (
              <option key={r.code} value={r.code}>
                {r.name}
              </option>
            ))}
          </select>
          <label className="checkbox-row">
            <input
              type="checkbox"
              checked={editActive}
              disabled={confirming}
              onChange={(e) => setEditActive(e.target.checked)}
            />{' '}
            Cuenta activa
          </label>
          <ErrorBox message={update.isError ? errorMessage(update.error) : ''} />
          <button
            className="primary full"
            disabled={update.isPending || !roles.data || !editRoles.length}
          >
            {update.isPending
              ? 'Guardando…'
              : confirming
                ? 'Confirmar y guardar'
                : 'Revisar cambios'}
          </button>
        </form>
      </Modal>
    </>
  )
}
