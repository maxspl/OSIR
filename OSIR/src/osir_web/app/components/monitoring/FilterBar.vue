<script setup lang="ts">
import { extractVal } from '~/utils/monitoring'

interface Option { label: string; value: string }

type FilterType = 'select' | 'input'

interface FilterDef {
  icon: string
  label: string
  modelKey: string
  type?: FilterType
  options?: Option[]
  placeholder?: string
  disabled?: boolean
  badge?: { label: string; color: string; variant: string }
}

const props = defineProps<{
  filters: FilterDef[][]   // array of rows, each row is an array of filter defs
}>()

const emit = defineEmits<{
  'update': [key: string, value: string]
}>()

const modelValues = defineModel<Record<string, string>>('modelValues')

function update(key: string, val: unknown) {
  const extracted = extractVal(val)
  if (modelValues.value) modelValues.value[key] = extracted
  emit('update', key, extracted)
}
</script>

<template>
  <div class="rounded-lg bg-(--ui-bg-elevated) border border-(--ui-border) divide-y divide-(--ui-border)">
    <div
      v-for="(row, rowIdx) in filters"
      :key="rowIdx"
      class="grid divide-x divide-(--ui-border)"
      :style="`grid-template-columns: repeat(${row.length}, minmax(0, 1fr))`"
    >
      <div
        v-for="f in row"
        :key="f.modelKey"
        class="flex items-center gap-3 px-4 py-3 transition-opacity duration-200"
        :class="f.disabled ? 'opacity-40 pointer-events-none' : ''"
      >
        <UIcon :name="f.icon" class="text-primary w-4 h-4 shrink-0" />
        <span class="text-xs font-medium text-muted shrink-0">{{ f.label }}</span>
        
        <!-- Select input -->
        <USelectMenu
          v-if="f.type !== 'input'"
          :model-value="modelValues?.[f.modelKey]"
          :items="f.options"
          value-key="value"
          label-key="label"
          :placeholder="f.placeholder ?? `All…`"
          class="w-full"
          @update:model-value="update(f.modelKey, $event)"
        />
        
        <!-- Text input -->
        <UInput
          v-else
          :model-value="modelValues?.[f.modelKey]"
          :placeholder="f.placeholder ?? 'Search…'"
          size="sm"
          class="w-full"
          :ui="{ icon: { trailing: { pointer: '' } } }"
          @update:model-value="update(f.modelKey, $event)"
        />
        
        <Transition
          enter-active-class="transition duration-150 ease-out"
          enter-from-class="opacity-0 scale-90"
          enter-to-class="opacity-100 scale-100"
          leave-active-class="transition duration-100 ease-in"
          leave-from-class="opacity-100 scale-100"
          leave-to-class="opacity-0 scale-90"
        >
          <UButton
            v-if="modelValues?.[f.modelKey] && modelValues[f.modelKey] !== 'all' && modelValues[f.modelKey] !== ''"
            icon="i-lucide-x"
            size="sm"
            variant="ghost"
            color="neutral"
            @click="update(f.modelKey, 'all')"
          />
        </Transition>
        <UBadge
          v-if="f.badge"
          :label="f.badge.label"
          :color="(f.badge.color as any)"
          :variant="(f.badge.variant as any)"
          size="sm"
          class="ml-auto shrink-0"
        />
      </div>
    </div>
  </div>
</template>