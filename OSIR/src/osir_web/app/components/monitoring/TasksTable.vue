<script setup lang="ts">
import type { TaskRow } from '~/stores/task'
import type { TaskDetail } from '~/stores/handler'
import type { OsirDbStatusModel } from '~/api/types'
import { statusCfg, short, timeAgo } from '~/utils/monitoring'

// Normalize task types
interface NormalizedTask {
  task_id: string
  case_name: string
  module: string
  processing_status: OsirDbStatusModel
  start_time?: string | null
  input: string
  timestamp?: string
}

function normalizeTask(t: TaskRow | TaskDetail): NormalizedTask {
  return {
    task_id: t.task_id,
    case_name: (t as TaskRow).case_name || '',
    module: t.module,
    processing_status: (t as TaskDetail).processing_status || (t as TaskRow).status,
    start_time: t.start_time || (t as TaskDetail).start_time,
    input: t.input || (t as TaskDetail).input || '',
    timestamp: (t as TaskRow).timestamp,
  }
}

const props = defineProps<{
  tasks?: TaskRow[] | TaskDetail[]
  showInputFilter?: boolean
  showPagination?: boolean
  total?: number
  // Lazy loading mode
  useLazyLoading?: boolean
  caseNames?: string[] | null
  status?: string | null
  input?: string | null
  handlerId?: string | null
  // Client-side filters (not supported by API)
  moduleFilter?: string | null
}>()

const emit = defineEmits<{
  (e: 'select-task', value: Event, row: unknown): void
}>()

// For static mode pagination
const page = defineModel<number>('page', { default: 1 })
const pageSize = defineModel<number>('pageSize', { default: 10 })
const inputFilter = defineModel<string>('inputFilter', { default: '' })

// For lazy loading mode
const lazyPage = ref<number>(1)
const lazyPageSize = ref<number>(10)
const lazyInputFilter = ref<string>('')
const taskStore = props.useLazyLoading ? useTaskStore() : null

const columns = [
  { accessorKey: 'task_id',   header: 'ID' },
  { accessorKey: 'case_name', header: 'Case' },
  { accessorKey: 'module',    header: 'Module' },
  { accessorKey: 'processing_status', header: 'Status' },
  { accessorKey: 'start_time', header: 'Started' },
  { accessorKey: 'input',     header: 'Input Path' },
]

// Normalize and filter tasks
const normalizedTasks = computed(() => {
  if (!props.tasks) return []
  return props.tasks.map(normalizeTask)
})

const filteredTasks = computed(() => {
  let tasks: NormalizedTask[] = []
  
  if (props.useLazyLoading && taskStore) {
    // In lazy mode, use tasks from store (already filtered by case, status, input)
    tasks = taskStore.tasks.map(normalizeTask)
  } else {
    // In static mode, use props.tasks
    tasks = normalizedTasks.value
    
    // Apply input filter for static mode
    if (props.showInputFilter && inputFilter.value) {
      tasks = tasks.filter(t => 
        t.input.toLowerCase().includes(inputFilter.value.toLowerCase())
      )
    }
  }
  
  // Apply module filter (client-side only, not supported by API)
  if (props.moduleFilter && props.moduleFilter !== 'all') {
    tasks = tasks.filter(t => t.module === props.moduleFilter)
  }
  
  return tasks
})

// Lazy loading logic
const buildLazyParams = () => ({
  caseNames: props.caseNames ?? null,
  status: props.status ?? null,
  input: props.input ?? null,
  handlerId: props.handlerId ?? null,
  module: props.moduleFilter && props.moduleFilter !== 'all' ? props.moduleFilter : null,
})

const fetchLazyTasks = () => {
  if (!props.useLazyLoading || !taskStore) return
  const { caseNames, status, input, handlerId, module } = buildLazyParams()
  taskStore.fetchTasks(caseNames, status, input, lazyPage.value, lazyPageSize.value, handlerId, module)
}

const startLazyPolling = () => {
  if (!props.useLazyLoading || !taskStore) return
  const { caseNames, status, input, handlerId, module } = buildLazyParams()
  taskStore.startPolling(caseNames, status, input, lazyPage.value, lazyPageSize.value, 10000, handlerId, module)
}

const stopLazyPolling = () => {
  if (props.useLazyLoading && taskStore) {
    taskStore.stopPolling()
  }
}

// Initialize and watch for lazy mode
if (props.useLazyLoading && taskStore) {
  lazyPage.value = taskStore.pagination.page
  lazyPageSize.value = taskStore.pagination.pageSize

  watch([lazyPage, lazyPageSize], () => {
    taskStore.setPage(lazyPage.value)
    taskStore.setPageSize(lazyPageSize.value)
    fetchLazyTasks()
    startLazyPolling()
  })

  let lazyInputDebounce: ReturnType<typeof setTimeout>
  watch(lazyInputFilter, () => {
    lazyPage.value = 1
    clearTimeout(lazyInputDebounce)
    lazyInputDebounce = setTimeout(() => {
      fetchLazyTasks()
      startLazyPolling()
    }, 500)
  })

  watch(() => [props.caseNames, props.status, props.input, props.moduleFilter, props.handlerId], () => {
    lazyPage.value = 1
    fetchLazyTasks()
    startLazyPolling()
  }, { deep: true })

  onMounted(() => {
    fetchLazyTasks()
    startLazyPolling()
  })

  onUnmounted(() => {
    stopLazyPolling()
  })
}

