<script setup lang="ts">
defineProps<{
  title: string
  description: string
  buttonLabel: string
}>()

const emit = defineEmits<{ 'action': [] }>()
</script>

<template>
  <div class="rounded-lg border border-red-500/30 bg-red-500/5 overflow-hidden">
    <div class="flex items-center gap-2 px-4 py-3 border-b border-red-500/30">
      <UIcon name="i-lucide-triangle-alert" class="w-4 h-4 text-red-500 shrink-0" />
      <span class="text-xs font-semibold uppercase tracking-wide text-red-500">Danger Zone</span>
    </div>
    <div class="flex items-center justify-between gap-4 px-4 py-3">
      <div>
        <p class="text-sm font-medium">{{ title }}</p>
        <p class="text-xs text-muted mt-0.5">{{ description }}</p>
      </div>
      <UButton
        :label="buttonLabel"
        icon="i-lucide-trash-2"
        color="error"
        variant="subtle"
        size="sm"
        class="shrink-0"
        @click="emit('action')"
      />
    </div>
  </div>
</template>