import { defineStore } from 'pinia'
import type { SelectMenuItem } from '@nuxt/ui'
import { useOsirApi } from '~/api'
import type { OsirDbCaseModel } from '~/api/types'

export interface CaseState {
  cases: OsirDbCaseModel[]
  currentCase: OsirDbCaseModel | null
  isLoading: boolean
  error: string | null
}

export const useCaseStore = defineStore('case', {
  state: (): CaseState => ({
    cases: [],
    currentCase: null,
    isLoading: false,
    error: null,
  }),

  getters: {
    caseOptions: (state): SelectMenuItem[] =>
      state.cases.map(c => ({ label: c.name, value: c.case_uuid })),
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
  },
})
