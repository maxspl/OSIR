<script setup lang="ts">
withDefaults(defineProps<{
  orientation?: 'horizontal' | 'vertical'
}>(), {
  orientation: 'horizontal'
})

const items = useOsirMenuItems()
</script>

<template>
  <UNavigationMenu :items="items" :orientation="orientation" />
</template>
