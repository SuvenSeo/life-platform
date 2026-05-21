import { initializeApp, type FirebaseApp } from 'firebase/app'
import { getAuth, GoogleAuthProvider, type Auth } from 'firebase/auth'

type FirebaseRuntime = {
  app: FirebaseApp
  auth: Auth
  provider: GoogleAuthProvider
}

let runtime: FirebaseRuntime | null = null

export function isTestAuthConfigured() {
  return Boolean(testAuthToken())
}

export function isFirebaseConfigured() {
  return Boolean(
    import.meta.env.VITE_FIREBASE_API_KEY &&
      import.meta.env.VITE_FIREBASE_AUTH_DOMAIN &&
      import.meta.env.VITE_FIREBASE_PROJECT_ID &&
      import.meta.env.VITE_FIREBASE_APP_ID,
  )
}

export function getFirebaseRuntime(): FirebaseRuntime | null {
  if (!isFirebaseConfigured()) return null
  if (runtime) return runtime
  const app = initializeApp({
    apiKey: import.meta.env.VITE_FIREBASE_API_KEY,
    appId: import.meta.env.VITE_FIREBASE_APP_ID,
    authDomain: import.meta.env.VITE_FIREBASE_AUTH_DOMAIN,
    messagingSenderId: import.meta.env.VITE_FIREBASE_MESSAGING_SENDER_ID,
    projectId: import.meta.env.VITE_FIREBASE_PROJECT_ID,
  })
  runtime = {
    app,
    auth: getAuth(app),
    provider: new GoogleAuthProvider(),
  }
  return runtime
}

export function testAuthToken() {
  return import.meta.env.VITE_LIFE_TEST_AUTH_TOKEN || (globalThis as { __LIFELK_TEST_AUTH_TOKEN__?: string }).__LIFELK_TEST_AUTH_TOKEN__ || null
}
