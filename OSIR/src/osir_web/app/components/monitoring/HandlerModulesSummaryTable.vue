<script setup lang="ts">
import type { OsirDbStatusModel, HandlerModuleStats } from '~/api/types'
import { statusCfg } from '~/utils/monitoring'

interface ModuleStats {
  module: string
  total: number
  task_created: number
  processing_started: number
  processing_done: number
  processing_failed: number
}

const props = defineProps<{
  // Can receive either tasksByModule (legacy) or moduleStats from API
  tasksByModule?: Record<string, any[]>
  moduleStats?: HandlerModuleStats[]
  filterTaskStatus: string
  filterModule: string
}>()

const emit = defineEmits<{
  'select-module': [module: string]
}>()

const statusOrder: OsirDbStatusModel[] = [
  'task_created',
  'processing_started', 
  'processing_done',
  'processing_failed'
]

// Compute stats for each module
const modulesStats = computed<ModuleStats[]>(() => {
  const stats: ModuleStats[] = []
  
  // Use moduleStats from API if available (lazy loading mode)
  if (props.moduleStats && props.moduleStats.length > 0) {
    for (const ms of props.moduleStats) {
      // Skip if module doesn't match filter
      if (props.filterModule !== 'all' && ms.module !== props.filterModule) continue
      
      // Check if we should filter by status
      if (props.filterTaskStatus !== 'all') {
        const statusCount = ms.status_counts[props.filterTaskStatus] ?? 0
        if (statusCount === 0) continue
      }
      
      stats.push({
        module: ms.module,
        total: ms.task_count,
        task_created: ms.status_counts.task_created ?? 0,
        processing_started: ms.status_counts.processing_started ?? 0,
        processing_done: ms.status_counts.processing_done ?? 0,
        processing_failed: ms.status_counts.processing_failed ?? 0,
      })
    }
    return stats
  }
  
  // Fallback to tasksByModule (legacy mode)
  if (!props.tasksByModule) return []
  
  for (const [module, tasks] of Object.entries(props.tasksByModule)) {
    // Skip if module doesn't match filter
    if (props.filterModule !== 'all' && module !== props.filterModule) continue
    
    const filteredTasks = props.filterTaskStatus === 'all' 
      ? tasks 
      : tasks.filter(t => t.processing_status === props.filterTaskStatus)
    
    if (filteredTasks.length === 0 && props.filterTaskStatus !== 'all') continue
    
    const counts: Record<OsirDbStatusModel, number> = {
      task_created: 0,
      processing_started: 0,
      processing_done: 0,
      processing_failed: 0,
    }
    
    for (const t of tasks) {
      counts[t.processing_status] = (counts[t.processing_status] || 0) + 1
    }
    
    stats.push({
      module,
      total: tasks.length,
      task_created: counts.task_created,
      processing_started: counts.processing_started,
      processing_done: counts.processing_done,
      processing_failed: counts.processing_failed,
    })
  }
  
  return stats
})

const columns = [
  { accessorKey: 'module', header: 'Module' },
  { accessorKey: 'total', header: 'Total' },
  { accessorKey: 'task_created', header: 'Created' },
  { accessorKey: 'processing_started', header: 'Processing' },
  { accessorKey: 'processing_done', header: 'Done' },
  { accessorKey: 'processing_failed', header: 'Failed' },
]

function onRowSelect(_e: Event, row: { original: ModuleStats }) {
  emit('select-module', row.original.module)
}
</script>

<template>
  <div class="space-y-4">
    <UTable
      :data="modulesStats"
      :columns="columns"
      class="clickable-rows"
      @select="onRowSelect"
    >
      <!-- Module name -->
      <template #module-cell="{ row }">
        <div class="flex items-center gap-2">
          <UIcon name="i-lucide-package" class="w-4 h-4 text-primary shrink-0" />
          <span class="font-medium">{{ row.original.module }}</span>
        </div>
      </template>

      <!-- Total count -->
      <template #total-cell="{ row }">
        <UBadge :label="String(row.original.total)" color="neutral" variant="subtle" size="sm" />
      </template>

      <!-- Status counts -->
      <template v-for="status in statusOrder" :#[`${status}-cell`]="{ row }">
        <div class="flex items-center justify-center gap-1">
          <span
            v-if="status === 'processing_started' && row.original[status] > 0"
            class="w-1.5 h-1.5 rounded-full bg-green-400 animate-pulse"
          />
          <UBadge
            :label="String(row.original[status])"
            :color="statusCfg[status].color"
            variant="subtle"
            size="sm"
          />
        </div>
      </template>

      <!-- Empty state -->
      <template #empty>
        <div class="flex flex-col items-center gap-2 py-10 text-center">
          <UIcon name="i-lucide-package" class="w-8 h-8 text-muted" />
          <p class="text-sm text-muted">No modules found for this handler.</p>
        </div>
      </template>
    </UTable>
  </div>
</template>

<style scoped>
:deep(.clickable-rows tbody tr) { cursor: pointer; }
:deep(.clickable-rows tbody tr:hover) { background-color: var(--ui-bg-elevated); }
</style>
