import { defineStore } from 'pinia'
import type { SelectMenuItem } from '@nuxt/ui'
import { useOsirApi } from '~/api'
import type { OsirDbStatusModel, PaginatedTaskResponse } from '~/api/types'

export type TaskStatus = OsirDbStatusModel

export interface TaskRow {
  task_id: string
  case_name: string
  agent: string
  module: string
  status: OsirDbStatusModel
  timestamp: string
  start_time: string | null
  duration_seconds: number | null
  input: string
}

export interface PaginationState {
  page: number
  pageSize: number
  total: number
  totalPages: number
}

function ensureNumber(value: unknown): number {
  return typeof value === 'number' ? value : Number(value) || 0
}



interface TaskState {
  tasks: TaskRow[]
  isLoading: boolean
  error: string | null
  pollInterval: ReturnType<typeof setInterval> | null
  pagination: PaginationState
}

export const useTaskStore = defineStore('task', {
  state: (): TaskState => ({
    tasks: [],
    isLoading: false,
    error: null,
    pollInterval: null,
    pagination: {
      page: 1,
      pageSize: 20,
      total: 0,
      totalPages: 0
    }
  }),

  getters: {
    caseOptions: (state): SelectMenuItem[] => [
      { label: 'All cases', value: 'all' },
      ...[...new Set(state.tasks.map(t => t.case_name))].map(c => ({ label: c, value: c })),
    ],
    moduleOptions: (state): SelectMenuItem[] => [
      { label: 'All modules', value: 'all' },
      ...[...new Set(state.tasks.map(t => t.module))].map(m => ({ label: m, value: m })),
    ],
  },

  actions: {
    async fetchTasks(
      caseNames: string[] | null = null,
      status: string | null = null,
      input: string | null = null,
      page: number = 1,
      pageSize: number = 20,
      handlerId: string | null = null,
      module: string | null = null
    ) {
      this.isLoading = true
      this.error = null
      try {
        const api = useOsirApi()
        const caseStore = useCaseStore()
        
        // Use case store to create UUID to name mapping
        const caseUuidToName = new Map<string, string>()
        for (const c of caseStore.cases) {
          caseUuidToName.set(c.case_uuid, c.name)
        }
        
        let result: { response: PaginatedTaskResponse }
        
        // If handlerId is provided, fetch tasks for that specific handler
        if (handlerId) {
          result = await api.handler.get_tasks(handlerId, page, pageSize, status, module)
        } else {
          // Single API call for all tasks with pagination and filters
          result = await api.case.tasksAll(caseNames, status, input, page, pageSize)
        }
        
        const paginatedData: PaginatedTaskResponse = result.response
        
        const rows: TaskRow[] = []
        for (const t of paginatedData.tasks) {
          rows.push({
            task_id:          t.task_id,
            case_name:        caseUuidToName.get(String(t.case_uuid)) || 'Unknown',
            agent:            t.agent,
            module:           t.module,
            status:           t.processing_status!,
            timestamp:        t.timestamp,
            start_time:       t.trace?.start_time ?? null,
            duration_seconds: t.trace?.duration_seconds ?? null,
            input:            t.input,
          })
        }
        
        this.tasks = rows
        this.pagination = {
          page,
          pageSize,
          total: ensureNumber(paginatedData.total),
          totalPages: ensureNumber(paginatedData.total_pages)
        }
      } catch (e) {
        this.error = 'Failed to fetch tasks'
        console.error('Error fetching tasks:', e)
      } finally {
        this.isLoading = false
      }
    },

    setPage(page: number) {
      this.pagination.page = page
    },

    setPageSize(pageSize: number) {
      this.pagination.pageSize = pageSize
      this.pagination.page = 1
    },

    startPolling(
      caseNames: string[] | null = null,
      status: string | null = null,
      input: string | null = null,
      page: number = 1,
      pageSize: number = 20,
      ms = 10000,
      handlerId: string | null = null,
      module: string | null = null
    ) {
      this.fetchTasks(caseNames, status, input, page, pageSize, handlerId, module)
      this.stopPolling()
      this.pollInterval = setInterval(() => 
        this.fetchTasks(caseNames, status, input, page, pageSize, handlerId, module), ms)
    },

    stopPolling() {
      if (this.pollInterval) {
        clearInterval(this.pollInterval)
        this.pollInterval = null
      }
    },
  },
})
