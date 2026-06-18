<script setup lang="ts">
import { useTaskStore } from '~/stores/task'
import type { TaskStatus } from '~/stores/task'
import { useCaseStore } from '~/stores/case'
import { statusOptions } from '~/utils/monitoring'
import FilterBar from '~/components/monitoring/FilterBar.vue'

useSeoMeta({ title: 'Status — Task On-Going' })

const taskStore = useTaskStore()
const caseStore = useCaseStore()

const page = ref<number>(1)
const pageSize = ref<number>(10)

// Filter values
const filterValues = reactive({
  filterCase:   'all',
  filterModule: 'all',
  filterInput:  '',
  filterStatus: 'all',
})

// Sync page and pageSize from store on initial load
const syncPage = () => {
  page.value = taskStore.pagination.page
  pageSize.value = taskStore.pagination.pageSize
}

// Initialize from store
syncPage()

// Build filter params for API call
const buildFilterParams = () => {
  const params: { status: string | null, input: string | null, caseNames: string[] | null } = {
    status: null,
    input: null,
    caseNames: null
  }
  
  if (filterValues.filterStatus !== 'all') {
    params.status = filterValues.filterStatus
  }
  
  if (filterValues.filterInput) {
    params.input = filterValues.filterInput
  }
  
  if (filterValues.filterCase !== 'all') {
    params.caseNames = [filterValues.filterCase]
  }
  
  return params
}

// Fetch tasks with current filters
const fetchTasks = () => {
  const { status, input, caseNames } = buildFilterParams()
  taskStore.fetchTasks(
    caseNames,
    status,
    input,
    page.value,
    pageSize.value
  )
}

// Restart polling with current filters
const restartPolling = () => {
  const { status, input, caseNames } = buildFilterParams()
  taskStore.startPolling(caseNames, status, input, page.value, pageSize.value, 10000)
}

// Watch local page/pageSize changes to update store and refetch
watch([page, pageSize], () => {
  taskStore.setPage(page.value)
  taskStore.setPageSize(pageSize.value)
  fetchTasks()
  restartPolling()
})

// Debounced refetch for input filter
let inputDebounce: ReturnType<typeof setTimeout>

function onFilterUpdate(key: string, value: string) {
  if (key === 'filterInput') {
    page.value = 1
    clearTimeout(inputDebounce)
    inputDebounce = setTimeout(() => {
      fetchTasks()
      restartPolling()
    }, 500)
  } else {
    page.value = 1
    fetchTasks()
    restartPolling()
  }
  // Update the filter value
  (filterValues as any)[key] = value
}

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

// Filtered tasks (module filter is applied client-side)
const filteredTasks = computed(() =>
  taskStore.tasks.filter(t => {
    const matchStatus = filterValues.filterStatus === 'all' || t.status === filterValues.filterStatus
    const matchCase = filterValues.filterCase === 'all' || t.case_name === filterValues.filterCase
    const matchInput = !filterValues.filterInput || t.input.toLowerCase().includes(filterValues.filterInput.toLowerCase())
    const matchModule = filterValues.filterModule === 'all' || t.module === filterValues.filterModule
    return matchStatus && matchCase && matchInput && matchModule
  })
)

onMounted(() => {
  fetchTasks()
  restartPolling()
})

onUnmounted(() => {
  taskStore.stopPolling()
})

function timeAgo(dateStr: string): string {
  const diff = Date.now() - new Date(dateStr).getTime()
  const s = Math.floor(diff / 1000)
  if (s < 60)                    return 'just now'
  const m = Math.floor(s / 60)
  if (m < 60)                    return `${m} minute${m > 1 ? 's' : ''} ago`
  const h = Math.floor(m / 60)
  if (h < 24)                    return `${h} hour${h > 1 ? 's' : ''} ago`
  const d = Math.floor(h / 24)
  if (d < 7)                     return `${d} day${d > 1 ? 's' : ''} ago`
  const w = Math.floor(d / 7)
  if (w < 4)                     return `${w} week${w > 1 ? 's' : ''} ago`
  const mo = Math.floor(d / 30)
  if (mo < 12)                   return `${mo} month${mo > 1 ? 's' : ''} ago`
  const y = Math.floor(d / 365)
  return `${y} year${y > 1 ? 's' : ''} ago`
}

