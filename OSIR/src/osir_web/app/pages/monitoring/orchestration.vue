<script setup lang="ts">
import { useHandlerStore } from '~/stores/handler'
import { useCaseStore } from '~/stores/case'
import { getStatusCfg, statusOptions } from '~/utils/monitoring'
import { useOsirApi } from '~/api'
import  FilterBar  from '~/components/monitoring/FilterBar.vue'
import HandlerTable from '~/components/monitoring/HandlerTable.vue'
import HandlerSummaryCard from '~/components/monitoring/HandlerSummaryCard.vue'
import HandlerTasksByModule from '~/components/monitoring/HandlerTasksByModule.vue'
import DangerZone from '~/components/monitoring/DangerZone.vue'
import HandlerModuleStatus from '~/components/monitoring/HandlerModuleStatus.vue'
import TaskInfoCard from '~/components/monitoring/TaskInfoCard.vue'
import ViewTabs from '~/components/monitoring/ViewTabs.vue'

useSeoMeta({ title: 'Orchestration Monitoring' })

// ── API ─────────────────────────────────────────────────────────────────────
const api = useOsirApi()
const toast = useToast()

// ── Stores ────────────────────────────────────────────────────────────────────
const handlerStore = useHandlerStore()
const caseStore = useCaseStore()

await caseStore.fetchCases()
await handlerStore.fetchHandlers(caseStore.cases.map(c => ({ name: c.name, uuid: c.case_uuid })))

// ── Filters ───────────────────────────────────────────────────────────────────
const filterValues = reactive({
  filterCaseName:      'all',
  filterHandlerStatus: 'all',
  filterHandlerId:     '',
  filterTaskStatus:    'all',
  filterModule:        'all',
  filterTaskCaseName:  'all',
})

const filtersRef = computed(() => ({
  ...filterValues,
  selectedHandler: selectedHandler.value,
}))

const {
  filterCaseName,
  filterHandlerStatus,
  caseNameOptions,
  handlerOptions,
  moduleOptions,
  filteredHandlers,
  currentTasks,
  onCaseChange,
  selectHandlerById,
  applyHandlerFilters,
  extractVal,
} = useMonitoringFilters(
  computed({
    get: () => selectedHandler.value,
    set: (v) => { selectedHandler.value = v },
  }),
)

// Keep filterValues in sync with composable refs
watch(() => filterValues.filterTaskCaseName, (v) => {
  if (v !== filterValues.filterTaskCaseName) filterValues.filterTaskCaseName = v
})

function onFilterUpdate(key: string, value: string) {
  if (key === 'filterTaskCaseName') {
    onCaseChange(value)
    filterValues.filterTaskCaseName = value
  } else if (key === 'filterHandlerId') {
    selectHandlerById(value)
    filterValues.filterHandlerId = value
  } else if (key === 'filterCaseName') {
    filterCaseName.value = value
    filterValues.filterCaseName = value
  } else if (key === 'filterHandlerStatus') {
    filterHandlerStatus.value = value
    filterValues.filterHandlerStatus = value
  } else {
    (filterValues as any)[key] = value
  }
}

// ── Navigation ────────────────────────────────────────────────────────────────
const { activeView, selectedHandler, selectedTask, selectHandler, selectTask } =
  useMonitoringNavigation(async (handler) => {
    applyHandlerFilters(handler)
    filterValues.filterHandlerId = handler.handler_id
    filterValues.filterTaskCaseName = handler.case_name ?? 'all'
    filterValues.filterTaskStatus = 'all'
    filterValues.filterModule = 'all'
    if (!handlerStore.tasksByHandler[handler.handler_id]) {
      await handlerStore.fetchTasksForHandler(handler)
    }
  })

// ── Polling ───────────────────────────────────────────────────────────────────
useMonitoringPolling(activeView, selectedHandler, selectedTask)

// ── Actions ──────────────────────────────────────────────────────────────────
async function deleteHandler() {
  if (!selectedHandler.value) return
  try {
    await api.handler.delete(selectedHandler.value.handler_id)
    await handlerStore.fetchHandlers(caseStore.cases.map(c => ({ name: c.name, uuid: c.case_uuid })))
    selectedHandler.value = null
    filterValues.filterHandlerId = ''
    toast.add({ title: 'Success', description: 'Handler deleted successfully', color: 'success' })
  } catch (error) {
    toast.add({ title: 'Error', description: 'Failed to delete handler', color: 'error' })
    console.error('Failed to delete handler:', error)
  }
}

async function deleteAllHandlers() {
  const caseName = filterValues.filterCaseName
  if (caseName === 'all') return
  const handlersToDelete = handlerStore.handlers.filter(h => h.case_name === caseName)
  if (handlersToDelete.length === 0) return
  try {
    await Promise.all(handlersToDelete.map(h => api.handler.delete(h.handler_id)))
    await handlerStore.fetchHandlers(caseStore.cases.map(c => ({ name: c.name, uuid: c.case_uuid })))
    selectedHandler.value = null
    filterValues.filterHandlerId = ''
    toast.add({ title: 'Success', description: `${handlersToDelete.length} handler(s) deleted successfully`, color: 'success' })
  } catch (error) {
    toast.add({ title: 'Error', description: 'Failed to delete handlers', color: 'error' })
    console.error('Failed to delete handlers:', error)
  }
}

