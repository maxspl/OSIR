<script setup lang="ts">
import { h, resolveComponent } from 'vue'
import type { TableColumn, TableRow } from '@nuxt/ui'

type ModuleModel = {
  module_path: string
  description: string
  processor: string
}

const props = defineProps<{
  tableRows: ModuleModel[]
  isLoadingInfos: boolean
  selectedCount: number
}>()

const emit = defineEmits<{
  'select': [event: Event, row: TableRow<ModuleModel>]
}>()

const showTable = ref(false)
const rowSelection = defineModel<Record<string, boolean>>('rowSelection')

const UCheckbox = resolveComponent('UCheckbox')

const columns: TableColumn<ModuleModel>[] = [
  {
    id: 'select',
    cell: ({ row }) => h(UCheckbox, {
      'modelValue': row.getIsSelected(),
      'onUpdate:modelValue': (value: boolean, event: Event) => {
        emit('select', event, row)
        row.toggleSelected(!!value)
      },
      'aria-label': 'Select row',
    }),
    enableSorting: false,
    enableHiding: false,
  },
  { accessorKey: 'module_path', header: 'Module' },
  { accessorKey: 'description', header: 'Description' },
  { accessorKey: 'processor', header: 'Processor' },
]
</script>

<template>
  <div class="space-y-4">
    <div class="flex items-center justify-between">
      <div>
        <p class="text-sm font-medium text-highlighted">Table View</p>
        <p class="text-xs text-muted">Browse and select modules from the table</p>
      </div>
      <USwitch v-model="showTable" />
    </div>

    <Transition
      enter-active-class="transition duration-200 ease-out"
      enter-from-class="opacity-0 -translate-y-1"
      enter-to-class="opacity-100 translate-y-0"
      leave-active-class="transition duration-150 ease-in pointer-events-none"
      leave-from-class="opacity-100 translate-y-0"
      leave-to-class="opacity-0 -translate-y-1"
    >
      <div v-if="showTable">
        <div v-if="isLoadingInfos" class="flex items-center gap-2 text-xs text-muted">
          <UIcon name="i-lucide-loader-circle" class="w-3.5 h-3.5 animate-spin" />
          Loading module details…
        </div>
        <UTable
          v-model:row-selection="rowSelection"
          :data="tableRows"
          :columns="columns"
          :loading="isLoadingInfos && tableRows.length === 0"
          @select="(e, row) => emit('select', e, row)"
        >
          <template #empty>
            <div class="flex flex-col items-center gap-2 py-8 text-center">
              <UIcon name="i-lucide-package" class="w-8 h-8 text-muted" />
              <p class="text-sm text-muted">No modules available.</p>
            </div>
          </template>
        </UTable>
        <p v-if="selectedCount" class="text-xs text-muted mt-2">
          {{ selectedCount }} module{{ selectedCount > 1 ? 's' : '' }} selected
        </p>
      </div>
    </Transition>
  </div>
</template>
