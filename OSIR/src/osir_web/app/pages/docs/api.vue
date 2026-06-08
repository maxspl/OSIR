<script setup lang="ts">
const { protocol, hostname } = useRequestURL()
const apiDocsUrl = `${protocol}//${hostname}:8502/docs`
</script>

<template>
  <docsFrame
    title="API Docs"
    :url="apiDocsUrl"
    icon="i-lucide-code-2"
    label="FastAPI"
    iframeTitle="FastAPI documentation"
    sandbox="allow-same-origin allow-scripts allow-forms"
  />
</template>