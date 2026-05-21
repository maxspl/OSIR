import { defineStore } from 'pinia'
import type { SelectMenuItem } from '@nuxt/ui'
import { useOsirApi } from '~/api'
import type { OsirProfileModel } from '~/api/types'

export interface ProfileState {
  profiles: string[]
  profileInfoMap: Record<string, OsirProfileModel>
  isLoading: boolean
  error: string | null
  pollInterval: ReturnType<typeof setInterval> | null
}

export const useProfileStore = defineStore('profile', {
  state: (): ProfileState => ({
    profiles: [],
    profileInfoMap: {},
    isLoading: false,
    error: null,
    pollInterval: null,
  }),

  getters: {
    profileOptions: (state): SelectMenuItem[] =>
      state.profiles.map(p => ({ label: p, value: p })),
  },

  actions: {
    setLoading(loading: boolean) {
      this.isLoading = loading
    },

    setError(error: string | null) {
      this.error = error
    },

    setProfiles(profiles: string[]) {
      this.profiles = profiles
    },

    setProfileInfoMap(map: Record<string, OsirProfileModel>) {
      this.profileInfoMap = map
    },

    async fetchProfiles() {
      if (this.profiles.length) return
      this.setLoading(true)
      this.setError(null)
      try {
        const api = useOsirApi()
        const data = await api.profile.list()
        this.setProfiles(data.response ?? [])
      } catch (e) {
        this.setError('Failed to fetch profiles')
      } finally {
        this.setLoading(false)
      }
    },

    async fetchProfileInfo(profileName: string) {
      if (this.profileInfoMap[profileName]) return
      this.setLoading(true)
      this.setError(null)
      try {
        const api = useOsirApi()
        const data = await api.profile.info(profileName)
        if (data.response) {
          this.profileInfoMap[profileName] = data.response
        }
      } catch (e) {
        this.setError('Failed to fetch profile info')
      } finally {
        this.setLoading(false)
      }
    },

    async fetchAllProfileInfos() {
      if (!this.profiles.length) return
      this.setLoading(true)
      this.setError(null)
      try {
        const api = useOsirApi()
        const snapshot = [...this.profiles]
        const promises = snapshot.map(profileName => api.profile.info(profileName))
        const results = await Promise.all(promises)
        
        results.forEach((result, index) => {
          if (result.response) {
            this.profileInfoMap[snapshot[index]] = result.response
          }
        })
      } catch (e) {
        this.setError('Failed to fetch all profile infos')
      } finally {
        this.setLoading(false)
      }
    },

    async refresh() {
      this.setProfiles([])
      this.setProfileInfoMap({})
      await this.fetchProfiles()
    },

    startPolling(ms = 5000) {
      this.refresh()
      this.stopPolling()
      this.pollInterval = setInterval(() => this.refresh(), ms)
    },

    stopPolling() {
      if (this.pollInterval) {
        clearInterval(this.pollInterval)
        this.pollInterval = null
      }
    },
  },
})
