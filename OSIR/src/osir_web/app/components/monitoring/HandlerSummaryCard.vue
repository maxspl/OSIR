<script setup lang="ts">
import type { HandlerRow } from '~/stores/handler'
import type { ProcessingStatus } from '~/stores/handler'
import { getStatusCfg, statusStripeClass, short } from '~/utils/monitoring'

const props = defineProps<{
  handler: HandlerRow
  startTime: string | null
  endTime: string | null
  taskStatusCount: Record<string, number>
}>()

// Ensure taskStatusCount is never undefined
const safeTaskStatusCount = computed(() => props.taskStatusCount || {})

const emit = defineEmits<{
  'stop': []
  'rerun': []
}>()
const statusLabels: Record<string, string> = {
  'task_created': 'Created',
  'processing_started': 'Processing',
  'processing_done': 'Success',
  'processing_failed': 'Failed',
}

const statusIcons: Record<string, string> = {
  'task_created': 'i-lucide-clock',
  'processing_started': 'i-lucide-loader-circle',
  'processing_done': 'i-lucide-check-circle-2',
  'processing_failed': 'i-lucide-x-circle',
}

const statusColors: Record<string, string> = {
  'task_created': 'text-neutral-400',
  'processing_started': 'text-amber-400',
  'processing_done': 'text-green-500',
  'processing_failed': 'text-red-500',
}
</script>

<template>
  <div class="rounded-lg border border-(--ui-border) overflow-hidden flex">
    <div class="w-1 shrink-0" :class="statusStripeClass[handler.processing_status as ProcessingStatus] ?? 'bg-neutral-400'" />
    <div class="flex-1">
      <div class="flex items-center gap-4 px-5 py-3">
        <UIcon
          :name="getStatusCfg(handler.processing_status).icon"
          class="w-5 h-5 shrink-0"
          :class="{
            'text-primary':     handler.processing_status === 'processing_done',
            'text-amber-400':   handler.processing_status === 'processing_started',
            'text-neutral-400': handler.processing_status === 'task_created',
            'text-red-500':     handler.processing_status === 'processing_failed',
          }"
        />
        <div class="flex-1 min-w-0">
          <p class="text-xs text-muted uppercase tracking-wide font-medium">Handler</p>
          <p class="font-mono text-xs font-medium break-all">{{ handler.handler_id }}</p>
          <!-- Task status summary -->
          <div v-if="Object.keys(safeTaskStatusCount).length > 0" class="flex items-center gap-2 mt-1">
            <span
              v-for="(count, status) in safeTaskStatusCount"
              :key="status"
              class="flex items-center gap-1 text-xs"
              :class="statusColors[status]"
            >
              <UIcon :name="statusIcons[status]" class="w-3 h-3" />
              <span>{{ statusLabels[status] }}: {{ count }}</span>
            </span>
          </div>
        </div>
        <div class="flex items-center gap-4 text-xs text-muted shrink-0">
          <span class="flex items-center gap-1">
            <UIcon name="i-lucide-folder-open" class="w-3 h-3" />{{ handler.case_name }}
          </span>
          <span v-if="startTime" class="flex items-center gap-1">
            <UIcon name="i-lucide-clock" class="w-3 h-3" />Started: {{ startTime }}
          </span>
          <span v-if="endTime" class="flex items-center gap-1">
            <UIcon name="i-lucide-flag" class="w-3 h-3" />Ended: {{ endTime }}
          </span>
          <span v-else class="flex items-center gap-1">
            <UIcon name="i-lucide-clock" class="w-3 h-3" />Ongoing
          </span>
        </div>
        <div class="flex items-center gap-2">
          <UButton
            v-if="handler.processing_status === 'processing_started'"
            label="Stop Handler"
            icon="i-lucide-square"
            color="error"
            variant="subtle"
            size="sm"
            @click="emit('stop')"
          />
          <!-- <UButton
            v-if="handler.processing_status === 'processing_done' || handler.processing_status === 'processing_failed'"
            label="Rerun Handler"
            icon="i-lucide-refresh-cw"
            color="primary"
            variant="subtle"
            size="sm"
            @click="emit('rerun')"
          /> -->
        </div>
      </div>
    </div>
  </div>
</template>