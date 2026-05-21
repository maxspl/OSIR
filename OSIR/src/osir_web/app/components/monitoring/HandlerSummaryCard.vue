<script setup lang="ts">
import type { HandlerRow } from '~/stores/handler'
import type { ProcessingStatus } from '~/stores/handler'
import { getStatusCfg, statusStripeClass, short } from '~/utils/monitoring'

defineProps<{
  handler: HandlerRow
  startTime: string | null
  endTime: string | null
}>()

const emit = defineEmits<{
  'stop': []
  'rerun': []
}>()
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