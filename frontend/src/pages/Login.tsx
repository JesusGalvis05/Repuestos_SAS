import { useState } from 'react'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { Navigate } from 'react-router-dom'
import { ArrowUpRight, ShieldCheck, Eye, EyeOff, Wrench } from 'lucide-react'
import { useAuth } from '../auth'
import { errorMessage } from '../lib/api'
import { ErrorBox } from '../components/ui'

const schema = z.object({
  email: z.email('Ingrese un correo válido.'),
  password: z.string().min(1, 'Ingrese su contraseña.'),
})
type Values = z.infer<typeof schema>

export default function Login() {
  const { user, login } = useAuth()
  const [error, setError] = useState('')
  const [show, setShow] = useState(false)
  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm<Values>({ resolver: zodResolver(schema) })
  if (user) return <Navigate to="/" replace />
  return (
    <main className="login-page">
      <section className="login-story">
        <a className="brand" href="/">
          <span className="brand-mark">
            JG<span>↗</span>
          </span>
          <span>
            REPUESTOS<small>GESTIÓN COMERCIAL</small>
          </span>
        </a>
        <div className="story-content">
          <span className="eyebrow">CADA PIEZA CUENTA.</span>
          <h1>
            Tu negocio,
            <br />
            en buena
            <br />
            <em>dirección.</em>
          </h1>
          <p>
            Un solo lugar para organizar tu operación.
            <br />
            Más claridad para tomar la próxima decisión.
          </p>
          <div className="part-drawing" aria-hidden="true">
            <div className="gear-ring">
              <Wrench size={106} strokeWidth={1} />
            </div>
            <span className="part-caption">JG / CONTROL Y CONFIANZA</span>
          </div>
        </div>
        <footer>
          JG Repuestos <span>Hecho para el trabajo de cada día.</span>
        </footer>
      </section>
      <section className="login-form-area">
        <div className="login-form-card">
          <div className="secure-label">
            <ShieldCheck size={16} /> ACCESO A TU ESPACIO
          </div>
          <h2>Bienvenido de nuevo</h2>
          <p className="muted">Ingresa con tu cuenta para continuar.</p>
          <form
            onSubmit={handleSubmit(async (values) => {
              setError('')
              try {
                await login(values.email, values.password)
              } catch (e) {
                setError(errorMessage(e))
              }
            })}
            noValidate
          >
            <label htmlFor="email">Correo electrónico</label>
            <input
              id="email"
              type="email"
              autoComplete="username"
              placeholder="nombre@empresa.com"
              {...register('email')}
              aria-invalid={!!errors.email}
              aria-describedby="email-error"
            />
            <span id="email-error" className="field-error">
              {errors.email?.message}
            </span>
            <label htmlFor="password">Contraseña</label>
            <div className="password-field">
              <input
                id="password"
                type={show ? 'text' : 'password'}
                autoComplete="current-password"
                placeholder="Tu contraseña"
                {...register('password')}
                aria-invalid={!!errors.password}
                aria-describedby="password-error"
              />
              <button
                type="button"
                className="icon-button"
                onClick={() => setShow(!show)}
                aria-label={show ? 'Ocultar contraseña' : 'Mostrar contraseña'}
              >
                {show ? <EyeOff size={18} /> : <Eye size={18} />}
              </button>
            </div>
            <span id="password-error" className="field-error">
              {errors.password?.message}
            </span>
            <ErrorBox message={error} />
            <button className="primary login-submit" disabled={isSubmitting}>
              {isSubmitting ? 'Ingresando…' : 'Ingresar al sistema'}
              <ArrowUpRight size={20} />
            </button>
          </form>
          <div className="access-note">
            <ShieldCheck size={20} />
            <p>
              Tu acceso es personal y seguro.
              <br />
              <span>Si necesitas una cuenta, contacta al administrador.</span>
            </p>
          </div>
        </div>
        <footer>
          © {new Date().getFullYear()} JG Repuestos <span>Gestión con confianza.</span>
        </footer>
      </section>
    </main>
  )
}
