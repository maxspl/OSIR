<script setup lang="ts">
import { ref, computed, watch, onMounted, onUnmounted } from 'vue'
import type { TreeItemSelectEvent } from 'reka-ui'
import type { TreeItem } from '@nuxt/ui'

const props = defineProps<{
  items: TreeItem[]
  modelValue: string[]
  loading?: boolean
  placeholder?: string
}>()

const emit = defineEmits<{
  'update:modelValue': [value: string[]]
}>()

// ── State ────────────────────────────────────────────────────────────────────
const isOpen = ref(false)
const triggerRef = ref<HTMLElement | null>(null)
const containerRef = ref<HTMLElement | null>(null)
const dropdownRef = ref<HTMLElement | null>(null)
const triggerWidth = ref(200)
const searchQuery = ref('')
const expandedKeys = ref<string[]>([])
const dropdownDirection = ref<'top' | 'bottom'>('bottom')

// ── Click outside handler ────────────────────────────────────────────────────
function handleClickOutside(event: MouseEvent) {
  if (containerRef.value && !containerRef.value.contains(event.target as Node)) {
    isOpen.value = false
  }
}

// ── Dropdown position ────────────────────────────────────────────────────────
function updateDropdownPosition() {
  if (!triggerRef.value) return
  
  const triggerRect = triggerRef.value.getBoundingClientRect()
  const viewportHeight = window.innerHeight
  
  // Space available below and above the trigger
  const spaceBelow = viewportHeight - triggerRect.bottom
  const spaceAbove = triggerRect.top
  
  // Estimated dropdown height (search bar + tree content)
  const estimatedDropdownHeight = 300
  
  // Open upwards if there's not enough space below
  dropdownDirection.value = spaceBelow >= estimatedDropdownHeight ? 'bottom' : 'top'
}

const searchInputRef = ref<HTMLInputElement | null>(null)

watch(isOpen, (val) => {
  if (val) {
    updateDropdownPosition()
    if (triggerRef.value) {
      triggerWidth.value = triggerRef.value.getBoundingClientRect().width - 20
    }
    nextTick(() => {
      searchInputRef.value?.focus()
    })
  }
  if (!val) {
    searchQuery.value = ''
  }
})

onMounted(() => {
  document.addEventListener('click', handleClickOutside)
  window.addEventListener('resize', updateDropdownPosition)
})

onUnmounted(() => {
  document.removeEventListener('click', handleClickOutside)
  window.removeEventListener('resize', updateDropdownPosition)
})

// ── Computed ─────────────────────────────────────────────────────────────────
function findSelectedItems(items: TreeItem[], values: string[]): TreeItem[] {
  const selected: TreeItem[] = []
  
  function traverse(nodes: TreeItem[]) {
    for (const node of nodes) {
      if (values.includes(node.value)) {
        selected.push(node)
      }
      if (node.children && node.children.length > 0) {
        traverse(node.children)
      }
    }
  }
  
  traverse(items)
  return selected
}

const selected = computed<TreeItem[]>(() => findSelectedItems(props.items, props.modelValue))

const selectedLeaves = computed(() =>
  selected.value.filter((item) => !item.children || item.children.length === 0)
)

// ── Filter tree items based on search query ───────────────────────────────
function filterTreeItems(items: TreeItem[], query: string): TreeItem[] {
  if (!query) return items
  
  const lowerQuery = query.toLowerCase()
  const leafMatches: TreeItem[] = []
  
  function collectLeaves(nodes: TreeItem[]) {
    for (const node of nodes) {
      if (node.children && node.children.length > 0) {
        collectLeaves(node.children)
      } else if (node.label.toLowerCase().includes(lowerQuery)) {
        leafMatches.push({ ...node })
      }
    }
  }
  
  collectLeaves(items)
  return leafMatches
}

const filteredItems = computed(() => filterTreeItems(props.items, searchQuery.value))

// ── Reset search when dropdown closes ────────────────────────────────────────
watch(searchQuery, () => {
  expandedKeys.value = []
})

