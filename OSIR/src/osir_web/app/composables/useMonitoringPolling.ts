import { ref, watch, onUnmounted } from 'vue'
import type { Ref } from 'vue'
import type { View } from './useMonitoringNavigation'
import type { HandlerRow, TaskDetail } from '~/stores/handler'
import { useHandlerStore } from '~/stores/handler'
import { useCaseStore } from '~/stores/case'

const PROCESSING_STATES = ['processing', 'processing_started']

// Set to false to silence the polling debug logs.
const DEBUG = true
function dbg(...args: unknown[]) {
  if (DEBUG) console.debug('[monitoring-poll]', ...args)
}

/**
 * SINGLE monitoring polling system (replaces the former duo
 * useMonitoringNavigation + useMonitoringPolling).
 *
 * One timer, driven by the active view and the presence of "in progress" tasks:
 *  - handler-by-case : refresh the handler LIST if at least one is in progress
 *  - task-by-handler : refresh the selected handler's status + stats
 *  - task-info       : refresh the selected task (status + logs)
 * Polling stops automatically as soon as nothing is "in progress".
 */
export function useMonitoringPolling(
  activeView: Ref<View>,
  selectedHandler: Ref<HandlerRow | null> = ref(null),
  selectedTask: Ref<TaskDetail | null> = ref(null),
) {
  const handlerStore = useHandlerStore()
  const caseStore = useCaseStore()
  const POLLING_INTERVAL = 10000

  dbg('consolidated poller active (v2 — single system)')

  let pollTimer: ReturnType<typeof setInterval> | null = null

  // Is there anything "in progress" to watch, for the current view?
  function isProcessing(): boolean {
    switch (activeView.value) {
      case 'handler-by-case':
        return handlerStore.handlers.some(h => PROCESSING_STATES.includes(h.processing_status))
      case 'task-by-handler':
        return !!selectedHandler.value
          && PROCESSING_STATES.includes(selectedHandler.value.processing_status)
      case 'task-info':
        return !!selectedTask.value
          && PROCESSING_STATES.includes(selectedTask.value.processing_status)
      default:
        return false
    }
  }

  // One polling tick: refresh only what is visible in the current view.
  async function pollOnce() {
    const view = activeView.value
    switch (view) {
      case 'handler-by-case': {
        const cases = caseStore.cases.map(c => ({ name: c.name, uuid: c.case_uuid }))
        if (cases.length) {
          dbg('tick › handler-by-case: refresh handler list')
          await handlerStore.fetchHandlers(cases)
        }
        break
      }
      case 'task-by-handler': {
        const h = selectedHandler.value
        if (h) {
          dbg('tick › task-by-handler: refresh handler status + stats', h.handler_id)
          await handlerStore.refreshHandler(h.handler_id)
          // resync the ref with the fresh status from the store (updates the badge + triggers useHandlerSummary)
          const fresh = handlerStore.handlers.find(x => x.handler_id === h.handler_id)
          if (fresh) selectedHandler.value = fresh
          // explicit refresh of the displayed stats (modules table / counters)
          await handlerStore.fetchStatsForHandler(h.handler_id)
        }
        break
      }
      case 'task-info': {
        const t = selectedTask.value
        if (t) {
          dbg('tick › task-info: refresh task', t.task_id)
          const fresh = await handlerStore.fetchTaskInfo(t.task_id)
          if (fresh) selectedTask.value = fresh
        }
        break
      }
    }

    // Auto-stop as soon as nothing is in progress anymore.
    if (!isProcessing()) {
      dbg('nothing in progress → auto-stopping polling')
      stopPolling()
    }
  }

  function startPolling() {
    stopPolling()
    if (!isProcessing()) {
      dbg('startPolling skipped — nothing in progress (view:', activeView.value, ')')
      return
    }
    dbg('starting polling — view:', activeView.value, `(${POLLING_INTERVAL}ms)`)
    pollTimer = setInterval(pollOnce, POLLING_INTERVAL)
  }

  function stopPolling() {
    if (pollTimer !== null) {
      dbg('stopping polling')
      clearInterval(pollTimer)
      pollTimer = null
    }
  }

  // (Re)start/stop polling when the view, the selection or a status changes.
  onNuxtReady(() => {
    watch(
    () => [
      activeView.value,
      selectedHandler.value?.handler_id,
      selectedHandler.value?.processing_status,
      selectedTask.value?.task_id,
      selectedTask.value?.processing_status,
      // handler-by-case: react when the set of "in progress" handlers changes
      activeView.value === 'handler-by-case'
        ? handlerStore.handlers.some(h => PROCESSING_STATES.includes(h.processing_status))
        : false,
    ],
    () => startPolling(),
    { immediate: true },
  )
  })
  

  onUnmounted(() => stopPolling())

  return { startPolling, stopPolling }
}
