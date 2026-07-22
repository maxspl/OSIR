import type { HandlerRow, TaskDetail } from '~/stores/handler'
import type { TaskRow } from '~/stores/task'
import { useHandlerStore } from '~/stores/handler'

export type View = 'handler-by-case' | 'task-by-handler' | 'task-info'

export function useMonitoringNavigation(
  onHandlerSelected: (h: HandlerRow) => Promise<void>,
) {
  const handlerStore = useHandlerStore()
  const route = useRoute()

  const activeView      = ref<View>('handler-by-case')
  const selectedHandler = ref<HandlerRow | null>(null)
  const selectedTask    = ref<TaskDetail | null>(null)

  // ── Navigation ────────────────────────────────────────────────────────────
  // NB: live polling is entirely handled by useMonitoringPolling (single system).
  // This composable ONLY manages navigation state (view + selection).
  onMounted(async () => {
    if (route.query.view === 'task-info') {
      const taskId = route.query.taskId as string | undefined
      if (taskId) {
        const task = await handlerStore.fetchTaskInfo(taskId)
        if (task) selectedTask.value = task
      }
      activeView.value = 'task-info'
    }

    if (route.query.handler_id) {
      const handlerId = route.query.handler_id as string
      const handler = handlerStore.handlers.find(h => h.handler_id === handlerId)
      if (handler) {
        selectedHandler.value = handler
        activeView.value = 'task-by-handler'
        await onHandlerSelected(handler)
      }
      await navigateTo({ query: { ...route.query, handler_id: undefined } }, { replace: true })
    }
  })

  async function selectHandler(_e: Event, row: unknown) {
    const h = (row as { original: HandlerRow }).original
    selectedHandler.value = h
    activeView.value = 'task-by-handler'
    await onHandlerSelected(h)
  }

  async function selectTask(_e: Event, row: unknown) {
    const taskRow = (row as { original: TaskRow | TaskDetail }).original
    // If it's already a TaskDetail (with logs), use it directly
    if ('logs' in taskRow) {
      selectedTask.value = taskRow as TaskDetail
    } else {
      // Otherwise, fetch the full details with logs
      const taskDetail = await handlerStore.fetchTaskInfo(taskRow.task_id)
      if (taskDetail) {
        selectedTask.value = taskDetail
      }
    }
    activeView.value = 'task-info'
  }

  return { activeView, selectedHandler, selectedTask, selectHandler, selectTask }
}
