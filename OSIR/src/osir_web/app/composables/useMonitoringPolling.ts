import { ref, watch, computed, onUnmounted } from 'vue'
import type { Ref } from 'vue'
import type { View } from './useMonitoringNavigation'
import type { HandlerRow, TaskDetail } from '~/stores/handler'
import { useHandlerStore } from '~/stores/handler'
import { useCaseStore } from '~/stores/case'

export function useMonitoringPolling(
  activeView: Ref<View>,
  selectedHandler: Ref<HandlerRow | null> = ref(null),
  selectedTask: Ref<TaskDetail | null> = ref(null),
) {
  const handlerStore = useHandlerStore()
  const caseStore = useCaseStore()
  const POLLING_INTERVAL = 10000

  const hasProcessingHandlers = computed(() =>
    handlerStore.handlers.some(h => h.processing_status === 'processing_started')
  )

  const hasProcessingTask = computed(() =>
    selectedTask.value?.processing_status === 'processing_started'
  )

  // Handler By Case: Poll handlers only if any handler is processing
  function startPollingHandlerByCase() {
    if (!hasProcessingHandlers.value) return
    const cases = caseStore.cases.map(c => ({ name: c.name, uuid: c.case_uuid }))
    if (cases.length > 0) handlerStore.startPollingHandlers(cases, POLLING_INTERVAL)
  }

  // Task By Handler: Poll only the selected handler if it's processing
  function startPollingTaskByHandler() {
    if (!selectedHandler.value || selectedHandler.value.processing_status !== 'processing_started') return
    handlerStore.startPollingHandler(selectedHandler.value, POLLING_INTERVAL)
  }

  // Task Info: Poll only the selected task if it's processing
  function startPollingTaskInfo() {
    if (!selectedTask.value) return
    // Always fetch the task once on view entry
    handlerStore.fetchTaskInfo(selectedTask.value.task_id)
    // Only start polling if task is processing
    if (selectedTask.value.processing_status === 'processing_started') {
      handlerStore.startPollingTask(selectedTask.value.task_id, POLLING_INTERVAL)
    }
  }

  function stopPolling() {
    handlerStore.stopPolling()
  }

  // Watch activeView to start/stop appropriate polling
  watch(activeView, (view) => {
    stopPolling()
    switch (view) {
      case 'handler-by-case':
        startPollingHandlerByCase()
        break
      case 'task-by-handler':
        startPollingTaskByHandler()
        break
      case 'task-info':
        startPollingTaskInfo()
        break
    }
  })

  // Watch selectedHandler for task-by-handler view
  watch(selectedHandler, (handler) => {
    if (activeView.value === 'task-by-handler') {
      stopPolling()
      if (handler) startPollingTaskByHandler()
    }
  })

  // Watch selectedTask for task-info view
  watch(selectedTask, (task) => {
    if (activeView.value === 'task-info') {
      stopPolling()
      if (task) startPollingTaskInfo()
    }
  })

  onUnmounted(() => stopPolling())

  return { startPolling: startPollingHandlerByCase, stopPolling }
}