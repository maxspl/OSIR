<script setup lang="ts">
import type { HandlerRow } from '~/stores/handler'
import { handlerColumns, getStatusCfg, short, timeAgo } from '~/utils/monitoring'

defineProps<{
  handlers: HandlerRow[]
  showDangerZone: boolean
}>()

const emit = defineEmits<{
  'select': [e: Event, row: unknown]
  'delete-all': []
}>()
</script>

<template>
  <div class="space-y-4">
    <UTable
      :data="handlers"
      :columns="handlerColumns"
      class="clickable-rows"
      @select="(e, row) => emit('select', e, row)"
    >
      <template #handler_id-cell="{ row }">
        <span class="font-mono text-xs text-muted">{{ short(row.original.handler_id) }}</span>
      </template>
      <template #processing_status-cell="{ row }">
        <UBadge
          :label="getStatusCfg(row.original.processing_status).label"
          :color="getStatusCfg(row.original.processing_status).color"
          :icon="getStatusCfg(row.original.processing_status).icon"
          variant="subtle"
          size="sm"
        />
      </template>
      <template #created_at-cell="{ row }">
        <span class="text-xs text-muted">{{ timeAgo(row.original.created_at) }}</span>
      </template>
      <template #task_count-cell="{ row }">
        <UBadge :label="String(row.original.task_count)" color="neutral" variant="subtle" size="sm" />
      </template>
      <template #empty>
        <div class="flex flex-col items-center gap-2 py-10 text-center">
          <UIcon name="i-lucide-layers" class="w-8 h-8 text-muted" />
          <p class="text-sm text-muted">No handlers found.</p>
        </div>
      </template>
    </UTable>

    <DangerZone
      v-if="showDangerZone"
      title="Delete all handlers of a case"
      description="Permanently removes all handlers and their associated tasks for the selected case."
      button-label="Delete All Handlers"
      @action="emit('delete-all')"
    />
  </div>
</template>