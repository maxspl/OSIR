<script setup lang="ts">
import { menuItems } from '~/utils/monitoring'
import type { View } from '~/composables/useMonitoringNavigation'

const activeView = defineModel<View>('activeView')
</script>

<template>
  <div class="flex items-center gap-1 p-1 rounded-lg bg-(--ui-bg-elevated) border border-(--ui-border) w-fit">
    <UButton
      v-for="item in menuItems"
      :key="item.view"
      :label="item.label"
      :icon="item.icon"
      size="sm"
      :variant="activeView === item.view ? 'solid' : 'ghost'"
      :color="activeView === item.view ? 'primary' : 'neutral'"
      @click="activeView = item.view"
    />
  </div>
</template>