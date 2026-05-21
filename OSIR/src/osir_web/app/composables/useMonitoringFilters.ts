import type { HandlerRow } from '~/stores/handler'
import { useHandlerStore } from '~/stores/handler'
import { extractVal } from '~/utils/monitoring'

export function useMonitoringFilters(selectedHandler: Ref<HandlerRow | null>) {
  const handlerStore = useHandlerStore()

  const filterCaseName      = ref('all')
  const filterHandlerStatus = ref('all')
  const filterHandlerId     = ref('')
  const filterTaskStatus    = ref('all')
  const filterModule        = ref('all')
  const filterTaskCaseName  = ref('all')

  const caseNameOptions = computed(() => handlerStore.caseOptions)

  const handlerOptions = computed(() => {
    if (filterTaskCaseName.value === 'all') return []
    return [
      { label: 'All handlers', value: 'all' },
      ...handlerStore.handlers
        .filter(h => h.case_name === filterTaskCaseName.value)
        .map(h => ({ label: `${h.handler_id.slice(0, 8)}… — ${h.processing_status}`, value: h.handler_id })),
    ]
  })

  const moduleOptions = computed(() => {
    const source = filterHandlerId.value
      ? (handlerStore.tasksByHandler[filterHandlerId.value] ?? [])
      : Object.values(handlerStore.tasksByHandler).flat()
    return [
      { label: 'All modules', value: 'all' },
      ...[...new Set(source.map(t => t.module))].map(m => ({ label: m, value: m })),
    ]
  })

  const filteredHandlers = computed(() => {
    const result = handlerStore.handlers.filter(h =>
      (filterCaseName.value === 'all' || h.case_name === filterCaseName.value)
      && (filterHandlerStatus.value === 'all' || h.processing_status === filterHandlerStatus.value),
    )
    return [...result].sort((a, b) => {
      const dateA = a.created_at || ''
      const dateB = b.created_at || ''
      if (!dateA || !dateB) return 0
      return new Date(dateB).getTime() - new Date(dateA).getTime()
    })
  })

  const allTasks = computed(() => {
    const tasks = Object.values(handlerStore.tasksByHandler).flat()
    return [...tasks].sort((a, b) => {
      const dateA = a.start_time || ''
      const dateB = b.start_time || ''
      if (!dateA || !dateB) return 0
      return new Date(dateB).getTime() - new Date(dateA).getTime()
    })
  })

  const currentTasks = computed(() => {
    const source = filterHandlerId.value
      ? (handlerStore.tasksByHandler[filterHandlerId.value] ?? [])
      : allTasks.value
    return source.filter(t =>
      (filterTaskStatus.value === 'all' || t.processing_status === filterTaskStatus.value)
      && (filterModule.value === 'all' || t.module === filterModule.value)
      && (filterTaskCaseName.value === 'all' || t.case_name === filterTaskCaseName.value),
    )
  })

  function onCaseChange(val: string) {
    filterTaskCaseName.value = val
    selectedHandler.value = null
    filterHandlerId.value = ''
  }

  async function selectHandlerById(id: string) {
    const handlerStore = useHandlerStore()
    if (id === 'all') {
      selectedHandler.value = null
      filterHandlerId.value = ''
    } else {
      const h = handlerStore.handlers.find(h => h.handler_id === id) ?? null
      selectedHandler.value = h
      filterHandlerId.value = id
      filterTaskCaseName.value = h?.case_name ?? 'all'
      if (h && !handlerStore.tasksByHandler[id]) {
        await handlerStore.fetchTasksForHandler(h)
      }
    }
  }

  function applyHandlerFilters(handler: HandlerRow) {
    filterHandlerId.value = handler.handler_id
    filterTaskCaseName.value = handler.case_name ?? 'all'
    filterTaskStatus.value = 'all'
    filterModule.value = 'all'
  }

  return {
    filterCaseName,
    filterHandlerStatus,
    filterHandlerId,
    filterTaskStatus,
    filterModule,
    filterTaskCaseName,
    caseNameOptions,
    handlerOptions,
    moduleOptions,
    filteredHandlers,
    currentTasks,
    onCaseChange,
    selectHandlerById,
    applyHandlerFilters,
    extractVal,
  }
}