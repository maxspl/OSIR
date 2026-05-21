import type { ProcessingStatus } from '~/stores/handler'

export type LogLevel = 'INFO' | 'WARNING' | 'ERROR' | 'DEBUG'

export type StatusCfg = {
  color: 'primary' | 'warning' | 'error' | 'neutral'
  icon: string
  label: string
}

export const statusCfg: Record<ProcessingStatus, StatusCfg> = {
  task_created:       { color: 'neutral', icon: 'i-lucide-clock',          label: 'Created' },
  processing_started: { color: 'warning', icon: 'i-lucide-loader-circle',  label: 'Processing' },
  processing_done:    { color: 'primary', icon: 'i-lucide-check-circle-2', label: 'Done' },
  processing_failed:  { color: 'error',   icon: 'i-lucide-x-circle',       label: 'Failed' },
}

export const statusStripeClass: Record<ProcessingStatus, string> = {
  task_created:       'bg-neutral-400',
  processing_started: 'bg-amber-400',
  processing_done:    'bg-primary',
  processing_failed:  'bg-red-500',
}

export const logLevelBadge: Record<LogLevel, 'neutral' | 'warning' | 'error' | 'primary'> = {
  INFO: 'neutral', DEBUG: 'neutral', WARNING: 'warning', ERROR: 'error',
}

export const logRowClass: Record<LogLevel, string> = {
  INFO:    'border-l-2 border-transparent',
  DEBUG:   'border-l-2 border-transparent opacity-70',
  WARNING: 'border-l-2 border-amber-500 bg-amber-500/5',
  ERROR:   'border-l-2 border-red-500 bg-red-500/5',
}

export const logMsgClass: Record<LogLevel, string> = {
  INFO:    'text-(--ui-text)',
  DEBUG:   'text-(--ui-text-muted)',
  WARNING: 'text-amber-500',
  ERROR:   'text-red-500',
}

export function getStatusCfg(status: string): StatusCfg {
  return statusCfg[status as ProcessingStatus] ?? { color: 'neutral', icon: 'i-lucide-circle', label: status }
}

export function formatDuration(seconds: number | null): string {
  if (seconds == null) return '—'
  if (seconds < 60) return `${seconds.toFixed(3)}s`
  const m = Math.floor(seconds / 60)
  const s = Math.round(seconds % 60)
  if (m < 60) return s > 0 ? `${m}m ${s}s` : `${m}m`
  const h = Math.floor(m / 60)
  const rem = m % 60
  return rem > 0 ? `${h}h ${rem}m` : `${h}h`
}

export function short(uuid: string): string {
  return uuid.slice(0, 8) + '…'
}

export function timeAgo(dateStr: string): string {
  const diff = Date.now() - new Date(dateStr).getTime()
  const s = Math.floor(diff / 1000)
  if (s < 60)   return 'just now'
  const m = Math.floor(s / 60)
  if (m < 60)   return `${m} minute${m > 1 ? 's' : ''} ago`
  const h = Math.floor(m / 60)
  if (h < 24)   return `${h} hour${h > 1 ? 's' : ''} ago`
  const d = Math.floor(h / 24)
  if (d < 7)    return `${d} day${d > 1 ? 's' : ''} ago`
  const w = Math.floor(d / 7)
  if (w < 4)    return `${w} week${w > 1 ? 's' : ''} ago`
  const mo = Math.floor(d / 30)
  if (mo < 12)  return `${mo} month${mo > 1 ? 's' : ''} ago`
  const y = Math.floor(d / 365)
  return `${y} year${y > 1 ? 's' : ''} ago`
}

export function extractVal(val: unknown): string {
  if (val === null || val === undefined) return 'all'
  if (typeof val === 'object' && 'value' in (val as object)) return (val as { value: string }).value
  return String(val)
}

export const statusOptions = [
  { label: 'All statuses',  value: 'all' },
  { label: 'Done',          value: 'processing_done' },
  { label: 'Processing',    value: 'processing_started' },
  { label: 'Created',       value: 'task_created' },
  { label: 'Failed',        value: 'processing_failed' },
]

export const handlerColumns = [
  { accessorKey: 'handler_id',        header: 'Handler ID' },
  { accessorKey: 'case_name',         header: 'Case' },
  { accessorKey: 'processing_status', header: 'Status' },
  { accessorKey: 'created_at',        header: 'Created' },
  { accessorKey: 'task_count',        header: 'Tasks' },
]

export const taskColumns = [
  { accessorKey: 'task_id',           header: 'Task ID' },
  { accessorKey: 'input',             header: 'Input' },
  { accessorKey: 'processing_status', header: 'Status' },
  { accessorKey: 'start_time',        header: 'Started' },
]

export const taskColumnsNoHandler = [
  { accessorKey: 'task_id',           header: 'Task ID' },
  { accessorKey: 'case_name',         header: 'Case Name' },
  { accessorKey: 'module',            header: 'Input' },
  { accessorKey: 'processing_status', header: 'Status' },
  { accessorKey: 'start_time',        header: 'Started' }
]

export const menuItems = [
  { view: 'handler-by-case', label: 'Handler By Case', icon: 'i-lucide-layers' },
  { view: 'task-by-handler', label: 'Task By Handler', icon: 'i-lucide-list-tree' },
  { view: 'task-info',       label: 'Task Info',       icon: 'i-lucide-file-search' },
] as const