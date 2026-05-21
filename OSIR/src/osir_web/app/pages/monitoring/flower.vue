<script setup lang="ts">
useSeoMeta({ title: 'Master & Agent Status' })

import { useFlowerStore } from '~/stores/flower'
import type { FlowerWorkerRow } from '~/stores/flower'

type View = 'running-workers' | 'flower'
type WorkerStatus = 'Online' | 'Offline' | 'Heartbeat'

const flowerStore = useFlowerStore()
const activeView = ref<View>('running-workers')

const menuItems = [
  { view: 'running-workers' as View, label: 'Running Workers', icon: 'i-lucide-server' },
  { view: 'flower'          as View, label: 'Flower',          icon: 'i-lucide-layout-dashboard' },
]

// Fetch workers on component mount
onMounted(() => {
  flowerStore.fetchWorkers()
  flowerStore.startPolling()
})

onBeforeUnmount(() => {
  flowerStore.stopPolling()
})

type StatusCfg = { color: 'primary' | 'warning' | 'error' | 'neutral'; icon: string }
const statusCfg: Record<WorkerStatus, StatusCfg> = {
  Online:    { color: 'primary', icon: 'i-lucide-circle-check' },
  Heartbeat: { color: 'warning', icon: 'i-lucide-heart-pulse' },
  Offline:   { color: 'error',   icon: 'i-lucide-circle-x' },
}

const workerColumns = [
  { accessorKey: 'name',            header: 'Worker Name' },
  { accessorKey: 'status',          header: 'Status' },
  { accessorKey: 'activeTaskCount', header: 'Active' },
  { accessorKey: 'processedCount',  header: 'Processed' },
  { accessorKey: 'failedCount',     header: 'Failed' },
  { accessorKey: 'loadAvg',         header: 'Load Avg (1m / 5m / 15m)' },
  { accessorKey: 'heartbeat',       header: 'Last Heartbeat' },
]

const flowerUrl = 'http://localhost:5555'

// Helper to get workers from store
const workers = computed(() => flowerStore.workers)
</script>

<template>
  <UPage>
    <div class="max-w-6xl mx-auto px-4 py-10 space-y-6">

      <!-- Header -->
      <div class="space-y-3">
        <UBadge label="Flower Monitoring" color="primary" variant="subtle" size="sm" icon="i-lucide-cpu" />
        <h1 class="text-2xl font-bold text-primary uppercase leading-tight font-syne">
          MASTER &amp; AGENT STATUS
        </h1>
        <p class="text-sm text-muted">Monitor your agents &amp; master using Flower.</p>
      </div>

      <USeparator />

      <!-- Menu tabs -->
      <div class="flex items-center gap-1 p-1 rounded-lg bg-(--ui-bg-elevated) border border-(--ui-border) w-fit">
        <UButton
          v-for="item in menuItems"
          :key="item.view"
          :label="item.label"
          :icon="item.icon"
          size="sm"
          :variant="activeView === item.view ? 'solid' : 'ghost'"
          :color="activeView === item.view ? 'primary' : 'neutral'"
          @click="activeView = item.view"
        />
      </div>

      <!-- ── VIEW 1 : Running Workers ────────────────────────────────────────── -->
      <template v-if="activeView === 'running-workers'">
        <div class="rounded-lg border border-(--ui-border) overflow-hidden">
          <div class="flex items-center gap-2 px-4 py-3 bg-(--ui-bg-elevated) border-b border-(--ui-border)">
            <UIcon name="i-lucide-server" class="w-4 h-4 text-primary shrink-0" />
            <span class="text-xs font-semibold uppercase tracking-wide">Running Workers</span>
            <UBadge :label="String(workers.length)" color="neutral" variant="subtle" size="xs" class="ml-1" />
          </div>

          <UTable :data="workers" :columns="workerColumns">
            <template #name-cell="{ row }">
              <span class="font-mono text-xs">{{ row.original.name }}</span>
            </template>
            <template #status-cell="{ row }">
              <UBadge
                :label="row.original.status"
                :color="statusCfg[row.original.status as WorkerStatus].color"
                :icon="statusCfg[row.original.status as WorkerStatus].icon"
                variant="subtle"
                size="sm"
              />
            </template>
            <template #activeTaskCount-cell="{ row }">
              <UBadge
                :label="String(row.original.activeTaskCount)"
                :color="row.original.activeTaskCount > 0 ? 'warning' : 'neutral'"
                variant="subtle"
                size="sm"
              />
            </template>
            <template #failedCount-cell="{ row }">
              <span
                class="text-sm font-mono"
                :class="row.original.failedCount > 0 ? 'text-red-500' : 'text-muted'"
              >{{ row.original.failedCount }}</span>
            </template>
            <template #loadAvg-cell="{ row }">
              <span class="font-mono text-xs text-muted">{{ row.original.loadAvg }}</span>
            </template>
            <template #heartbeat-cell="{ row }">
              <span class="text-xs text-muted">{{ row.original.heartbeat }}</span>
            </template>
            <template #empty>
              <div class="flex flex-col items-center gap-2 py-10 text-center">
                <UIcon name="i-lucide-server-off" class="w-8 h-8 text-muted" />
                <p class="text-sm text-muted">No workers found.</p>
              </div>
            </template>
          </UTable>
        </div>
      </template>

      <!-- ── VIEW 2 : Flower iframe ─────────────────────────────────────────── -->
      <template v-else-if="activeView === 'flower'">
        <div class="rounded-lg border border-(--ui-border) overflow-hidden">
          <div class="flex items-center gap-2 px-4 py-3 bg-(--ui-bg-elevated) border-b border-(--ui-border)">
            <UIcon name="i-lucide-layout-dashboard" class="w-4 h-4 text-primary shrink-0" />
            <span class="text-xs font-semibold uppercase tracking-wide">Flower</span>
            <UButton
              :href="flowerUrl"
              target="_blank"
              icon="i-lucide-external-link"
              size="xs"
              variant="ghost"
              color="neutral"
              class="ml-auto"
            />
          </div>
          <iframe
            :src="flowerUrl"
            class="w-full border-0"
            style="height: 700px;"
            title="Flower monitoring"
            sandbox="allow-same-origin allow-scripts allow-forms"
          />
        </div>
      </template>

    </div>
  </UPage>
</template>
