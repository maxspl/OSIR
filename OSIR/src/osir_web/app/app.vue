<script setup>
useHead({
  meta: [
    { name: 'viewport', content: 'width=device-width, initial-scale=1' }
  ],
  link: [
    { rel: 'icon', href: '/favicon.ico' },
    { rel: 'preconnect', href: 'https://fonts.googleapis.com' },
    { rel: 'preconnect', href: 'https://fonts.gstatic.com', crossorigin: '' },
    { rel: 'stylesheet', href: 'https://fonts.googleapis.com/css2?family=Syne:wght@800&display=swap' }
  ],
  htmlAttrs: {
    lang: 'en'
  }
})

const title = 'OSIR'
const description = 'Open Source Incident Response — Orchestration & Monitoring platform.'

useSeoMeta({
  title,
  description,
  ogTitle: title,
  ogDescription: description,
  twitterCard: 'summary_large_image'
})
</script>

<template>
  <UApp>
    <UHeader>
      <template #left>
        <NuxtLink to="/" class="flex items-center gap-2 shrink-0">
          <span class="text-3xl font-extrabold tracking-tight font-syne"><span class="text-primary dark:text-white">O</span><span class="text-primary dark:text-white">S</span><span class="text-primary">I</span><span class="text-primary">R</span></span>
          <UBadge label="v1.0.0" color="primary" variant="subtle" size="md" class="rounded-full" />
        </NuxtLink>
      </template>

      <OsirMenu />

      <template #right>
        <UColorModeButton />

        <UButton
          to="https://github.com"
          target="_blank"
          icon="i-simple-icons-github"
          aria-label="GitHub"
          color="neutral"
          variant="ghost"
        />

        <!-- <UDropdownMenu
          :items="[[
            { label: 'Profile', icon: 'i-lucide-user', disabled: true },
            { label: 'Settings', icon: 'i-lucide-settings', disabled: true },
          ], [
            { label: 'Sign out', icon: 'i-lucide-log-out', color: 'error', disabled: true },
          ]]"
        >
          <UButton
            icon="i-lucide-circle-user"
            aria-label="User profile"
            color="neutral"
            variant="ghost"
          />
        </UDropdownMenu> -->
      </template>
    </UHeader>

    <UMain>
      <NuxtPage />
    </UMain>

    <USeparator />

    <UFooter>
      <template #left>
        <p class="text-sm text-muted">
          Orchestration Software for Incident Response • © {{ new Date().getFullYear() }}
        </p>
      </template>

      <template #right>
        <UButton
          to="https://github.com/maxspl/osir"
          target="_blank"
          icon="i-simple-icons-github"
          aria-label="GitHub"
          color="neutral"
          variant="ghost"
        />
      </template>
    </UFooter>
  </UApp>
</template>
