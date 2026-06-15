import type { HandlerRow, TaskDetail } from '~/stores/handler'
import { useHandlerStore } from '~/stores/handler'

export function useHandlerSummary(selectedHandler: Ref<HandlerRow | null>) {
  const handlerStore = useHandlerStore()

  const handlerTasksByModule = computed(() => {
    if (!selectedHandler.value) return {} as Record<string, TaskDetail[]>
    const tasks = handlerStore.tasksByHandler[selectedHandler.value.handler_id] ?? []
    const grouped: Record<string, TaskDetail[]> = {}
    tasks.forEach(t => {
      if (!grouped[t.module]) grouped[t.module] = []
      grouped[t.module].push(t)
    })
    return grouped
  })

  const handlerModuleSummary = computed(() => {
    if (!selectedHandler.value?.modules) return { notLaunched: [], executed: [], failed: [] }
    const tasks = handlerStore.tasksByHandler[selectedHandler.value.handler_id] ?? []
    const executedModules = new Set(tasks.map(t => t.module))
    const notLaunched = selectedHandler.value.modules.filter(m => !executedModules.has(m))

    const executedModulesWithTasks: Record<string, TaskDetail[]> = {}
    tasks.forEach(t => {
      if (!executedModulesWithTasks[t.module]) executedModulesWithTasks[t.module] = []
      executedModulesWithTasks[t.module].push(t)
    })

    const executed = Object.keys(executedModulesWithTasks)
    const failed = executed.filter(m =>
      executedModulesWithTasks[m].some(t => t.processing_status === 'processing_failed')
    )

    return { notLaunched, executed, failed }
  })

  const handlerSummary = computed(() => {
    if (!selectedHandler.value) return null
    const tasks = handlerStore.tasksByHandler[selectedHandler.value.handler_id] ?? []
    const startDate = selectedHandler.value.created_at
    const endDates = tasks.map(t => t.end_time).filter((d): d is string => d !== null)
    const endDate = endDates.length > 0
      ? endDates.reduce((latest, d) => new Date(d) > new Date(latest) ? d : latest, endDates[0])
      : null

    return {
      handlerId: selectedHandler.value.handler_id,
      caseName: selectedHandler.value.case_name,
      status: selectedHandler.value.processing_status,
      modules: selectedHandler.value.modules,
      taskCount: selectedHandler.value.task_count,
      createdAt: startDate,
      endedAt: endDate,
      startTime: startDate,
      endTime: endDate,
    }
  })

  const taskStatusCount = computed(() => {
    if (!selectedHandler.value) return {}
    const tasks = handlerStore.tasksByHandler[selectedHandler.value.handler_id] ?? []
    const counts: Record<string, number> = {}
    tasks.forEach(t => {
      counts[t.processing_status] = (counts[t.processing_status] || 0) + 1
    })
    return counts
  })

  return { handlerTasksByModule, handlerModuleSummary, handlerSummary, taskStatusCount }
}