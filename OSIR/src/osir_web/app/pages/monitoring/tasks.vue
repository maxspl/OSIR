<script setup lang="ts">
import { useTaskStore } from '~/stores/task'
import { useCaseStore } from '~/stores/case'
import { statusOptions } from '~/utils/monitoring'
import FilterBar from '~/components/monitoring/FilterBar.vue'
import TasksTable from '~/components/monitoring/TasksTable.vue'

useSeoMeta({ title: 'Status — Task On-Going' })

const taskStore = useTaskStore()
const caseStore = useCaseStore()

// Filter values
const filterValues = reactive({
  filterCase:   'all',
  filterModule: 'all',
  filterInput:  '',
  filterStatus: 'all',
})

// Compute filter bar definition
const filterBarConfig = computed(() => [
  [
    { icon: 'i-lucide-folder-open', label: 'Case', modelKey: 'filterCase', options: taskStore.caseOptions, placeholder: 'All cases…' },
    { icon: 'i-lucide-package', label: 'Module', modelKey: 'filterModule', options: taskStore.moduleOptions, placeholder: 'All modules…' },
  ],
  [
    { icon: 'i-lucide-search', label: 'Input', modelKey: 'filterInput', type: 'input' as const, placeholder: 'Search by input path…' },
    { icon: 'i-lucide-activity', label: 'Status', modelKey: 'filterStatus', options: statusOptions, placeholder: 'All statuses…' },
  ],
])

function onFilterUpdate(key: string, value: string) {
  // Update the filter value
  (filterValues as any)[key] = value
}

// Filter tasks client-side for module (not supported by API)
const filteredTasks = computed(() => {
  return taskStore.tasks.filter(t => {
    const matchStatus = filterValues.filterStatus === 'all' || t.status === filterValues.filterStatus
    const matchCase = filterValues.filterCase === 'all' || t.case_name === filterValues.filterCase
    const matchInput = !filterValues.filterInput || t.input.toLowerCase().includes(filterValues.filterInput.toLowerCase())
    const matchModule = filterValues.filterModule === 'all' || t.module === filterValues.filterModule
    return matchStatus && matchCase && matchInput && matchModule
  })
})

const router = useRouter()

function openTaskInfo(_e: Event, row: unknown) {
  const t = (row as { original: { task_id: string } }).original
  router.push({ path: '/monitoring/orchestration', query: { view: 'task-info', taskId: t.task_id } })
}
</script>

<template>
  <UPage>
    <div class="max-w-6xl mx-auto px-4 py-10 space-y-8">

      <!-- Header -->
      <div class="flex items-start justify-between gap-4">
        <div class="space-y-3">
          <UBadge label="Monitoring" color="primary" variant="subtle" size="sm" icon="i-lucide-list-checks" />
          <h1 class="text-2xl font-bold text-primary uppercase leading-tight font-syne">
            TASK ON-GOING 
          </h1>
        </div>
        <div />
      </div>

      <USeparator />

      <!-- Filters -->
      <FilterBar
        :filters="filterBarConfig"
        :model-values="filterValues"
        @update="onFilterUpdate"
      />

      <!-- Module filter info -->
      <div v-if="filterValues.filterModule !== 'all'" class="text-center text-sm text-muted py-2">
        Showing tasks for module: {{ filterValues.filterModule }}
      </div>

      <!-- Tasks Table with server-side lazy loading -->
      <TasksTable
        :use-lazy-loading="true"
        :caseNames="filterValues.filterCase === 'all' ? null : [filterValues.filterCase]"
        :status="filterValues.filterStatus === 'all' ? null : filterValues.filterStatus"
        :input="filterValues.filterInput || null"
        :module-filter="filterValues.filterModule"
        :show-input-filter="false"
        @select-task="openTaskInfo"
      />

    </div>
  </UPage>
</template>