const router = useRouter()

function handleSelect(e: Event, row: unknown) {
  emit('select-task', e, row)
}
</script>

<template>
  <div class="space-y-4">
    <!-- Input filter (only for static mode) -->
    <div v-if="!props.useLazyLoading && showInputFilter" class="rounded-lg bg-(--ui-bg-elevated) border border-(--ui-border) p-4">
      <div class="flex items-center gap-3">
        <UIcon name="i-lucide-search" class="text-primary w-4 h-4 shrink-0" />
        <span class="text-xs font-medium text-muted shrink-0">Input</span>
        <UInput
          v-model="inputFilter"
          placeholder="Search by input path..."
          size="sm"
          class="w-full"
          :ui="{ icon: { trailing: { pointer: '' } } }"
        >
          <template #trailing>
            <UButton
              v-if="inputFilter"
              icon="i-lucide-x"
              size="sm"
              variant="ghost"
              color="neutral"
              @click="inputFilter = ''"
            />
          </template>
        </UInput>
      </div>
    </div>

    <!-- Input filter for lazy mode (internal) -->
    <div v-if="props.useLazyLoading && showInputFilter" class="rounded-lg bg-(--ui-bg-elevated) border border-(--ui-border) p-4">
      <div class="flex items-center gap-3">
        <UIcon name="i-lucide-search" class="text-primary w-4 h-4 shrink-0" />
        <span class="text-xs font-medium text-muted shrink-0">Input</span>
        <UInput
          v-model="lazyInputFilter"
          placeholder="Search by input path..."
          size="sm"
          class="w-full"
          :ui="{ icon: { trailing: { pointer: '' } } }"
        >
          <template #trailing>
            <UButton
              v-if="lazyInputFilter"
              icon="i-lucide-x"
              size="sm"
              variant="ghost"
              color="neutral"
              @click="lazyInputFilter = ''"
            />
          </template>
        </UInput>
      </div>
    </div>

    <UTable
      :data="filteredTasks"
      :columns="columns"
      :loading="props.useLazyLoading && taskStore?.isLoading"
      class="clickable-rows"
      @select="handleSelect"
    >
      <!-- ID cell -->
      <template #task_id-cell="{ row }">
        <span class="font-mono text-xs text-muted" :title="row.original.task_id">
          {{ short(row.original.task_id) }}
        </span>
      </template>

      <!-- Case cell -->
      <template #case_name-cell="{ row }">
        <span class="text-sm">{{ row.original.case_name }}</span>
      </template>

      <!-- Status cell -->
      <template #processing_status-cell="{ row }">
        <div class="flex items-center gap-2">
          <span
            v-if="row.original.processing_status === 'processing_started'"
            class="w-1.5 h-1.5 rounded-full bg-green-400 animate-pulse"
          />
          <UBadge
            :label="statusCfg[row.original.processing_status].label"
            :color="statusCfg[row.original.processing_status].color"
            :icon="statusCfg[row.original.processing_status].icon"
            variant="subtle"
            size="sm"
          />
        </div>
      </template>

      <!-- Started cell -->
      <template #start_time-cell="{ row }">
        <span class="text-xs text-muted">{{ timeAgo(row.original.start_time || row.original.timestamp) }}</span>
      </template>

      <!-- Input Path cell -->
      <template #input-cell="{ row }">
        <span class="max-w-xs block" :title="row.original.input">
          {{ row.original.input?.replace(/\/?OSIR\/share\/cases\//, '') }}
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

    <!-- Pagination for static mode -->
    <div v-if="!props.useLazyLoading && showPagination" class="flex items-center justify-between gap-4 py-4 flex-wrap">
      <div class="flex items-center gap-2 text-sm text-muted">
        <span>Showing {{ (page - 1) * pageSize + 1 }}-{{ Math.min(page * pageSize, props.total || 0) }} of {{ props.total || 0 }}</span>
      </div>
      <div class="flex items-center gap-4">
        <UPagination
          v-model:page="page"
          :total="props.total || 0"
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

    <!-- Pagination for lazy loading mode -->
    <div v-if="props.useLazyLoading && taskStore" class="flex items-center justify-between gap-4 py-4 flex-wrap">
      <div class="flex items-center gap-2 text-sm text-muted">
        <span>Showing {{ (lazyPage - 1) * lazyPageSize + 1 }}-{{ Math.min(lazyPage * lazyPageSize, taskStore.pagination.total) }} of {{ taskStore.pagination.total }}</span>
      </div>
      <div class="flex items-center gap-4">
        <UPagination
          v-model:page="lazyPage"
          :total="taskStore.pagination.total"
          :items-per-page="lazyPageSize"
          show-first
          show-last
        />
        <USelectMenu
          v-model="lazyPageSize"
          :items="[10, 20, 50, 100]"
          placeholder="Items per page"
          size="sm"
          class="w-32"
        />
      </div>
    </div>
  </div>
</template>

<style scoped>
:deep(.clickable-rows tbody tr) { cursor: pointer; }
:deep(.clickable-rows tbody tr:hover) { background-color: var(--ui-bg-elevated); }
</style>
