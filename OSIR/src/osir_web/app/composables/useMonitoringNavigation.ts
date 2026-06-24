import type { HandlerRow, TaskDetail } from '~/stores/handler'
import type { TaskRow } from '~/stores/task'
import { useHandlerStore } from '~/stores/handler'

export type View = 'handler-by-case' | 'task-by-handler' | 'task-info'

const PROCESSING_STATES = ['processing', 'processing_started']
const POLL_INTERVAL_MS = 5_000

export function useMonitoringNavigation(
  onHandlerSelected: (h: HandlerRow) => Promise<void>,
) {
  const handlerStore = useHandlerStore()
  const route = useRoute()

  const activeView      = ref<View>('handler-by-case')
  const selectedHandler = ref<HandlerRow | null>(null)
  const selectedTask    = ref<TaskDetail | null>(null)

  // ── Polling ──────────────────────────────────────────────────────────────
  let pollTimer: ReturnType<typeof setInterval> | null = null

  function isProcessing(): boolean {
    const handlerProcessing = selectedHandler.value
      ? PROCESSING_STATES.includes(selectedHandler.value.processing_status)
      : false

    const taskProcessing = selectedTask.value
      ? PROCESSING_STATES.includes(selectedTask.value.processing_status)
      : false

    return handlerProcessing || taskProcessing
  }

  async function pollRefresh() {
    if (!isProcessing()) {
      stopPolling()
      return
    }

    // Refresh handler tasks si un handler est sélectionné
    if (selectedHandler.value) {
      await handlerStore.fetchTasksForHandler(selectedHandler.value)

      // Sync selectedHandler avec les données fraîches du store
      const fresh = handlerStore.handlers.find(
        h => h.handler_id === selectedHandler.value!.handler_id,
      )
      if (fresh) selectedHandler.value = fresh
    }

    // Refresh task info si une task est sélectionnée
    if (selectedTask.value) {
      const freshTask = await handlerStore.fetchTaskInfo(selectedTask.value.task_id)
      if (freshTask) selectedTask.value = freshTask
    }

    // Arrêt automatique si plus rien n'est en cours après le refresh
    if (!isProcessing()) stopPolling()
  }

  function startPolling() {
    if (pollTimer !== null) return
    pollTimer = setInterval(pollRefresh, POLL_INTERVAL_MS)
  }

  function stopPolling() {
    if (pollTimer !== null) {
      clearInterval(pollTimer)
      pollTimer = null
    }
  }

  // Surveille les changements de statut pour démarrer/arrêter le polling
  watch(
    () => [selectedHandler.value?.processing_status, selectedTask.value?.processing_status],
    () => {
      if (isProcessing()) startPolling()
      else stopPolling()
    },
  )

  // Nettoyage à la destruction du composant
  onUnmounted(() => stopPolling())

  // ── Navigation ────────────────────────────────────────────────────────────
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
    // Si c'est déjà un TaskDetail (avec logs), on l'utilise directement
    if ('logs' in taskRow) {
      selectedTask.value = taskRow as TaskDetail
    } else {
      // Sinon, on fetch les détails complets avec les logs
      const taskDetail = await handlerStore.fetchTaskInfo(taskRow.task_id)
      if (taskDetail) {
        selectedTask.value = taskDetail
      }
    }
    activeView.value = 'task-info'
  }

  return { activeView, selectedHandler, selectedTask, selectHandler, selectTask }
}