<script setup lang="ts">
const reprocessFile = defineModel<boolean>('reprocessFile')

const props = defineProps<{
  isSubmitting: boolean
}>()

const emit = defineEmits<{
  'run': []
}>()
</script>

<template>
  <div class="space-y-6">
    <USeparator />

    <div class="flex items-center justify-between">
      <div>
        <p class="text-sm font-medium text-highlighted">Reprocess File</p>
        <p class="text-xs text-muted">Force reprocessing of already processed files</p>
      </div>
      <USwitch v-model="reprocessFile" />
    </div>

    <USeparator />

    <div class="flex justify-end">
      <UButton
        label="Run Orchestration"
        icon="i-lucide-play"
        size="lg"
        :disabled="isSubmitting"
        :loading="isSubmitting"
        @click="emit('run')"
      />
    </div>
  </div>
</template>
