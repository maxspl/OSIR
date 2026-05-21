<script setup lang="ts">
defineProps<{
  notLaunched: string[]
  executed: string[]
  failed: string[]
}>()
</script>

<template>
  <div
    v-if="notLaunched.length > 0 || executed.length > 0"
    class="flex gap-4"
  >
    <!-- Not launched -->
    <div
      v-if="notLaunched.length > 0"
      class="flex-1 rounded-lg border border-amber-500/30 bg-amber-500/5 overflow-hidden p-3"
    >
      <div class="flex items-start gap-3">
        <UIcon name="i-lucide-triangle-alert" class="w-4 h-4 text-amber-500 shrink-0 mt-0.5" />
        <div class="flex-1 min-w-0">
          <p class="text-xs font-semibold text-amber-600 dark:text-amber-400 uppercase tracking-wide">Not launched</p>
          <div class="flex flex-wrap gap-1 mt-2">
            <UBadge
              v-for="module in notLaunched"
              :key="module"
              :label="module"
              color="neutral"
              variant="subtle"
              size="sm"
            />
          </div>
        </div>
      </div>
    </div>

    <!-- Executed -->
    <div
      v-if="executed.length > 0"
      class="flex-1 rounded-lg border border-green-500/30 bg-green-500/5 overflow-hidden p-3"
    >
      <div class="flex items-start gap-3">
        <UIcon name="i-lucide-check-circle-2" class="w-4 h-4 text-green-500 shrink-0 mt-0.5" />
        <div class="flex-1 min-w-0">
          <p class="text-xs font-semibold text-green-600 dark:text-green-400 uppercase tracking-wide">Executed</p>
          <div class="flex flex-wrap gap-1 mt-2">
            <UBadge
              v-for="module in executed"
              :key="module"
              :label="module"
              :color="failed.includes(module) ? 'error' : 'neutral'"
              variant="subtle"
              size="sm"
            />
          </div>
        </div>
      </div>
    </div>
  </div>
</template>