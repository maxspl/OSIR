<script setup lang="ts">
defineProps<{
  badge: string
  title: string
  description: string
}>()
</script>

<template>
  <div class="space-y-2">
    <UBadge
      :label="badge"
      color="primary"
      variant="subtle"
      size="sm"
      icon="i-lucide-folder-open"
    />
    <h1 class="text-2xl font-bold text-primary uppercase leading-tight font-syne">
      {{ title }}
    </h1>
    <p class="text-sm text-muted">
      {{ description }}
    </p>
  </div>
</template>