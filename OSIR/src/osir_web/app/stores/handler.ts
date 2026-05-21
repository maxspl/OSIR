import { defineStore } from 'pinia'
import { useOsirApi } from '~/api'
import type { OsirDbTaskModel, OsirDbHandlerModel, PostHandlerCreateRequest, PostHandlerCreateResponse, PostHandlerAdvancedCreateRequest } from '~/api/types'

export type ProcessingStatus = 'task_created' | 'processing_started' | 'processing_done' | 'processing_failed'

export interface HandlerRow {
  handler_id:        string
  case_name:         string | null
  case_uuid:         string
  modules:           string[]
  task_ids:          string[]
  processing_status: ProcessingStatus
  created_at:        string | null
  task_count:        number
}

export interface ParsedLog {
  timestamp: string
  level:     string
  message:   string
}

export interface TaskDetail {
  task_id:           string
  handler_id:        string
  case_name:         string
  case_uuid:         string
  agent:             string
  module:            string
  fn:                string | null
  processing_status: ProcessingStatus
  start_time:        string | null
  end_time:          string | null
  duration_seconds:  number | null
  input:             string
  output:            string | null
  logs:              ParsedLog[]
}

function mapStatus(s?: string | null): ProcessingStatus {
  switch (s) {
    case 'task_created':       return 'task_created'
    case 'processing_started': return 'processing_started'
    case 'processing_done':    return 'processing_done'
    case 'processing_failed':  return 'processing_failed'
    default:                   return 'task_created'
  }
}

function parseLogLine(line: string): ParsedLog {
  // Format: [LEVEL][YYYY-MM-DD HH:MM:SS,mmm] - File:line - func() - message
  const match = line.match(/^\[(\w+)\]\[([^\]]+)\]\s*-\s*.+\s*-\s*.+\(\)\s*-\s*(.+)$/)
  if (!match) {
    return { level: 'INFO', timestamp: '', message: line.trim() }
  }
  const level = match[1] || 'INFO'
  const timeStr = match[2] || ''
  const timeParts = timeStr.split(' ')
  const rawTime = timeParts[1] || timeParts[0] || ''
  const timestamp = rawTime.split(',')[0] || ''
  const message = (match[3] || line).trim()
  return { level, timestamp, message }
}

function toTaskDetail(t: OsirDbTaskModel, handlerId: string, caseName: string): TaskDetail {
  return {
    task_id:           t.task_id,
    handler_id:        handlerId,
    case_name:         caseName,
    case_uuid:         t.case_uuid,
    agent:             t.agent,
    module:            t.module,
    fn:                t.trace?.function ?? null,
    processing_status: mapStatus(t.processing_status ?? undefined),
    start_time:        t.trace?.start_time ?? null,
    end_time:          t.trace?.end_time ?? null,
    duration_seconds:  t.trace?.duration_seconds ?? null,
    input:             t.input,
    output:            t.output ?? null,
    logs:              (t.trace?.logs ?? []).map(parseLogLine),
  }
}

interface HandlerState {
  handlers:        HandlerRow[]
  tasksByHandler:  Record<string, TaskDetail[]>
  isLoading:       boolean
  isLoadingTasks:  boolean
  error:           string | null
  pollInterval:   NodeJS.Timeout | null
}

