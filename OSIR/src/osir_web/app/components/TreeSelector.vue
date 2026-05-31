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
const triggerWidth = ref(200)
const searchQuery = ref('')
const expandedKeys = ref<string[]>([])

// ── Click outside handler ────────────────────────────────────────────────────
function handleClickOutside(event: MouseEvent) {
  if (containerRef.value && !containerRef.value.contains(event.target as Node)) {
    isOpen.value = false
  }
}

onMounted(() => {
  document.addEventListener('click', handleClickOutside)
})

onUnmounted(() => {
  document.removeEventListener('click', handleClickOutside)
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
watch(isOpen, (val) => {
  if (val && triggerRef.value) {
    triggerWidth.value = triggerRef.value.getBoundingClientRect().width - 20
  }
  if (!val) {
    searchQuery.value = ''
  }
})

watch(searchQuery, () => {
  expandedKeys.value = []
})

// ── Handle selection ─────────────────────────────────────────────────────────
function onSelect(e: TreeItemSelectEvent<TreeItem>) {
  if (e.detail.originalEvent.type === 'click') {
    e.preventDefault()
  }
  const label = e.detail.value?.label
  if (!label) return
  const index = expandedKeys.value.indexOf(label)
  if (index === -1) {
    expandedKeys.value = [...expandedKeys.value, label]
  } else {
    expandedKeys.value = expandedKeys.value.filter(l => l !== label)
  }
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
      v-if="isOpen"
      class="absolute z-50 mt-1 bg-(--ui-bg-elevated) border border-(--ui-border) rounded-lg shadow-lg max-h-96 overflow-y-auto"
      :style="{ width: triggerWidth ? `${triggerWidth}px` : undefined }"
    >

      <!-- Search input -->
      <div class="px-3 py-2 border-b border-(--ui-border)">
        <UInput
          v-model="searchQuery"
          placeholder="Search..."
          size="sm"
          class="w-full"
          autofocus
          :loading="loading"
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
