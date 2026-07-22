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
  devServer: {
    port: 8501
  },
  modules: [
    '@nuxt/eslint',
    '@nuxt/ui',
    '@pinia/nuxt',
    'nuxt-monaco-editor',
  ],

  devtools: {
    enabled: true
  },

  // Disable sourcemap generation at build time: on a bundle that includes monaco-editor,
  // generating sourcemaps (the server ones especially) is very memory-heavy and OOMs the
  // build on low-RAM machines. No runtime impact (sourcemaps are only used for debugging).
  sourcemap: { server: false, client: false },

  css: ['~/assets/css/main.css', 'highlight.js/styles/atom-one-dark.css'],

  routeRules: {
    // '/' only redirects to /cases (see pages/index.vue): no point prerendering it, and
    // prerendering loads the whole server bundle (monaco…) → OOM at build time.
    // We just disable prerendering (runtime behaviour unchanged).
    '/': { prerender: false },
    '/proxy/**': { proxy: 'http://master-api:8502/**' },
    '/flower/**': { proxy: 'http://master-flower:5555/**' }
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
        'yaml',
        'highlight.js/lib/core',
        'highlight.js/lib/languages/yaml',
        '@uppy/tus',
        'nuxt-monaco-editor',
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
