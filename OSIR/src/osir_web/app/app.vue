<script setup>
import pkg from '../package.json'

useHead({
  meta: [
    { name: 'viewport', content: 'width=device-width, initial-scale=1' }
  ],
  link: [
    { rel: 'icon', href: '/favicon.ico' }
  ],
  htmlAttrs: {
    lang: 'en'
  }
})

const title = 'OSIR'
const description = 'Open Software for Incident Response — Orchestration & Monitoring platform.'

// Splunk link based on the FQDN the user is on (instead of a hardcoded localhost).
// useRequestURL() gives the request host on the server and window.location on the client.
const splunkUrl = computed(() => `http://${useRequestURL().hostname}:8000`)

useSeoMeta({
  title,
  description,
  ogTitle: title,
  ogDescription: description,
  twitterCard: 'summary_large_image'
})

const toaster = { position: 'top-right', max:5 }
</script>

<template>
  <UApp :toaster="toaster">
    <UHeader>
      <template #left>
        <NuxtLink to="/" class="flex items-center gap-2 shrink-0">
          <span class="text-3xl font-extrabold tracking-tight font-syne"><span class="text-primary dark:text-white">O</span><span class="text-primary dark:text-white">S</span><span class="text-primary">I</span><span class="text-primary">R</span></span>
          <UBadge :label="`v${pkg.version}`" color="primary" variant="subtle" size="md" class="rounded-full" />
        </NuxtLink>
      </template>

      <OsirMenu />

      <template #body>
        <OsirMenu orientation="vertical" />
      </template>

      <template #right>
        <UColorModeButton />

        <UButton
          to="https://github.com/maxspl/OSIR"
          target="_blank"
          icon="i-simple-icons-github"
          aria-label="GitHub"
          color="neutral"
          variant="ghost"
        />
        <UButton
          :to="splunkUrl"
          target="_blank"
          aria-label="Splunk"
          color="neutral"
          variant="ghost"
        >
            <img
              src="~/assets/Splunk-Symbol.png"
              alt="GitHub"
              class="h-5"
            >
        </UButton>

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
