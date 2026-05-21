import { defineStore } from 'pinia'
import { useOsirApi } from '~/api'

export interface AuthState {
  user: string | null
  isAuthenticated: boolean
  isLoading: boolean
  error: string | null
}

export const useAuthStore = defineStore('auth', {
  state: (): AuthState => ({
    user: null,
    isAuthenticated: false,
    isLoading: false,
    error: null,
  }),

  getters: {
    currentUser: (state) => state.user,
  },

  actions: {
    setUser(user: string | null) {
      this.user = user
      this.isAuthenticated = !!user
    },

    setLoading(loading: boolean) {
      this.isLoading = loading
    },

    setError(error: string | null) {
      this.error = error
    },

    clearAuth() {
      this.user = null
      this.isAuthenticated = false
      this.error = null
    },

    async checkAuth() {
      this.setLoading(true)
      this.setError(null)
      try {
        const api = useOsirApi()
        const response = await api.auth.check()
        this.setUser(response.response?.user ?? null)
        return this.isAuthenticated
      } catch (e) {
        this.setError('Failed to check authentication')
        this.clearAuth()
        return false
      } finally {
        this.setLoading(false)
      }
    },

    async login(credentials: { username: string; password: string }) {
      this.setLoading(true)
      this.setError(null)
      try {
        const api = useOsirApi()
        const response = await api.auth.login(credentials)
        if (response.response?.success) {
          this.setUser(credentials.username)
          return true
        }
        this.setError('Login failed')
        return false
      } catch (e) {
        this.setError('Login failed')
        this.clearAuth()
        return false
      } finally {
        this.setLoading(false)
      }
    },

    async logout() {
      this.setLoading(true)
      this.setError(null)
      try {
        const api = useOsirApi()
        await api.auth.logout()
        this.clearAuth()
      } catch (e) {
        this.setError('Logout failed')
      } finally {
        this.setLoading(false)
      }
    },
  },
})