// ── Handle selection ─────────────────────────────────────────────────────────
function onSelect(e: TreeItemSelectEvent<TreeItem>) {
  const item = e.detail.value
  if (!item) return
  
  // If item has children, handle expansion/collapse and prevent default selection
  if (item.children && item.children.length > 0) {
    if (e.detail.originalEvent.type === 'click') {
      e.preventDefault()
    }
    const label = item.label
    const index = expandedKeys.value.indexOf(label)
    if (index === -1) {
      expandedKeys.value = [...expandedKeys.value, label]
    } else {
      expandedKeys.value = expandedKeys.value.filter(l => l !== label)
    }
  }
  // If item has no children, allow default selection behavior
}

function onSelectedChange(val: TreeItem[]) {
  emit('update:modelValue', val.map(item => item.value))
}
</script>

<template>
  <div ref="containerRef" class="relative w-full flex-1 min-w-0">
    <!-- Trigger -->
    <button
      ref="triggerRef"
      type="button"
      tabindex="0"
      :aria-expanded="isOpen"
      :aria-label="placeholder || 'Select items...'"
      class="relative group rounded-md inline-flex items-center focus:outline-none disabled:cursor-not-allowed disabled:opacity-75 transition-colors px-3 py-2 text-base gap-2 text-highlighted bg-default ring ring-inset ring-accented hover:bg-elevated disabled:bg-default focus-visible:ring-2 focus-visible:ring-inset focus-visible:ring-primary pe-11 w-full cursor-pointer"
      @click="isOpen = !isOpen"
    >
      <div class="flex items-center gap-1 flex-wrap flex-1 min-w-0 truncate">
        <template v-if="selectedLeaves.length > 0">
          <UBadge
            v-for="item in selectedLeaves.slice(0, 5)"
            :key="item.value"
            :label="item.label"
            color="primary"
            variant="solid"
            size="md"
            class="rounded-full"
          />
          <UBadge
            v-if="selectedLeaves.length > 5"
            :label="`+${selectedLeaves.length - 5}`"
            color="primary"
            variant="subtle"
            size="md"
            class="rounded-full"
          />
        </template>
        <span v-else class="text-dimmed truncate">{{ placeholder || 'Select items...' }}</span>
      </div>
      <span class="absolute inset-y-0 end-0 flex items-center pe-3">
        <UIcon
          name="i-lucide-chevron-down"
          class="w-6 h-6 text-(--ui-text-dimmed) shrink-0 transition-transform duration-200"
          :class="{ 'rotate-180': isOpen }"
        />
      </span>
    </button>

    <!-- Dropdown content -->
    <div
      ref="dropdownRef"
      v-if="isOpen"
      class="absolute z-50 bg-default border border-default rounded-lg shadow-lg max-h-[300px] overflow-y-auto divide-y divide-default"
      :class="dropdownDirection === 'bottom' ? 'mt-1' : 'bottom-full mb-1'"
      :style="{ width: triggerWidth ? `${triggerWidth}px` : undefined }"
    >

      <!-- Search input -->
      <div class="relative w-full border-b border-default">
        <input
          ref="searchInputRef"
          v-model="searchQuery"
          type="text"
          placeholder="Search…"
          autocomplete="off"
          autofocus
          class="w-full rounded-md border-0 appearance-none placeholder:(--ui-text-dimmed) focus:outline-none disabled:cursor-not-allowed disabled:opacity-75 transition-colors px-3 py-2 text-base gap-2 text-(--ui-text-highlighted) bg-transparent"
          :disabled="loading"
        />
      </div>

      <!-- Tree -->
      <div class="p-2">
        <UTree
          :model-value="selected"
          :items="filteredItems"
          :expanded="expandedKeys"
          size="xl"
          multiple
          bubble-select
          propagate-select
          @update:model-value="onSelectedChange"
          @select="onSelect"
          value-key="value"
        >
          <template #item-leading="{ selected, indeterminate, handleSelect }">
            <UCheckbox
              :model-value="indeterminate ? 'indeterminate' : selected"
              tabindex="-1"
              @change="handleSelect"
              @click.stop
            />
          </template>
        </UTree>
      </div>
    </div>
  </div>
</template>
