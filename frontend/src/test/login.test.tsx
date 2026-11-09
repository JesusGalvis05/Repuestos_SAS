import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { MemoryRouter } from 'react-router-dom'
import { describe, expect, it, vi } from 'vitest'
import Login from '../pages/Login'

const login = vi.fn()
vi.mock('../auth', () => ({ useAuth: () => ({ user: null, login }) }))

describe('Inicio de sesión', () => {
  it('valida el correo antes de llamar al servidor', async () => {
    render(
      <MemoryRouter>
        <Login />
      </MemoryRouter>,
    )
    await userEvent.type(screen.getByLabelText('Correo electrónico'), 'invalid')
    await userEvent.type(screen.getByLabelText('Contraseña', { exact: true }), 'password')
    await userEvent.click(screen.getByRole('button', { name: /Ingresar al sistema/i }))
    expect(await screen.findByText('Ingrese un correo válido.')).toBeInTheDocument()
    expect(login).not.toHaveBeenCalled()
  })
  it('permite mostrar y ocultar la contraseña', async () => {
    render(
      <MemoryRouter>
        <Login />
      </MemoryRouter>,
    )
    const input = screen.getByLabelText('Contraseña', { exact: true })
    expect(input).toHaveAttribute('type', 'password')
    await userEvent.click(screen.getByRole('button', { name: 'Mostrar contraseña' }))
    expect(input).toHaveAttribute('type', 'text')
    await userEvent.click(screen.getByRole('button', { name: 'Ocultar contraseña' }))
    expect(input).toHaveAttribute('type', 'password')
  })
})
