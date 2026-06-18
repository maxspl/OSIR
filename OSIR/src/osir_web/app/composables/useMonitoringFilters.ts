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
    // Use modules from selected handler, or from all handlers' stats
    const handler = selectedHandler.value
    if (handler) {
      const stats = handlerStore.statsByHandler[handler.handler_id]
      if (stats && Array.isArray(stats.modules)) {
        const executedModules = stats.modules.map(m => m.module)
        const notLaunched = stats.not_launched_modules ?? []
        const modules = [...new Set([...executedModules, ...notLaunched])]
        return [
          { label: 'All modules', value: 'all' },
          ...modules.map(m => ({ label: m, value: m })),
        ]
      }
      // Fallback to handler.modules
      return [
        { label: 'All modules', value: 'all' },
        ...handler.modules.map(m => ({ label: m, value: m })),
      ]
    }
    // If no handler selected, get modules from all handlers
    return [
      { label: 'All modules', value: 'all' },
      ...[...new Set(handlerStore.handlers.flatMap(h => h.modules))].map(m => ({ label: m, value: m })),
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
      // Fetch stats for the selected handler
      if (h) {
        await handlerStore.fetchStatsForHandler(h.handler_id)
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
    onCaseChange,
    selectHandlerById,
    applyHandlerFilters,
    extractVal,
  }
}