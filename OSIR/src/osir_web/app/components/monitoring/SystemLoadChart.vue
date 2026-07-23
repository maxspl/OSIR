<script setup lang="ts">
import { computed, ref, onMounted, onBeforeUnmount } from 'vue'
import type { OsirDbMetricsModel } from '~/api'

const props = defineProps<{
  samples: OsirDbMetricsModel[]
  metric: 'mem_pct' | 'cpu_pct' | 'swap_pct' | 'loadavg' | 'worker_rss_mb'
  title: string
  unit?: string
  max?: number          // fixed y-max (e.g. 100 for percentages)
}>()

// One colour per agent, stable by index.
const palette = ['#4ea1ff', '#46c99a', '#f5b13d', '#ef6b6b', '#a78bfa', '#58b6d8']

// ── Responsive width (viewBox in px, height fixed) ───────────────────────────
const H = 220
const padL = 44
const padR = 14
const padT = 12
const padB = 24
const wrapper = ref<HTMLElement | null>(null)
const width = ref(600)
let ro: ResizeObserver | null = null

onMounted(() => {
  if (wrapper.value) {
    width.value = wrapper.value.clientWidth || 600
    ro = new ResizeObserver(([e]) => { width.value = e.contentRect.width })
    ro.observe(wrapper.value)
  }
})
onBeforeUnmount(() => ro?.disconnect())

// ── Series: one per agent, {t, v} sorted, null values dropped ────────────────
type Point = { t: number, v: number }
type Series = { agent: string, color: string, points: Point[], last: number | null }

const series = computed<Series[]>(() => {
  const byAgent = new Map<string, Point[]>()
  for (const s of props.samples) {
    const v = s[props.metric] as number | null
    if (v === null || v === undefined) continue
    const arr = byAgent.get(s.agent) ?? []
    arr.push({ t: new Date(s.ts).getTime(), v })
    byAgent.set(s.agent, arr)
  }
  return [...byAgent.keys()].sort().map((agent, i) => {
    const points = (byAgent.get(agent) as Point[]).sort((a, b) => a.t - b.t)
    return {
      agent,
      color: palette[i % palette.length],
      points,
      last: points.length ? points[points.length - 1].v : null,
    }
  })
})

const hasData = computed(() => series.value.some(s => s.points.length > 0))

// ── Scales ───────────────────────────────────────────────────────────────────
const tRange = computed<[number, number]>(() => {
  const ts = props.samples.map(s => new Date(s.ts).getTime())
  return ts.length ? [Math.min(...ts), Math.max(...ts)] : [0, 1]
})

const yMax = computed(() => {
  if (props.max) return props.max
  const vals = series.value.flatMap(s => s.points.map(p => p.v))
  const m = vals.length ? Math.max(...vals) : 1
  // Nice ceil to 1 / 2 / 5 * 10^n so the axis reads cleanly.
  const pow = Math.pow(10, Math.floor(Math.log10(m || 1)))
  const n = m / pow
  const nice = n <= 1 ? 1 : n <= 2 ? 2 : n <= 5 ? 5 : 10
  return nice * pow
})

const plotW = computed(() => Math.max(1, width.value - padL - padR))
const plotH = H - padT - padB

function xOf(t: number): number {
  const [t0, t1] = tRange.value
  if (t1 === t0) return padL + plotW.value
  return padL + ((t - t0) / (t1 - t0)) * plotW.value
}
function yOf(v: number): number {
  return padT + plotH - (v / yMax.value) * plotH
}

// ── Paths ─────────────────────────────────────────────────────────────────────
function linePath(points: Point[]): string {
  return points.map((p, i) => `${i ? 'L' : 'M'}${xOf(p.t).toFixed(1)} ${yOf(p.v).toFixed(1)}`).join(' ')
}
function areaPath(points: Point[]): string {
  if (!points.length) return ''
  const base = padT + plotH
  const first = xOf(points[0].t).toFixed(1)
  const lastX = xOf(points[points.length - 1].t).toFixed(1)
  return `${linePath(points)} L${lastX} ${base} L${first} ${base} Z`
}

// ── Ticks ─────────────────────────────────────────────────────────────────────
const yTicks = computed(() =>
  [0, 0.25, 0.5, 0.75, 1].map(f => {
    const v = yMax.value * f
    return { y: yOf(v), label: v >= 100 ? Math.round(v).toString() : v.toFixed(v < 10 ? 1 : 0) }
  }),
)

const xTicks = computed(() => {
  const [t0, t1] = tRange.value
  if (t1 === t0) return []
  return [0, 0.33, 0.66, 1].map(f => {
    const t = t0 + (t1 - t0) * f
    return { x: xOf(t), label: new Date(t).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) }
  })
})

const fmt = (v: number | null) =>
  v === null ? '—' : (v >= 100 ? Math.round(v).toString() : v.toFixed(1))
</script>

<template>
  <div ref="wrapper" class="rounded-lg border border-default bg-elevated/40 p-4">
    <div class="flex items-center justify-between mb-2 flex-wrap gap-2">
      <h3 class="text-sm font-semibold">
        {{ title }}<span v-if="unit" class="text-muted font-normal"> ({{ unit }})</span>
      </h3>
      <div class="flex items-center gap-3 flex-wrap">
        <span v-for="s in series" :key="s.agent" class="inline-flex items-center gap-1.5 text-xs text-muted">
          <span class="inline-block w-2.5 h-2.5 rounded-sm" :style="{ background: s.color }" />
          {{ s.agent }}
          <span class="font-medium text-highlighted tabular-nums">{{ fmt(s.last) }}<span v-if="unit === '%'">%</span></span>
        </span>
      </div>
    </div>

    <svg v-if="hasData" :viewBox="`0 0 ${width} ${H}`" :height="H" width="100%" role="img">
      <!-- horizontal grid + y labels -->
      <g>
        <line
          v-for="(t, i) in yTicks" :key="`g${i}`"
          :x1="padL" :x2="width - padR" :y1="t.y" :y2="t.y"
          stroke="currentColor" stroke-opacity="0.15" class="text-muted"
        />
        <text
          v-for="(t, i) in yTicks" :key="`yl${i}`"
          :x="padL - 6" :y="t.y + 3" text-anchor="end"
          class="fill-current text-muted" font-size="10"
        >{{ t.label }}</text>
      </g>
      <!-- x labels -->
      <text
        v-for="(t, i) in xTicks" :key="`xl${i}`"
        :x="t.x" :y="H - 6" text-anchor="middle"
        class="fill-current text-muted" font-size="10"
      >{{ t.label }}</text>
      <!-- series -->
      <g v-for="s in series" :key="s.agent">
        <path :d="areaPath(s.points)" :fill="s.color" fill-opacity="0.08" stroke="none" />
        <path :d="linePath(s.points)" :stroke="s.color" fill="none" stroke-width="1.5"
              stroke-linejoin="round" stroke-linecap="round" />
      </g>
    </svg>

    <p v-else class="text-sm text-muted text-center py-10">No samples in this window.</p>
  </div>
</template>
