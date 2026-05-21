<script setup lang="ts">

const props = defineProps<{
  title: string
  url: string
  icon: string
  label: string
  iframeTitle: string
  sandbox?: string
}>()

useSeoMeta({ title: props.title })

</script>

<template>
  <UPage>
    <div class="max-w-6xl mx-auto px-4 py-10 space-y-6">
      <div class="rounded-lg border border-(--ui-border) overflow-hidden">
        <div class="flex items-center gap-2 px-4 py-3 bg-(--ui-bg-elevated) border-b border-(--ui-border)">
          <UIcon :name="icon" class="w-4 h-4 text-primary shrink-0" />
          <span class="text-xs font-semibold uppercase tracking-wide">{{ label }}</span>
          <UButton
            :href="url"
            target="_blank"
            icon="i-lucide-external-link"
            size="xs"
            variant="ghost"
            color="neutral"
            class="ml-auto"
          />
        </div>
        <iframe
          :src="url"
          class="w-full border-0"
          style="height: 780px;"
          :title="iframeTitle"
          :sandbox="sandbox"
        />
      </div>
    </div>
  </UPage>
</template>