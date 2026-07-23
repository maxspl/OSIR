<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import { useOsirApi } from '~/api'
import type { OsirDbMetricsModel } from '~/api'
import SystemLoadChart from '~/components/monitoring/SystemLoadChart.vue'

const api = useOsirApi()

const samples = ref<OsirDbMetricsModel[]>([])
const windowSeconds = ref(900)
const loading = ref(false)
let timer: ReturnType<typeof setInterval> | null = null

const windowOptions = [
  { label: '15 min', value: 900 },
  { label: '1 hour', value: 3600 },
  { label: '6 hours', value: 21600 }
]

async function refresh() {
  loading.value = true
  try {
    const res = await api.system.metrics(windowSeconds.value)
    samples.value = res.response ?? []
  } catch (e) {
    console.error('Failed to load system metrics', e)
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  refresh()
  timer = setInterval(refresh, 5000)
})
onUnmounted(() => { if (timer) clearInterval(timer) })
</script>

<template>
  <div class="flex flex-col gap-4 p-4">
    <div class="flex items-center justify-between gap-4">
      <div>
        <h1 class="text-lg font-semibold">System load</h1>
        <p class="text-sm text-muted">Live RAM / CPU / load per agent.</p>
      </div>
      <div class="flex items-center gap-2">
        <UButton
          icon="i-lucide-refresh-cw"
          variant="ghost"
          size="sm"
          :loading="loading"
          @click="refresh"
        />
        <USelect
          v-model="windowSeconds"
          :items="windowOptions"
          size="sm"
          @update:model-value="refresh"
        />
      </div>
    </div>

    <div class="grid grid-cols-1 xl:grid-cols-2 gap-4">
      <SystemLoadChart :samples="samples" metric="mem_pct" title="RAM used" unit="%" :max="100" />
      <SystemLoadChart :samples="samples" metric="cpu_pct" title="CPU" unit="%" :max="100" />
      <SystemLoadChart :samples="samples" metric="swap_pct" title="Swap used" unit="%" :max="100" />
      <SystemLoadChart :samples="samples" metric="worker_rss_mb" title="Workers RSS" unit="MB" />
    </div>
  </div>
</template>
