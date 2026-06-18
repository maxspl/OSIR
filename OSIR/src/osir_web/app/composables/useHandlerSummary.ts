import type { HandlerRow, TaskDetail } from '~/stores/handler'
import { useHandlerStore } from '~/stores/handler'

export function useHandlerSummary(selectedHandler: Ref<HandlerRow | null>) {
  const handlerStore = useHandlerStore()

  // Raw stats from backend API (GetTaskStatsResponse format)
  const rawStats = computed(() => {
    if (!selectedHandler.value) return null
    return handlerStore.statsByHandler[selectedHandler.value.handler_id] ?? null
  })

  // Transform backend stats into our expected format
  const stats = computed(() => {
    const s = rawStats.value
    if (!s) return null
    
    const byModule = s.by_module ?? {}
    const byStatus = s.by_status ?? {}
    
    // Calculate module summaries from by_module
    const allHandlerModules = selectedHandler.value?.modules ?? []
    const executedModules = Object.keys(byModule)
    const notLaunchedModules = allHandlerModules.filter(m => !executedModules.includes(m))
    const failedModules = Object.keys(byModule).filter(m => 
      byModule[m]?.processing_failed > 0
    )
    
    // Transform by_module into moduleStats format
    const moduleStats = Object.entries(byModule).map(([module, modStats]) => ({
      module,
      task_count: modStats.total ?? 0,
      status_counts: {
        task_created: modStats.task_created ?? 0,
        processing_started: modStats.processing_started ?? 0,
        processing_done: modStats.processing_done ?? 0,
        processing_failed: modStats.processing_failed ?? 0,
      },
      has_failed: (modStats.processing_failed ?? 0) > 0,
      has_started: (modStats.processing_started ?? 0) > 0,
    }))
    
    return {
      total_tasks: s.total ?? 0,
      status_counts: byStatus,
      modules: moduleStats,
      not_launched_modules: notLaunchedModules,
      executed_modules: executedModules,
      failed_modules: failedModules,
      start_time: s.first_task_at,
      end_time: s.last_finished_at,
    }
  })

  const handlerTasksByModule = computed(() => {
    if (!selectedHandler.value) return {} as Record<string, TaskDetail[]>
    return {}
  })

  const handlerModuleSummary = computed(() => {
    if (!selectedHandler.value?.modules) return { notLaunched: [], executed: [], failed: [] }
    const s = stats.value
    if (!s) return { notLaunched: selectedHandler.value.modules, executed: [], failed: [] }
    return {
      notLaunched: s.not_launched_modules,
      executed: s.executed_modules,
      failed: s.failed_modules,
    }
  })

  const handlerSummary = computed(() => {
    if (!selectedHandler.value) return null
    const s = stats.value
    return {
      handlerId: selectedHandler.value.handler_id,
      caseName: selectedHandler.value.case_name,
      status: selectedHandler.value.processing_status,
      modules: selectedHandler.value.modules,
      taskCount: selectedHandler.value.task_count,
      createdAt: selectedHandler.value.created_at,
      endedAt: s?.end_time ?? null,
      startTime: selectedHandler.value.created_at,
      endTime: s?.end_time ?? null,
    }
  })

  const taskStatusCount = computed(() => {
    if (!selectedHandler.value) return {}
    const s = stats.value
    if (!s) return {}
    return s.status_counts
  })

  // Module stats for HandlerModulesSummaryTable
  const moduleStats = computed(() => {
    const s = stats.value
    if (!s) return []
    return s.modules
  })

  // Fetch stats when handler changes
  watch(selectedHandler, async (handler) => {
    if (handler) {
      await handlerStore.fetchStatsForHandler(handler.handler_id)
    }
  }, { immediate: true })

  return { handlerTasksByModule, handlerModuleSummary, handlerSummary, taskStatusCount, moduleStats }
}