const columns = [
  { accessorKey: 'task_id',   header: 'ID' },
  { accessorKey: 'case_name', header: 'Case' },
  { accessorKey: 'module',    header: 'Module' },
  { accessorKey: 'status',    header: 'Status' },
  { accessorKey: 'timestamp', header: 'Started' },
  { accessorKey: 'input',     header: 'Input Path' },
]

// ── Status / log config ──────────────────────────────────────────────────────
type StatusCfg = { color: 'primary' | 'warning' | 'error' | 'neutral'; icon: string; label: string }

const statusConfig: Record<TaskStatus, StatusCfg> = {
  task_created:       { color: 'neutral',  icon: 'i-lucide-clock',            label: 'Created' },
  processing_started: { color: 'warning',  icon: 'i-lucide-loader-circle',   label: 'Processing' },
  processing_done:    { color: 'primary',  icon: 'i-lucide-check-circle-2', label: 'Done' },
  processing_failed:  { color: 'error',    icon: 'i-lucide-x-circle',         label: 'Failed' },
}

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

      <!-- Table -->
      <UTable
        :data="filteredTasks"
        :columns="columns"
        :loading="taskStore.isLoading && !taskStore.tasks.length"
        class="clickable-rows"
        @select="openTaskInfo"
      >
        <!-- ID cell -->
        <template #task_id-cell="{ row }">
          <span class="font-mono text-xs text-muted" :title="row.original.task_id">
            {{ row.original.task_id.slice(0, 8) }}…
          </span>
        </template>

        <!-- Status cell -->
        <template #status-cell="{ row }">
          <div class="flex items-center gap-2">
            <span
              v-if="row.original.status === 'processing_started'"
              class="w-1.5 h-1.5 rounded-full bg-green-400 animate-pulse"
            />
            <UBadge
              :label="statusConfig[row.original.status as TaskStatus].label"
              :color="statusConfig[row.original.status as TaskStatus].color"
              :icon="statusConfig[row.original.status as TaskStatus].icon"
              variant="subtle"
              size="sm"
            />
          </div>
        </template>

        <!-- Started cell -->
        <template #timestamp-cell="{ row }">
          <span class="text-xs text-muted">{{ timeAgo(row.original.start_time ?? row.original.timestamp) }}</span>
        </template>

        <!-- Input Path cell -->
        <template #input-cell="{ row }">
          <span class="max-w-xs block" :title="row.original.input">
            {{ row.original.input.replace(/\/?OSIR\/share\/cases\//, '') }}
          </span>
        </template>

        <!-- Empty state -->
        <template #empty>
          <div class="flex flex-col items-center gap-2 py-10 text-center">
            <UIcon name="i-lucide-list-checks" class="w-8 h-8 text-muted" />
            <p class="text-sm text-muted">No tasks found.</p>
          </div>
        </template>
      </UTable>

      <!-- Pagination -->
      <div v-if="taskStore.pagination.total > 0" class="flex items-center justify-between gap-4 py-4 flex-wrap">
        <div class="flex items-center gap-2 text-sm text-muted">
          <span>Showing {{ (page - 1) * pageSize + 1 }}-{{ Math.min(page * pageSize, taskStore.pagination.total) }} of {{ taskStore.pagination.total }}</span>
        </div>
        <div class="flex items-center gap-4">
          <UPagination
            v-model:page="page"
            :total="taskStore.pagination.total"
            :items-per-page="pageSize"
            show-first
            show-last
          />
          <USelectMenu
            v-model="pageSize"
            :items="[10, 20, 50, 100]"
            placeholder="Items per page"
            size="sm"
            class="w-32"
          />
        </div>
      </div>

    </div>
  </UPage>
</template>

<style scoped>
:deep(.clickable-rows tbody tr) { cursor: pointer;}
:deep(.clickable-rows tbody tr:hover) { background-color: var(--ui-bg-elevated); }
</style>