// ── Handler summary ───────────────────────────────────────────────────────────
const { handlerTasksByModule, handlerModuleSummary, handlerSummary } = useHandlerSummary(selectedHandler)

// ── FilterBar definitions ─────────────────────────────────────────────────────
const view1Filters = computed(() => [[
  { icon: 'i-lucide-folder-open', label: 'Case',   modelKey: 'filterCaseName',      options: caseNameOptions.value, placeholder: 'All cases…' },
  { icon: 'i-lucide-activity',    label: 'Status', modelKey: 'filterHandlerStatus', options: statusOptions,          placeholder: 'All statuses…' },
]])

const view2Filters = computed(() => [
  [
    { icon: 'i-lucide-folder-open', label: 'Case',    modelKey: 'filterTaskCaseName', options: caseNameOptions.value, placeholder: 'All cases…' },
    {
      icon: 'i-lucide-layers', label: 'Handler', modelKey: 'filterHandlerId',
      options: handlerOptions.value,
      placeholder: 'All handlers…',
      disabled: filterValues.filterTaskCaseName === 'all' && !filterValues.filterHandlerId,
      badge: selectedHandler.value ? {
        label: getStatusCfg(selectedHandler.value.processing_status).label,
        color: getStatusCfg(selectedHandler.value.processing_status).color,
        variant: 'subtle',
      } : undefined,
    },
  ],
  [
    { icon: 'i-lucide-activity', label: 'Status', modelKey: 'filterTaskStatus', options: statusOptions,       placeholder: 'All statuses…' },
    { icon: 'i-lucide-package',  label: 'Module', modelKey: 'filterModule',     options: moduleOptions.value, placeholder: 'All modules…' },
  ],
])
</script>

<template>
  <UPage>
    <div class="max-w-6xl mx-auto px-4 py-10 space-y-6">

      <OsirHeader
        badge="Monitoring"
        title="ORCHESTRATION - MONITORING"
        description="Find and monitor your on-going handlers & tasks."
      />

      <USeparator />

      <ViewTabs v-model:active-view="activeView" />

      <!-- ── VIEW 1 : Handler By Case ──────────────────────────────────────── -->
      <template v-if="activeView === 'handler-by-case'">
        <FilterBar
          :filters="view1Filters"
          :model-values="filterValues"
          @update="onFilterUpdate"
        />
        <HandlerTable
          :handlers="filteredHandlers"
          :show-danger-zone="filterValues.filterCaseName !== 'all'"
          @select="selectHandler"
          @delete-all="deleteAllHandlers"
        />
      </template>

      <!-- ── VIEW 2 : Task By Handler ──────────────────────────────────────── -->
      <template v-else-if="activeView === 'task-by-handler'">
        <FilterBar
          :filters="view2Filters"
          :model-values="filterValues"
          @update="onFilterUpdate"
        />

        <!-- No handler selected: message -->
        <template v-if="!selectedHandler">
          <div class="flex flex-col items-center gap-3 py-16 text-center">
            <UIcon name="i-lucide-layers" class="w-10 h-10 text-muted" />
            <p class="text-sm text-muted">
              Select a handler from
              <UButton label="Handler By Case" variant="link" size="sm" class="p-0" @click="activeView = 'handler-by-case'" />
              to see its tasks.
            </p>
          </div>
        </template>

        <!-- Handler selected: summary + modules -->
        <template v-else>
          <HandlerSummaryCard
            :handler="selectedHandler"
            :start-time="handlerSummary?.startTime ?? null"
            :end-time="handlerSummary?.endTime ?? null"
            @stop="() => {}"
            @rerun="() => {}"
          />

          <HandlerModuleStatus
            :not-launched="handlerModuleSummary.notLaunched"
            :executed="handlerModuleSummary.executed"
            :failed="handlerModuleSummary.failed"
          />

          <HandlerTasksByModule
            :tasks-by-module="handlerTasksByModule"
            :filter-task-status="filterValues.filterTaskStatus"
            :filter-module="filterValues.filterModule"
            @select-task="selectTask"
          />

          <DangerZone
            title="Delete selected handler"
            description="Permanently removes this handler and all its associated tasks."
            button-label="Delete Handler"
            @action="deleteHandler"
          />
        </template>
      </template>

      <!-- ── VIEW 3 : Task Info ────────────────────────────────────────────── -->
      <template v-else-if="activeView === 'task-info'">
        <div v-if="!selectedTask" class="flex flex-col items-center gap-3 py-16 text-center">
          <UIcon name="i-lucide-file-search" class="w-10 h-10 text-muted" />
          <p class="text-sm text-muted">
            Select a task from
            <UButton label="Task By Handler" variant="link" size="sm" class="p-0" @click="activeView = 'task-by-handler'" />
            to see its details.
          </p>
        </div>
        <TaskInfoCard
          v-else
          :task="selectedTask"
          @stop="() => {}"
          @rerun="() => {}"
          @back="activeView = 'task-by-handler'"
        />
      </template>

    </div>
  </UPage>
</template>

<style scoped>
:deep(.clickable-rows tbody tr) { cursor: pointer; }
:deep(.clickable-rows tbody tr:hover) { background-color: var(--ui-bg-elevated); }
</style>