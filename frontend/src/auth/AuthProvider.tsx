import { onAuthStateChanged, signInWithPopup, signOut, type User as FirebaseUser } from 'firebase/auth'
import { useCallback, useEffect, useMemo, useState, type ReactNode } from 'react'

import { AuthContext, type AuthContextValue, type LifeAuthUser } from './AuthContext'
import { getFirebaseRuntime, isFirebaseConfigured, isTestAuthConfigured, testAuthToken } from '../lib/firebase'

function publicUser(user: FirebaseUser): LifeAuthUser {
  return {
    uid: user.uid,
    email: user.email,
    displayName: user.displayName,
    photoURL: user.photoURL,
  }
}

function testUser(): LifeAuthUser {
  return {
    uid: 'test-user',
    email: 'test@ariva.local',
    displayName: 'Ariva Test User',
    photoURL: null,
  }
}

export function AuthProvider({ children }: { children: ReactNode }) {
  const [firebaseUser, setFirebaseUser] = useState<FirebaseUser | null>(null)
  const [testSignedIn, setTestSignedIn] = useState(isTestAuthConfigured())
  const [authLoading, setAuthLoading] = useState(isFirebaseConfigured() && !isTestAuthConfigured())

  useEffect(() => {
    if (isTestAuthConfigured()) {
      return
    }
    const runtime = getFirebaseRuntime()
    if (!runtime) {
      return
    }
    return onAuthStateChanged(runtime.auth, (nextUser) => {
      setFirebaseUser(nextUser)
      setAuthLoading(false)
    })
  }, [])

  const getToken = useCallback(async () => {
    const token = testAuthToken()
    if (token && testSignedIn) return token
    if (!firebaseUser) return null
    return firebaseUser.getIdToken()
  }, [firebaseUser, testSignedIn])

  const signIn = useCallback(async () => {
    if (isTestAuthConfigured()) {
      setTestSignedIn(true)
      return
    }
    const runtime = getFirebaseRuntime()
    if (!runtime) return
    await signInWithPopup(runtime.auth, runtime.provider)
  }, [])

  const handleSignOut = useCallback(async () => {
    if (isTestAuthConfigured()) {
      setTestSignedIn(false)
      return
    }
    const runtime = getFirebaseRuntime()
    if (runtime) await signOut(runtime.auth)
  }, [])

  const value = useMemo<AuthContextValue>(() => {
    const user = testAuthToken() && testSignedIn ? testUser() : firebaseUser ? publicUser(firebaseUser) : null
    return {
      authConfigured: isFirebaseConfigured() || isTestAuthConfigured(),
      authLoading,
      user,
      getToken,
      signIn,
      signOut: handleSignOut,
    }
  }, [authLoading, firebaseUser, getToken, handleSignOut, signIn, testSignedIn])

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}
