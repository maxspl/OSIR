import { defineStore } from 'pinia'

export interface FlowerWorker {
  hostname: string
  pid: number
  freq: number
  clock: number
  active: number
  processed: number
  loadavg: number[]
  'sw_ident': string
  'sw_ver': string
  'sw_sys': string
  status: boolean
  'worker-online': number
  'worker-heartbeat': number
  heartbeats: number[]
}

export interface FlowerWorkerRow {
  name: string
  status: 'Online' | 'Offline' | 'Heartbeat'
  activeTaskCount: number
  processedCount: number
  failedCount: number
  loadAvg: string
  heartbeat: string
  pid: number
  freq: string
  swIdent: string
  swVer: string
  swSys: string
  clock: number
}

function mapStatus(worker: FlowerWorker): 'Online' | 'Offline' | 'Heartbeat' {
  if (!worker.status) return 'Offline'
  if (worker['worker-heartbeat'] > 60) return 'Heartbeat'
  return 'Online'
}

function formatHeartbeat(timestamp: number): string {
  const date = new Date(timestamp * 1000)
  return date.toISOString().replace('T', ' ').replace('\.\d+Z$', '')
}

function formatLoadAvg(loadavg: number[]): string {
  if (!loadavg || loadavg.length === 0) return '—'
  return loadavg.map(v => v.toFixed(2)).join(' / ')
}

function toWorkerRow(worker: FlowerWorker): FlowerWorkerRow {
  const lastHeartbeat = worker.heartbeats.length > 0 
    ? Math.max(...worker.heartbeats) 
    : worker.clock
  
  return {
    name: worker.hostname,
    status: mapStatus(worker),
    activeTaskCount: worker.active,
    processedCount: worker.processed,
    failedCount: 0, // Not provided by Flower API
    loadAvg: formatLoadAvg(worker.loadavg),
    heartbeat: formatHeartbeat(lastHeartbeat),
    pid: worker.pid,
    freq: worker.freq.toFixed(1),
    swIdent: worker['sw_ident'],
    swVer: worker['sw_ver'],
    swSys: worker['sw_sys'],
    clock: worker.clock,
  }
}

interface FlowerState {
  workers: FlowerWorkerRow[]
  isLoading: boolean
  error: string | null
  pollInterval: ReturnType<typeof setInterval> | null
}

export const useFlowerStore = defineStore('flower', {
  state: (): FlowerState => ({
    workers: [],
    isLoading: false,
    error: null,
    pollInterval: null,
  }),

  actions: {
    async fetchWorkers() {
      this.isLoading = true
      this.error = null
      try {
        const response = await $fetch<{ data: FlowerWorker[] }>('/flower/workers?json=1')
        this.workers = response.data.map(toWorkerRow)
      } catch (e) {
        this.error = 'Failed to fetch workers from Flower API'
        console.error('Flower API error:', e)
      } finally {
        this.isLoading = false
      }
    },

    startPolling(ms = 10000) {
      this.fetchWorkers()
      this.stopPolling()
      this.pollInterval = setInterval(() => this.fetchWorkers(), ms)
    },

    stopPolling() {
      if (this.pollInterval) {
        clearInterval(this.pollInterval)
        this.pollInterval = null
      }
    },
  },
})
