<script setup lang="ts">
import { useTaskStore } from '~/stores/task'
import type { TaskStatus } from '~/stores/task'
import { useCaseStore } from '~/stores/case'

useSeoMeta({ title: 'Status — Task On-Going' })

type Filter = 'all' | 'ongoing' | 'past'

const filter = ref<Filter>('all')
const filterCase   = ref('all')
const filterModule = ref('all')

function extractVal(val: unknown): string {
  if (val === null || val === undefined) return 'all'
  if (typeof val === 'object' && 'value' in (val as object)) return (val as { value: string }).value
  return String(val)
}

const taskStore = useTaskStore()
const caseStore = useCaseStore()

await caseStore.fetchCases()

onMounted(() => {
  taskStore.startPolling(caseStore.cases.map(c => c.name), 10000)
})
onUnmounted(() => {
  taskStore.stopPolling()
})

const caseOptions   = computed(() => taskStore.caseOptions)
const moduleOptions = computed(() => taskStore.moduleOptions)

const filteredTasks = computed(() =>
  taskStore.tasks.filter(t => {
    const matchStatus = filter.value === 'all'
      || (filter.value === 'ongoing' && (t.status === 'processing_started' || t.status === 'task_created'))
      || (filter.value === 'past'    && (t.status === 'processing_done' || t.status === 'processing_failed'))
    return matchStatus
      && (filterCase.value   === 'all' || t.case_name === filterCase.value)
      && (filterModule.value === 'all' || t.module    === filterModule.value)
  })
)


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

const filters: { label: string, value: Filter }[] = [
  { label: 'All',      value: 'all' },
  { label: 'On-Going', value: 'ongoing' },
  { label: 'Past',     value: 'past' },
]

const counts = computed(() => ({
  all:     taskStore.tasks.length,
  ongoing: taskStore.tasks.filter(t => t.status === 'processing_started' || t.status === 'task_created').length,
  past:    taskStore.tasks.filter(t => t.status === 'processing_done' || t.status === 'processing_failed').length,
}))

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
          <p class="text-sm text-muted">Find and monitor your on-going tasks. - <UBadge>Last 200 By Case</UBadge></p> 
        </div>
        
        <!-- Filter -->
        <div class="flex items-center gap-1 p-1 rounded-lg bg-(--ui-bg-elevated) border border-(--ui-border) shrink-0 mt-1">
          <UButton
            v-for="f in filters"
            :key="f.value"
            :label="`${f.label} (${counts[f.value]})`"
            size="sm"
            :variant="filter === f.value ? 'solid' : 'ghost'"
            :color="filter === f.value ? 'primary' : 'neutral'"
            @click="filter = f.value"
          />
        </div>
      </div>

      <USeparator />

      <!-- Filters -->
      <div class="rounded-lg bg-(--ui-bg-elevated) border border-(--ui-border)">
        <div class="grid grid-cols-2 divide-x divide-(--ui-border)">
          <!-- Case -->
          <div class="flex items-center gap-3 px-4 py-3">
            <UIcon name="i-lucide-folder-open" class="text-primary w-4 h-4 shrink-0" />
            <span class="text-xs font-medium text-muted shrink-0">Case</span>
            <USelectMenu
              :model-value="filterCase"
              :items="caseOptions"
              value-key="value"
              label-key="label"
              placeholder="All cases…"
              class="w-full"
              @update:model-value="filterCase = extractVal($event)"
            />
            <Transition
              enter-active-class="transition duration-150 ease-out"
              enter-from-class="opacity-0 scale-90"
              enter-to-class="opacity-100 scale-100"
              leave-active-class="transition duration-100 ease-in"
              leave-from-class="opacity-100 scale-100"
              leave-to-class="opacity-0 scale-90"
            >
              <UButton
                v-if="filterCase !== 'all'"
                icon="i-lucide-x"
                size="sm"
                variant="ghost"
                color="neutral"
                @click="filterCase = 'all'"
              />
            </Transition>
          </div>

          <!-- Module -->
          <div class="flex items-center gap-3 px-4 py-3">
            <UIcon name="i-lucide-package" class="text-primary w-4 h-4 shrink-0" />
            <span class="text-xs font-medium text-muted shrink-0">Module</span>
            <USelectMenu
              :model-value="filterModule"
              :items="moduleOptions"
              value-key="value"
              label-key="label"
              placeholder="All modules…"
              class="w-full"
              @update:model-value="filterModule = extractVal($event)"
            />
            <Transition
              enter-active-class="transition duration-150 ease-out"
              enter-from-class="opacity-0 scale-90"
              enter-to-class="opacity-100 scale-100"
              leave-active-class="transition duration-100 ease-in"
              leave-from-class="opacity-100 scale-100"
              leave-to-class="opacity-0 scale-90"
            >
              <UButton
                v-if="filterModule !== 'all'"
                icon="i-lucide-x"
                size="sm"
                variant="ghost"
                color="neutral"
                @click="filterModule = 'all'"
              />
            </Transition>
          </div>
        </div>
      </div>

      <!-- Table -->
      <UTable virtualize :data="filteredTasks" :columns="columns" :loading="taskStore.isLoading && !taskStore.tasks.length" class="clickable-rows max-h-100" @select="openTaskInfo">
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

    </div>
  </UPage>
</template>

<style scoped>
:deep(.clickable-rows tbody tr) { cursor: pointer; }
:deep(.clickable-rows tbody tr:hover) { background-color: var(--ui-bg-elevated); }
</style>
