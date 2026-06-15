import { defineStore } from 'pinia'
import type { SelectMenuItem } from '@nuxt/ui'
import { useOsirApi } from '~/api'
import type { OsirModuleModel } from '~/api/types'

export interface ModuleState {
  modules: string[]
  moduleInfoMap: Record<string, OsirModuleModel>
  isLoading: boolean
  isLoadingInfos: boolean
  error: string | null
  pollInterval: ReturnType<typeof setInterval> | null
}

export const useModuleStore = defineStore('module', {
  state: (): ModuleState => ({
    modules: [],
    moduleInfoMap: {},
    isLoading: false,
    isLoadingInfos: false,
    error: null,
    pollInterval: null,
  }),

  getters: {
    moduleOptions: (state): SelectMenuItem[] =>
      state.modules.map(m => ({ label: m, value: m })),
  },

  actions: {
    getBasename(modulePath: string): string {
      return modulePath.split('/').pop() || modulePath
    },

    getNonProfileModuleOptions(profileModules: string[]): SelectMenuItem[] {
      const profileBasenames = new Set(profileModules.map(this.getBasename))
      return this.modules
        .filter(m => !profileBasenames.has(this.getBasename(m)))
        .map(m => ({ label: m, value: m }))
    },

    getInProfileModuleOptions(profileModules: string[]): SelectMenuItem[] {
      const profileBasenames = new Set(profileModules.map(this.getBasename))
      return this.modules
        .filter(m => profileBasenames.has(this.getBasename(m)))
        .map(m => ({ label: m, value: m }))
    },

    setLoading(loading: boolean) {
      this.isLoading = loading
    },

    setLoadingInfos(loading: boolean) {
      this.isLoadingInfos = loading
    },

    setError(error: string | null) {
      this.error = error
    },

    setModules(modules: string[]) {
      this.modules = modules
    },

    setModuleInfoMap(map: Record<string, OsirModuleModel>) {
      this.moduleInfoMap = map
    },

    async fetchModules() {
      if (this.modules.length) return
      this.setLoading(true)
      this.setError(null)
      try {
        const api = useOsirApi()
        const data = await api.module.list()
        this.setModules(Array.isArray(data.response) ? data.response : [])
      } catch (e) {
        this.setError('Failed to fetch modules')
      } finally {
        this.setLoading(false)
      }
    },

    async fetchModuleInfos() {
      if (!this.modules.length || this.isLoadingInfos) return
      this.setLoadingInfos(true)
      this.setError(null)
      try {
        const api = useOsirApi()
        const snapshot = [...this.modules]
        const result = await api.module.info({ modules: snapshot })
        const next: Record<string, OsirModuleModel> = {}
        if (result.response) {
          for (const [name, info] of Object.entries(result.response)) {
            next[name] = info as unknown as OsirModuleModel
          }
        }
        this.setModuleInfoMap(next)
      } catch (e) {
        this.setError('Failed to fetch module infos')
      } finally {
        this.setLoadingInfos(false)
      }
    },

    async fetchModuleInfo(moduleName: string) {
      if (this.moduleInfoMap[moduleName]) return
      this.setLoadingInfos(true)
      this.setError(null)
      try {
        const api = useOsirApi()
        const result = await api.module.info({ modules: [moduleName] })
        if (result.response && result.response[moduleName]) {
          this.moduleInfoMap[moduleName] = result.response[moduleName] as unknown as OsirModuleModel
        }
      } catch (e) {
        this.setError('Failed to fetch module info')
      } finally {
        this.setLoadingInfos(false)
      }
    },

    async refresh() {
      this.setModules([])
      this.setModuleInfoMap({})
      this.setLoadingInfos(false)
      await this.fetchModules()
      this.fetchModuleInfos()
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
