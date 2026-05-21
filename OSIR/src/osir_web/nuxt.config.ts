// https://nuxt.com/docs/api/configuration/nuxt-config

function isolateVueFinderLayers(css: string): string {
  // Only rename @layer blocks to prevent merging with Tailwind/Nuxt UI layers.
  // e.g. "@layer utilities { .hidden }" → "@layer vf-utilities { .hidden }"
  // This avoids selector scoping so VueFinder teleported modals still work.
  return css.replace(/@layer\s+([\w,\s]+)(?=\s*\{)/g, (match, names: string) => {
    const renamed = names
      .split(',')
      .map((n: string) => `vf-${n.trim()}`)
      .join(', ')
    return `@layer ${renamed}`
  })
}

export default defineNuxtConfig({
  modules: [
    '@nuxt/eslint',
    '@nuxt/ui',
    '@pinia/nuxt',
  ],

  devtools: {
    enabled: true
  },

  css: ['~/assets/css/main.css', 'highlight.js/styles/atom-one-dark.css'],

  routeRules: {
    '/': { prerender: true }
  },

  compatibilityDate: '2025-01-15',

  eslint: {
    config: {
      stylistic: {
        commaDangle: 'never',
        braceStyle: '1tbs'
      }
    }
  },

  vite: {
    optimizeDeps: {
      include: [
        '@vue/devtools-core',
        '@vue/devtools-kit',
        'vuefinder',
      ]
    },
    plugins: [
      {
        name: 'scope-vuefinder-css',
        enforce: 'pre',
        transform(code: string, id: string) {
          if (id.includes('vuefinder') && id.includes('.css')) {
            return { code: isolateVueFinderLayers(code), map: null }
          }
        }
      }
    ]
  }
})