export const useHandlerStore = defineStore('handler', {
  state: (): HandlerState => ({
    handlers:       [],
    tasksByHandler: {},
    isLoading:      false,
    isLoadingTasks: false,
    error:          null,
    pollInterval:  null,
  }),

  getters: {
    caseOptions: (state) => [
      { label: 'All cases', value: 'all' },
      ...[...new Set(state.handlers.map(h => h.case_name))].map(n => ({ label: n, value: n })),
    ],
  },

  actions: {
    async fetchHandlers(cases: { name: string; uuid: string }[]) {
      if (!cases.length) return
      this.isLoading = true
      this.error = null
      try {
        const api = useOsirApi()
        const results = await Promise.allSettled(
          cases.map(c =>
            api.case.handlers(c.name).then(r => ({ case_name: c.name, handlers: r.response ?? [] }))
          )
        )
        const rows: HandlerRow[] = []
        for (const result of results) {
          if (result.status === 'fulfilled') {
            for (const h of result.value.handlers) {
              rows.push({
                handler_id:        h.handler_id,
                case_name:         result.value.case_name,
                case_uuid:         h.case_uuid,
                modules:           h.modules,
                task_ids:          h.task_id,
                processing_status: h.processing_status as ProcessingStatus,
                created_at:        h.created_at ?? null,
                task_count:        h.task_id.length,
              })
            }
          }
        }
        this.handlers = rows
      } catch {
        this.error = 'Failed to fetch handlers'
      } finally {
        this.isLoading = false
      }
    },

    async fetchTasksForHandler(handler: HandlerRow) {
      if (!handler.task_ids.length) {
        this.tasksByHandler[handler.handler_id] = []
        return
      }
      this.isLoadingTasks = true
      try {
        const api = useOsirApi()
        const results = await api.handler.get_tasks_logs(handler.handler_id)
        
        const tasks: TaskDetail[] = []
        for (const result of results.response) {
          tasks.push(toTaskDetail(result, handler.handler_id, handler.case_name ?? ''))
        }
        this.tasksByHandler[handler.handler_id] = tasks
      } catch {
        this.error = 'Failed to fetch tasks for handler'
      } finally {
        this.isLoadingTasks = false
      }
    },

    async fetchTaskInfo(taskId: string): Promise<TaskDetail | null> {
      try {
        const api = useOsirApi()
        const r = await api.tasks.info(taskId)
        return r.response ? toTaskDetail(r.response, '', '') : null
      } catch {
        return null
      }
    },

    async refreshHandler(handlerId: string) {
      try {
        const api = useOsirApi()
        const r = await api.handler.status(handlerId)
        if (r.response) {
          const idx = this.handlers.findIndex(h => h.handler_id === handlerId)
          if (idx !== -1) {
            this.handlers[idx] = { ...this.handlers[idx], processing_status: r.response.processing_status } as HandlerRow
          }
        }
      } catch {
        this.error = 'Failed to refresh handler'
      }
    },

    async createHandler(request: PostHandlerCreateRequest): Promise<OsirDbHandlerModel | null> {
      this.isLoading = true
      this.error = null
      try {
        const api = useOsirApi()
        const response = await api.handler.create(request)
        if (response.response) {
          // Add the new handler to the list
          this.handlers.unshift({
            handler_id:        response.response.handler_id,
            case_name:         response.response.case_name ?? request.case_name,
            case_uuid:         response.response.case_uuid,
            modules:           response.response.modules ?? [],
            task_ids:          response.response.task_id ?? [],
            processing_status: response.response.processing_status as ProcessingStatus,
            created_at:        response.response.created_at ?? null,
            task_count:        (response.response.task_id ?? []).length,
          })
          return response.response
        }
        return null
      } catch (e) {
        this.error = 'Failed to create handler'
        throw e
      } finally {
        this.isLoading = false
      }
    },

    async createHandlerAdvanced(request: PostHandlerAdvancedCreateRequest): Promise<OsirDbHandlerModel | null> {
      this.isLoading = true
      this.error = null
      try {
        const api = useOsirApi()
        const response = await api.handler.advanced(request)
        if (response.response) {
          // Add the new handler to the list
          this.handlers.unshift({
            handler_id:        response.response.handler_id,
            case_name:         response.response.case_name ?? null,
            case_uuid:         response.response.case_uuid,
            modules:           response.response.modules ?? [],
            task_ids:          response.response.task_id ?? [],
            processing_status: response.response.processing_status as ProcessingStatus,
            created_at:        response.response.created_at ?? null,
            task_count:        (response.response.task_id ?? []).length,
          })
          return response.response
        }
        return null
      } catch (e) {
        this.error = 'Failed to create handler'
        throw e
      } finally {
        this.isLoading = false
      }
    },

    async fetchTasksForHandlers(handlers: HandlerRow[]) {
      this.isLoadingTasks = true
      try {
        const api = useOsirApi()
        for (const handler of handlers) {
          if (!handler.task_ids.length) {
            this.tasksByHandler[handler.handler_id] = []
            continue
          }
          const results = await Promise.allSettled(
            handler.task_ids.map(id => api.tasks.info(id).then(r => r.response))
          )
          const tasks: TaskDetail[] = []
          for (const result of results) {
            if (result.status === 'fulfilled' && result.value) {
              tasks.push(toTaskDetail(result.value, handler.handler_id, handler.case_name ?? ''))
            }
          }
          this.tasksByHandler[handler.handler_id] = tasks
        }
      } catch {
        this.error = 'Failed to fetch tasks for handlers'
      } finally {
        this.isLoadingTasks = false
      }
    },

    async fetchHandlersAndTasks(cases: { name: string; uuid: string }[]) {
      this.isLoading = true
      this.isLoadingTasks = true
      try {
        // Fetch handlers first
        await this.fetchHandlers(cases)
        
        // Then fetch tasks for all handlers
        const handlers = this.handlers
        if (handlers.length > 0) {
          await this.fetchTasksForHandlers(handlers)
        }
      } catch {
        this.error = 'Failed to fetch handlers and tasks'
      } finally {
        this.isLoading = false
        this.isLoadingTasks = false
      }
    },

    startPolling(cases: { name: string; uuid: string }[], ms = 10000) {
      this.fetchHandlersAndTasks(cases)
      this.stopPolling()
      this.pollInterval = setInterval(() => this.fetchHandlersAndTasks(cases), ms)
    },

    // Handler By Case: Poll only handlers (not tasks)
    startPollingHandlers(cases: { name: string; uuid: string }[], ms = 10000) {
      this.fetchHandlers(cases)
      this.stopPolling()
      this.pollInterval = setInterval(() => this.fetchHandlers(cases), ms)
    },

    // Task By Handler: Poll only the selected handler if processing
    startPollingHandler(handler: HandlerRow, ms = 10000) {
      if (handler.processing_status !== 'processing_started') return
      // Initial fetch: refresh handler and its tasks
      this.refreshHandler(handler.handler_id)
      if (!this.tasksByHandler[handler.handler_id]) {
        this.fetchTasksForHandler(handler)
      }
      this.stopPolling()
      this.pollInterval = setInterval(() => {
        if (this.handlers.find(h => h.handler_id === handler.handler_id)?.processing_status === 'processing_started') {
          this.refreshHandler(handler.handler_id)
        } else {
          this.stopPolling()
        }
      }, ms)
    },

    // Task Info: Poll only the selected task if processing
    startPollingTask(taskId: string, ms = 10000) {
      // Initial fetch
      this.fetchTaskInfo(taskId)
      this.stopPolling()
      // Start polling only if task is processing
      this.pollInterval = setInterval(async () => {
        const task = await this.fetchTaskInfo(taskId)
        if (task?.processing_status !== 'processing_started') {
          this.stopPolling()
        }
      }, ms)
    },

    stopPolling() {
      if (this.pollInterval) {
        clearInterval(this.pollInterval)
        this.pollInterval = null
      }
    },
  },
})
