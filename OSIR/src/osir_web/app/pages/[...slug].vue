<script setup>
const route = useRoute()

throw createError({
  statusCode: 404,
  statusMessage: `Not found : ${route.path}`,
  fatal: false,
})
</script>

<template>
  <div/>
</template>