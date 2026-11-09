export type User = {
  id: string
  email: string
  full_name: string
  active: boolean
  roles: string[]
  permissions: string[]
  last_login_at: string | null
}
export type Tokens = { access_token: string; expires_in: number; user: User }
export type UserPage = { items: User[]; total: number; page: number; page_size: number }
export type Role = { code: string; name: string; permissions: string[] }
export type Session = { id: string; created_at: string; expires_at: string; user_agent: string }
