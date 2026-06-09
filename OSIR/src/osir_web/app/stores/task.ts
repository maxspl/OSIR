import { defineStore } from 'pinia'
import type { SelectMenuItem } from '@nuxt/ui'
import { useOsirApi } from '~/api'
import type { OsirDbStatusModel } from '~/api/types'

export type TaskStatus = 'task_created' | 'processing_started' | 'processing_done' | 'processing_failed'

export interface TaskRow {
  task_id: string
  case_name: string
  agent: string
  module: string
  status: TaskStatus
  timestamp: string
  start_time: string | null
  duration_seconds: number | null
  input: string
}

function mapStatus(s?: OsirDbStatusModel | null): TaskStatus {
  switch (s) {
    case 'task_created':       return 'task_created'
    case 'processing_started': return 'processing_started'
    case 'processing_done':    return 'processing_done'
    case 'processing_failed':  return 'processing_failed'
    default:                   return 'task_created'
  }
}

interface TaskState {
  tasks: TaskRow[]
  isLoading: boolean
  error: string | null
  pollInterval: ReturnType<typeof setInterval> | null
}

export const useTaskStore = defineStore('task', {
  state: (): TaskState => ({
    tasks: [],
    isLoading: false,
    error: null,
    pollInterval: null,
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
    async fetchTasks(caseNames: string[]) {
      if (!caseNames.length) return
      this.isLoading = true
      this.error = null
      try {
        const api = useOsirApi()
        const results = await Promise.allSettled(
          caseNames.map(name =>
            api.case.tasks(name).then(r => ({ name, tasks: r.response ?? [] }))
          )
        )
        const rows: TaskRow[] = []
        for (const result of results) {
          if (result.status === 'fulfilled') {
            for (const t of result.value.tasks) {
              // console.log(t)
              rows.push({
                task_id:          t.task_id,
                case_name:        result.value.name,
                agent:            t.agent,
                module:           t.module,
                status:           mapStatus(t.processing_status),
                timestamp:        t.timestamp,
                start_time:       t.trace?.start_time ?? null,
                duration_seconds: t.trace?.duration_seconds ?? null,
                input:            t.input,
              })
            }
          }
        }
        this.tasks = rows
      } catch (e) {
        this.error = 'Failed to fetch tasks'
      } finally {
        this.isLoading = false
      }
    },

    startPolling(caseNames: string[], ms = 10000) {
      this.fetchTasks(caseNames)
      this.stopPolling()
      this.pollInterval = setInterval(() => this.fetchTasks(caseNames), ms)
    },

    stopPolling() {
      if (this.pollInterval) {
        clearInterval(this.pollInterval)
        this.pollInterval = null
      }
    },
  },
})
