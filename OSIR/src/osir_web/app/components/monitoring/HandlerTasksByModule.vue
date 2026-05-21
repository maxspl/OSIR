<script setup lang="ts">
import type { TaskDetail } from '~/stores/handler'
import { taskColumns, statusCfg, short, timeAgo } from '~/utils/monitoring'

defineProps<{
  tasksByModule: Record<string, TaskDetail[]>
  filterTaskStatus: string
  filterModule: string
}>()

const emit = defineEmits<{
  'select-task': [e: Event, row: unknown]
}>()
</script>

<template>
  <div class="space-y-4">
    <div
      v-for="(moduleTasks, moduleName) in tasksByModule"
      :key="moduleName"
      v-show="filterModule === 'all' || moduleName === filterModule"
      class="rounded-lg border border-(--ui-border) overflow-hidden"
    >
      <!-- Module header -->
      <div class="flex items-center gap-3 px-4 py-3 bg-(--ui-bg-elevated) border-b border-(--ui-border)">
        <UIcon name="i-lucide-package" class="w-4 h-4 text-primary shrink-0" />
        <span class="text-sm font-medium">{{ moduleName }}</span>
        <UBadge
          :label="`${moduleTasks.filter(t => filterTaskStatus === 'all' || t.processing_status === filterTaskStatus).length} task${moduleTasks.filter(t => filterTaskStatus === 'all' || t.processing_status === filterTaskStatus).length > 1 ? 's' : ''}`"
          color="neutral"
          variant="subtle"
          size="sm"
          class="ml-auto"
        />
      </div>

      <UTable
        :data="moduleTasks.filter(t => filterTaskStatus === 'all' || t.processing_status === filterTaskStatus)"
        :columns="taskColumns"
        class="clickable-rows"
        @select="(e, row) => emit('select-task', e, row)"
      >
        <template #task_id-cell="{ row }">
          <span class="font-mono text-xs text-muted">{{ short(row.original.task_id) }}</span>
        </template>
        <template #start_time-cell="{ row }">
          <span class="text-xs text-muted">{{ timeAgo(row.original.start_time) }}</span>
        </template>
        <template #processing_status-cell="{ row }">
          <UBadge
            :label="statusCfg[row.original.processing_status].label"
            :color="statusCfg[row.original.processing_status].color"
            :icon="statusCfg[row.original.processing_status].icon"
            variant="subtle"
            size="sm"
          />
        </template>

        <template #empty>
          <div class="px-4 py-2 text-center text-xs text-muted">
            No tasks matching filters for this module.
          </div>
        </template>
      </UTable>
    </div>

    <div v-if="Object.keys(tasksByModule).length === 0" class="rounded-lg border border-(--ui-border) p-4 text-center text-muted">
      <UIcon name="i-lucide-package" class="w-6 h-6 mx-auto mb-2 text-muted" />
      <p class="text-sm">No modules found for this handler.</p>
    </div>

    <div
      v-if="filterModule !== 'all' && !Object.keys(tasksByModule).some(m => m === filterModule)"
      class="rounded-lg border border-(--ui-border) p-4 text-center text-muted"
    >
      <UIcon name="i-lucide-search" class="w-6 h-6 mx-auto mb-2 text-muted" />
      <p class="text-sm">No tasks found for module "{{ filterModule }}" in this handler.</p>
    </div>
  </div>
</template>