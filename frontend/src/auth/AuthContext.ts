import { createContext } from 'react'

export interface LifeAuthUser {
  uid: string
  email: string | null
  displayName: string | null
  photoURL: string | null
}

export interface AuthContextValue {
  authConfigured: boolean
  authLoading: boolean
  user: LifeAuthUser | null
  getToken: () => Promise<string | null>
  signIn: () => Promise<void>
  signOut: () => Promise<void>
}

export const AuthContext = createContext<AuthContextValue | null>(null)
