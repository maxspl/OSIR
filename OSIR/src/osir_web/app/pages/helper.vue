<script setup lang="ts">
import hljs from 'highlight.js/lib/core'
import yamlLang from 'highlight.js/lib/languages/yaml'
import { stringify as yamlStringify } from 'yaml'
import { useProfileStore } from '~/stores/profile'
import { useModuleStore } from '~/stores/module'

hljs.registerLanguage('yaml', yamlLang)

useSeoMeta({ title: 'OSIR — Helper Modules & Profiles' })

// ── Stores ──────────────────────────────────────────────────────────────────
const profileStore = useProfileStore()
const moduleStore = useModuleStore()

// ── Fetch data on mount ────────────────────────────────────────────────────
onMounted(async () => {
  await profileStore.fetchProfiles()
  await profileStore.fetchAllProfileInfos()
  await moduleStore.fetchModules()
  await moduleStore.fetchModuleInfos()
})

onBeforeUnmount(() => {
  profileStore.stopPolling()
  moduleStore.stopPolling()
})

// ── State ───────────────────────────────────────────────────────────────────
type Source = 'profile' | 'module'
const activeSource = ref<Source>('profile')

const selectedProfile = ref<string>('')
const selectedModule = ref<string>('')

// ── Computed options ───────────────────────────────────────────────────────
const profileOptions = computed(() => profileStore.profileOptions)
const moduleOptions = computed(() => moduleStore.moduleOptions)

// ── YAML Content ────────────────────────────────────────────────────────────
// Serialize the real object directly (like the module editor) instead of rebuilding a
// hand-made, flattened/incomplete pseudo-YAML → correct and complete output.
function generateProfileYaml(profileName: string): string {
  const info = profileStore.profileInfoMap[profileName]
  if (!info) return `# Profile: ${profileName}\nNo info available`
  return `# Profile: ${profileName}\n${yamlStringify(info, { indent: 2 })}`
}

function generateModuleYaml(moduleName: string): string {
  const info = moduleStore.moduleInfoMap[moduleName]
  if (!info) return `# Module: ${moduleName}\nNo info available`
  return `# Module: ${moduleName}\n${yamlStringify(info, { indent: 2 })}`
}

const currentKey = computed(() =>
  activeSource.value === 'profile' ? selectedProfile.value : selectedModule.value,
)

const currentFilename = computed(() =>
  activeSource.value === 'profile'
    ? `profile-${selectedProfile.value}.yaml`
    : `module-${selectedModule.value}.yaml`,
)

const yamlContent = computed(() => {
  if (activeSource.value === 'profile') {
    return generateProfileYaml(selectedProfile.value)
  }
  return generateModuleYaml(selectedModule.value)
})

// Update active source when selection changes
watch(selectedProfile, () => { activeSource.value = 'profile' })
watch(selectedModule, () => { activeSource.value = 'module' })

// Don't auto-select - force user to make a choice
// selectedProfile and selectedModule remain empty by default

function wrapLines(html: string): string {
  return html.split('\n').map(line => `<span class="hl-line">${line || '&ZeroWidthSpace;'}</span>`).join('')
}

const highlighted = computed(() =>
  wrapLines(hljs.highlight(yamlContent.value, { language: 'yaml' }).value),
)
</script>

<template>
  <UPage>
    <div class="max-w-6xl mx-auto px-4 py-10 space-y-6">

      <!-- Panel -->
      <div class="rounded-lg border border-(--ui-border) overflow-hidden">
        <div class="flex items-center gap-2 px-4 py-3 bg-(--ui-bg-elevated) border-b border-(--ui-border)">
          <UIcon name="i-lucide-life-buoy" class="w-4 h-4 text-primary shrink-0" />
          <span class="text-xs font-semibold uppercase tracking-wide">Helper — Modules &amp; Profiles</span>
        </div>

      <!-- Selects -->
      <div class="flex gap-4 px-4 py-4">
        <UFormField label="Profile" class="flex-1">
          <USelectMenu
            v-model="selectedProfile"
            :items="profileOptions"
            value-key="value"
            label-key="label"
            placeholder="Select a profile…"
            icon="i-lucide-user-circle"
            class="w-full"
          />
        </UFormField>

        <UFormField label="Module" class="flex-1">
          <USelectMenu
            v-model="selectedModule"
            :items="moduleOptions"
            value-key="value"
            label-key="label"
            placeholder="Select a module…"
            icon="i-lucide-puzzle"
            class="w-full"
          />
        </UFormField>
      </div>

      <!-- YAML Viewer -->
      <div class="px-4 pb-4">
      <Transition
        enter-active-class="transition duration-150 ease-out"
        enter-from-class="opacity-0 translate-y-1"
        enter-to-class="opacity-100 translate-y-0"
        leave-active-class="transition duration-100 ease-in"
        leave-from-class="opacity-100 translate-y-0"
        leave-to-class="opacity-0 translate-y-1"
        mode="out-in"
      >
        <div :key="currentKey" class="rounded-lg overflow-hidden border border-(--ui-border) shadow-md">
          <!-- Titlebar -->
          <div class="flex items-center justify-between px-4 py-2 bg-zinc-900 border-b border-zinc-800">
            <div class="flex items-center gap-2">
              <span class="w-3 h-3 rounded-full bg-red-500/70" />
              <span class="w-3 h-3 rounded-full bg-yellow-500/70" />
              <span class="w-3 h-3 rounded-full bg-green-500/70" />
            </div>
            <span class="text-xs font-mono text-zinc-400">{{ currentFilename }}</span>
            <span class="text-xs font-mono text-zinc-600 tracking-widest">YAML</span>
          </div>
          <!-- Code -->
          <pre class="yaml-viewer m-0 p-4 text-sm font-mono leading-6 overflow-x-auto bg-zinc-950"><code class="hljs language-yaml" v-html="highlighted" /></pre>
        </div>
      </Transition>
      </div>

      </div>
    </div>
  </UPage>
</template>

<style scoped>
.yaml-viewer {
  tab-size: 2;
  counter-reset: line;
}

:deep(.hl-line) {
  display: block;
  counter-increment: line;
}

:deep(.hl-line::before) {
  content: counter(line);
  display: inline-block;
  width: 2rem;
  margin-right: 1.5rem;
  text-align: right;
  color: #3f3f46;
  user-select: none;
}
</style>
