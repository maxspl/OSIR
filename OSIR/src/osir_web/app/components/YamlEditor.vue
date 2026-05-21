<script setup lang="ts">
import hljs from 'highlight.js/lib/core'
import yamlLang from 'highlight.js/lib/languages/yaml'

hljs.registerLanguage('yaml', yamlLang)

const props = defineProps<{
  editableModules: string[]
  moduleYamlMap: Record<string, string>
  yamlErrors: Record<string, string>
  moduleEditMode: Record<string, boolean>
}>()

const emit = defineEmits<{
  'reset': [modulePath: string]
  'yaml-input': [modulePath: string]
  'toggle-edit': [modulePath: string]
}>()

const activeModuleEdit = defineModel<string>('activeModuleEdit')
const editorOpen = defineModel<boolean>('editorOpen')

// local writable copies so v-model on textarea works
const localYamlMap = computed(() => props.moduleYamlMap)
const localEditMode = computed(() => props.moduleEditMode)

function getBasename(modulePath: string): string {
  return modulePath.split('/').pop() || modulePath
}

function wrapLines(html: string): string {
  return html.split('\n').map(line => `<span class="hl-line">${line || '&ZeroWidthSpace;'}</span>`).join('')
}

function getHighlighted(modulePath: string): string {
  const content = props.moduleYamlMap[modulePath] ?? ''
  return wrapLines(hljs.highlight(content, { language: 'yaml' }).value)
}
</script>

<template>
  <Transition
    enter-active-class="transition duration-200 ease-out"
    enter-from-class="opacity-0 -translate-y-1"
    enter-to-class="opacity-100 translate-y-0"
    leave-active-class="transition duration-150 ease-in pointer-events-none"
    leave-from-class="opacity-100 translate-y-0"
    leave-to-class="opacity-0 -translate-y-1"
  >
    <div v-if="editableModules.length > 0" class="rounded-lg bg-(--ui-bg-elevated) border border-(--ui-border) overflow-hidden">

      <!-- Header -->
      <button
        class="w-full flex items-center gap-2 px-4 py-3 text-left hover:bg-(--ui-bg-muted) transition-colors"
        :class="editorOpen ? 'border-b border-(--ui-border)' : ''"
        @click="editorOpen = !editorOpen"
      >
        <UIcon name="i-lucide-file-code-2" class="text-primary w-4 h-4 shrink-0" />
        <span class="text-sm font-semibold text-muted uppercase tracking-wide">Module Configuration</span>
        <UBadge :label="String(editableModules.length)" color="primary" variant="subtle" size="xs" />
        <div class="ml-auto flex items-center gap-2">
          <span v-if="!editorOpen" class="text-xs text-muted">Edit modules YAML</span>
          <UIcon :name="editorOpen ? 'i-lucide-chevron-up' : 'i-lucide-pencil'" class="w-3.5 h-3.5 text-muted" />
        </div>
      </button>

      <!-- Body -->
      <Transition
        enter-active-class="transition duration-200 ease-out"
        enter-from-class="opacity-0 -translate-y-1"
        enter-to-class="opacity-100 translate-y-0"
        leave-active-class="transition duration-150 ease-in pointer-events-none"
        leave-from-class="opacity-100 translate-y-0"
        leave-to-class="opacity-0 -translate-y-1"
      >
        <div v-if="editorOpen">

          <!-- Module selector -->
          <div class="px-4 py-3 border-b border-(--ui-border) bg-(--ui-bg-muted)">
            <USelectMenu
              v-model="activeModuleEdit"
              :items="editableModules.map(m => ({ label: getBasename(m), value: m }))"
              value-key="value"
              label-key="label"
              placeholder="Select a module…"
              size="xl"
              class="w-full"
            />
          </div>

          <!-- Editor area -->
          <div v-if="activeModuleEdit && editableModules.includes(activeModuleEdit)" class="p-4 space-y-3">

            <div v-if="!moduleYamlMap[activeModuleEdit]" class="flex items-center gap-2 text-xs text-muted py-6 justify-center">
              <UIcon name="i-lucide-loader-circle" class="w-3.5 h-3.5 animate-spin" />
              Loading module configuration…
            </div>

            <template v-else>
              <!-- Code block -->
              <div class="rounded-lg overflow-hidden border border-(--ui-border) shadow-sm">
                <div class="flex items-center justify-between px-4 py-2 bg-zinc-900 border-b border-zinc-800">
                  <div class="flex items-center gap-1.5">
                    <span class="w-2.5 h-2.5 rounded-full bg-red-500/70" />
                    <span class="w-2.5 h-2.5 rounded-full bg-yellow-500/70" />
                    <span class="w-2.5 h-2.5 rounded-full bg-green-500/70" />
                  </div>
                  <span class="text-xs font-mono text-zinc-400">{{ getBasename(activeModuleEdit) }}</span>
                  <span class="text-xs font-mono text-zinc-600 tracking-widest">YAML</span>
                </div>

                <pre
                  v-if="!moduleEditMode[activeModuleEdit]"
                  class="yaml-viewer m-0 p-4 text-xs font-mono leading-5 overflow-x-auto bg-zinc-950 max-h-96"
                ><code class="hljs language-yaml" v-html="getHighlighted(activeModuleEdit)" /></pre>

                <textarea
                  v-else
                  :value="moduleYamlMap[activeModuleEdit]"
                  class="w-full h-96 font-mono text-xs bg-zinc-950 text-zinc-100 p-4 resize-y focus:outline-none leading-5 border-0 block"
                  :class="yamlErrors[activeModuleEdit] ? 'ring-1 ring-inset ring-error' : ''"
                  spellcheck="false"
                  autocomplete="off"
                  @input="emit('yaml-input', activeModuleEdit)"
                />
              </div>

              <!-- Status bar -->
              <div class="flex items-center justify-between">
                <p v-if="yamlErrors[activeModuleEdit]" class="text-xs text-error flex items-center gap-1">
                  <UIcon name="i-lucide-alert-circle" class="w-3 h-3 shrink-0" />
                  {{ yamlErrors[activeModuleEdit] }}
                </p>
                <p v-else class="text-xs text-muted flex items-center gap-1">
                  <UIcon name="i-lucide-check-circle" class="w-3 h-3 shrink-0 text-success" />
                  Valid YAML
                </p>
                <div class="flex items-center gap-2">
                  <UButton size="xs" variant="ghost" icon="i-lucide-rotate-ccw" @click="emit('reset', activeModuleEdit)">
                    Reset
                  </UButton>
                  <UButton
                    size="xs"
                    :variant="moduleEditMode[activeModuleEdit] ? 'solid' : 'outline'"
                    :icon="moduleEditMode[activeModuleEdit] ? 'i-lucide-eye' : 'i-lucide-pencil'"
                    @click="emit('toggle-edit', activeModuleEdit)"
                  >
                    {{ moduleEditMode[activeModuleEdit] ? 'Apply' : 'Edit' }}
                  </UButton>
                </div>
              </div>
            </template>
          </div>

        </div>
      </Transition>
    </div>
  </Transition>
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
