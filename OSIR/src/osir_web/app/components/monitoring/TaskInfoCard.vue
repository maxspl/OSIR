<script setup lang="ts">
import type { TaskDetail } from '~/stores/handler'
import type { ProcessingStatus } from '~/stores/handler'
import {
  statusCfg, statusStripeClass, logLevelBadge, logRowClass, logMsgClass,
  short, type LogLevel,
} from '~/utils/monitoring'

const props = defineProps<{
  task: TaskDetail
}>()

const emit = defineEmits<{
  'stop': []
  'rerun': []
  'back': []
}>()

const logSearch = ref('')

const filteredLogs = computed(() =>
  (props.task.logs ?? []).filter(l =>
    !logSearch.value || l.message.toLowerCase().includes(logSearch.value.toLowerCase()),
  )
)

const infoRows = computed(() => [
  ['i-lucide-folder',  'Case',     props.task.case_name],
  ['i-lucide-cpu',     'Agent',    props.task.agent],
  ['i-lucide-package', 'Module',   props.task.module],
  ['i-lucide-code',    'Function', props.task.fn ?? '—'],
] as [string, string, string][])
</script>

<template>
  <div class="space-y-4">
    <!-- Task summary card -->
    <div class="rounded-lg border border-(--ui-border) overflow-hidden flex">
      <div class="w-1 shrink-0" :class="statusStripeClass[task.processing_status as ProcessingStatus]" />
      <div class="flex-1">
        <div class="flex items-center gap-4 px-5 py-3">
          <UIcon
            :name="statusCfg[task.processing_status].icon"
            class="w-5 h-5 shrink-0"
            :class="{
              'text-primary':     task.processing_status === 'processing_done',
              'text-amber-400':   task.processing_status === 'processing_started',
              'text-neutral-400': task.processing_status === 'task_created',
              'text-red-500':     task.processing_status === 'processing_failed',
            }"
          />
          <div class="flex-1 min-w-0">
            <p class="text-xs text-muted uppercase tracking-wide font-medium">Task</p>
            <p class="font-mono text-xs font-medium break-all">{{ task.task_id }}</p>
          </div>
          <div class="flex items-center gap-4 text-xs text-muted shrink-0">
            <span v-if="task.start_time" class="flex items-center gap-1">
              <UIcon name="i-lucide-clock" class="w-3 h-3" />{{ task.start_time }}
            </span>
            <span v-if="task.end_time" class="flex items-center gap-1">
              <UIcon name="i-lucide-flag" class="w-3 h-3" />{{ task.end_time }}
            </span>
          </div>
          <div class="flex items-center gap-2">
            <UButton
              v-if="task.processing_status === 'processing_started'"
              label="Stop Task"
              icon="i-lucide-square"
              color="error"
              variant="subtle"
              size="sm"
              @click="emit('stop')"
            />
            <UButton
              v-if="task.processing_status === 'processing_done' || task.processing_status === 'processing_failed'"
              label="Rerun Task"
              icon="i-lucide-refresh-cw"
              color="primary"
              variant="subtle"
              size="sm"
              title="This feature may not work with modified modules"
              @click="emit('rerun')"
            />
          </div>
        </div>
      </div>
    </div>

    <!-- Info + Metrics -->
    <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">

      <!-- Information -->
      <div class="rounded-lg border border-(--ui-border) divide-y divide-(--ui-border) overflow-hidden">
        <div class="flex items-center gap-2 px-4 py-3 bg-(--ui-bg-elevated)">
          <UIcon name="i-lucide-info" class="w-4 h-4 text-primary shrink-0" />
          <span class="text-xs font-semibold uppercase tracking-wide">Information</span>
        </div>
        <div v-for="[icon, label, value] in infoRows" :key="label" class="flex items-center gap-3 px-4 py-2.5">
          <UIcon :name="icon" class="w-3.5 h-3.5 text-muted shrink-0" />
          <span class="text-xs text-muted w-20 shrink-0">{{ label }}</span>
          <span class="font-mono text-xs break-all ml-auto text-right">{{ value }}</span>
        </div>
      </div>

      <!-- Metrics -->
      <div class="rounded-lg border border-(--ui-border) divide-y divide-(--ui-border) overflow-hidden">
        <div class="flex items-center gap-2 px-4 py-3 bg-(--ui-bg-elevated)">
          <UIcon name="i-lucide-gauge" class="w-4 h-4 text-primary shrink-0" />
          <span class="text-xs font-semibold uppercase tracking-wide">Metrics</span>
        </div>
        <div class="flex items-start gap-3 px-4 py-2.5">
          <UIcon name="i-lucide-log-in" class="w-3.5 h-3.5 text-muted shrink-0 mt-0.5" />
          <span class="text-xs text-muted w-20 shrink-0">Input Path</span>
          <span class="font-mono text-xs break-all ml-auto text-right">{{ task.input || '—' }}</span>
        </div>
        <div class="flex items-start gap-3 px-4 py-2.5">
          <UIcon name="i-lucide-log-out" class="w-3.5 h-3.5 text-muted shrink-0 mt-0.5" />
          <span class="text-xs text-muted w-20 shrink-0">Output Path</span>
          <span class="font-mono text-xs break-all ml-auto text-right">{{ task.output || '—' }}</span>
        </div>
      </div>
    </div>

    <!-- Execution Traces -->
    <div class="rounded-lg border border-(--ui-border) overflow-hidden">
      <div class="flex items-center justify-between px-4 py-3 border-b border-(--ui-border) bg-(--ui-bg-elevated)">
        <div class="flex items-center gap-2">
          <UIcon name="i-lucide-terminal" class="w-4 h-4 text-green-400" />
          <span class="text-xs font-semibold text-highlighted uppercase tracking-wide">Execution Traces</span>
          <UBadge :label="`${filteredLogs.length} / ${(task.logs ?? []).length}`" color="neutral" variant="subtle" size="xs" />
        </div>
        <UInput v-model="logSearch" placeholder="Filter logs…" icon="i-lucide-search" size="xs" class="w-44" />
      </div>
      <div class="divide-y divide-(--ui-border) max-h-72 overflow-y-auto font-mono text-xs">
        <div
          v-for="(log, i) in filteredLogs"
          :key="i"
          class="flex items-start gap-3 px-4 py-2"
          :class="logRowClass[log.level as LogLevel]"
        >
          <span class="text-green-500/60 shrink-0 tabular-nums select-none">{{ log.timestamp }}</span>
          <UBadge
            :label="log.level"
            :color="logLevelBadge[log.level as LogLevel]"
            variant="subtle"
            size="xs"
            class="shrink-0 w-16 justify-center"
          />
          <span class="break-all" :class="logMsgClass[log.level as LogLevel]">{{ log.message }}</span>
        </div>
        <div v-if="filteredLogs.length === 0" class="px-4 py-8 text-center text-(--ui-text-muted) italic">
          No matching log lines.
        </div>
      </div>
    </div>
  </div>
</template>