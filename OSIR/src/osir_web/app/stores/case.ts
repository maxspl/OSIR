import { defineStore } from 'pinia'
import { useOsirApi } from '~/api'
import type { OsirDbCaseModel } from '~/api/types'

export interface CaseOption {
  label: string
  value: string
}

export interface CaseState {
  cases: OsirDbCaseModel[]
  currentCase: OsirDbCaseModel | null
  isLoading: boolean
  error: string | null
  pollInterval: ReturnType<typeof setInterval> | null
}

export const useCaseStore = defineStore('case', {
  state: (): CaseState => ({
    cases: [],
    currentCase: null,
    isLoading: false,
    error: null,
    pollInterval: null,
  }),

  getters: {
    // A case whose directory disappeared cannot be processed: keep it out of the
    // selector, but leave it in `cases` so task and handler views still resolve
    // its name from the UUID.
    caseOptions: (state): CaseOption[] =>
      state.cases
        .filter(c => c.exists_on_disk !== false)
        .map(c => ({ label: c.name, value: c.name })),

    missingCases: (state): OsirDbCaseModel[] =>
      state.cases.filter(c => c.exists_on_disk === false),
  },

  actions: {
    setLoading(loading: boolean) {
      this.isLoading = loading
    },

    setError(error: string | null) {
      this.error = error
    },

    setCases(cases: OsirDbCaseModel[]) {
      this.cases = cases
    },

    setCurrentCase(caseItem: OsirDbCaseModel | null) {
      this.currentCase = caseItem
    },

    async fetchCases() {
      if (this.cases.length) return
      this.setLoading(true)
      this.setError(null)
      try {
        const api = useOsirApi()
        const data = await api.case.list()
        this.setCases(data.response ?? [])
      } catch (e) {
        this.setError('Failed to fetch cases')
      } finally {
        this.setLoading(false)
      }
    },

    async refresh() {
      this.setCases([])
      await this.fetchCases()
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
