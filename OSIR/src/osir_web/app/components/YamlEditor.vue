<script setup lang="ts">
import { ref, computed, watch, nextTick } from 'vue'

function cssVar(name: string, fallback = '#000000'): string {
  if (typeof window === 'undefined') return fallback
  const raw = getComputedStyle(document.documentElement).getPropertyValue(name).trim()
  if (!raw) return fallback

  const canvas = document.createElement('canvas')
  canvas.width = canvas.height = 1
  const ctx = canvas.getContext('2d')
  if (!ctx) return fallback
  ctx.fillStyle = raw
  ctx.fillRect(0, 0, 1, 1)
  const [r, g, b] = ctx.getImageData(0, 0, 1, 1).data
  return '#' + [r, g, b].map(n => n.toString(16).padStart(2, '0')).join('')
}

function defineNuxtUITheme(monaco: any) {
  const bg = cssVar('--ui-bg', '#0f0f0f')
  const bgElevated = cssVar('--ui-bg-elevated', '#18181b')
  const bgMuted = cssVar('--ui-bg-muted', '#27272a')
  const border = cssVar('--ui-border', '#3f3f46')
  const fg = cssVar('--ui-text', '#f4f4f5')
  const fgMuted = cssVar('--ui-text-muted', '#a1a1aa')
  const fgDimmed = cssVar('--ui-text-dimmed', '#71717a')
  const primary = cssVar('--ui-primary', '#6366f1')
  const error = cssVar('--ui-error', '#f87171')
  const success = cssVar('--ui-success', '#34d399')
  const warning = cssVar('--ui-warning', '#fbbf24')
  const info = cssVar('--ui-info', '#38bdf8')

  monaco.editor.defineTheme('nuxt-ui', {
    base: 'vs-dark',
    inherit: true,

    colors: {
      'editor.background': bgElevated,
      'editor.foreground': fg,

      'editor.lineHighlightBackground': bgMuted + '80',
      'editor.lineHighlightBorder': '#00000000',

      'editor.selectionBackground': primary + '55',
      'editor.inactiveSelectionBackground': primary + '30',
      'editor.selectionHighlightBackground': primary + '30',

      'editor.wordHighlightBackground': '#00000000',
      'editor.wordHighlightBorder': '#00000000',
      'editor.wordHighlightStrongBackground': '#00000000',
      'editor.wordHighlightStrongBorder': '#00000000',
      'editor.wordHighlightTextBackground': '#00000000',
      'editor.wordHighlightTextBorder': '#00000000',

      'editor.findMatchBackground': warning + '50',
      'editor.findMatchHighlightBackground': warning + '25',
      'editor.findMatchBorder': warning,

      'editorLineNumber.foreground': fgDimmed,
      'editorLineNumber.activeForeground': fgMuted,

      'editorCursor.foreground': primary,

      'editorGutter.background': bgElevated,

      'editorIndentGuide.background1': border,
      'editorIndentGuide.activeBackground1': fgDimmed,

      'editorWhitespace.foreground': fgDimmed + '60',

      'scrollbar.shadow': '#00000000',
      'scrollbarSlider.background': fgDimmed + '40',
      'scrollbarSlider.hoverBackground': fgDimmed + '70',
      'scrollbarSlider.activeBackground': fgMuted,

      'minimap.background': bg,
      'minimapSlider.background': fgDimmed + '40',

      'editorWidget.background': bgMuted,
      'editorWidget.border': border,
      'editorWidget.foreground': fg,
      'editorSuggestWidget.background': bgMuted,
      'editorSuggestWidget.border': border,
      'editorSuggestWidget.selectedBackground': primary + '30',
      'editorSuggestWidget.highlightForeground': primary,

      'editorHoverWidget.background': bgMuted,
      'editorHoverWidget.border': border,

      'editorError.foreground': error,
      'editorWarning.foreground': warning,
      'editorInfo.foreground': primary,

      'editorBracketMatch.background': primary + '25',
      'editorBracketMatch.border': primary + '80',

      'editorOverviewRuler.border': border,
      'editorOverviewRuler.errorForeground': error,
      'editorOverviewRuler.warningForeground': warning,

      'focusBorder': primary,
      'contrastBorder': '#00000000',
      'editorStickyScrollHover.background': '#00000000',
    },

    rules: [
      { token: 'type.yaml', foreground: fgMuted.slice(1) },
      { token: 'string.yaml', foreground: primary.slice(1) },
      { token: 'string.unquoted.yaml', foreground: primary.slice(1) },
      { token: 'number.yaml', foreground: warning.slice(1) },
      { token: 'keyword.yaml', foreground: error.slice(1) },
      { token: 'comment.yaml', foreground: primary.slice(1), fontStyle: 'italic' },
      { token: 'delimiter.yaml', foreground: primary.slice(1) },
      { token: 'operators.yaml', foreground: primary.slice(1) },
      { token: 'type.anchor.yaml', foreground: primary.slice(1) },
      { token: 'type.alias.yaml', foreground: primary.slice(1) },
      { token: 'tag.yaml', foreground: primary.slice(1) },
      { token: 'invalid.yaml', foreground: error.slice(1) },
    ],
  })
}
const props = defineProps<{
  editableModules: string[]
  moduleYamlMap: Record<string, string>
  yamlErrors: Record<string, string>
  moduleEditMode: Record<string, boolean>
}>()

const emit = defineEmits<{
  'reset': [modulePath: string]
  'yaml-input': [modulePath: string, value: string]
  'toggle-edit': [modulePath: string]
}>()

const activeModuleEdit = defineModel<string>('activeModuleEdit')
const editorOpen = defineModel<boolean>('editorOpen')

const monacoEditorRef = ref<any>(null)
const isMonacoLoading = ref(true)

function getBasename(modulePath: string): string {
  return modulePath.split('/').pop() || modulePath
}

const editorOptions = computed(() => ({
  language: 'yaml',
  theme: 'nuxt-ui',
  minimap: { enabled: false },
  lineNumbers: 'on',
  lineDecorationsWidth: 10,
  lineNumbersMinChars: 2,
  fontSize: 12,
  wordWrap: 'on',
  scrollBeyondLastLine: false,
  automaticLayout: true,
  padding: { top: 10, bottom: 10 },
  readOnly: activeModuleEdit.value ? !props.moduleEditMode[activeModuleEdit.value] : true,
}))

const currentYaml = computed({
  get: () => activeModuleEdit.value ? (props.moduleYamlMap[activeModuleEdit.value] ?? '') : '',
  set: (value: string) => {
    if (activeModuleEdit.value) {
      emit('yaml-input', activeModuleEdit.value, value)
    }
  },
})

watch(
  () => activeModuleEdit.value ? props.moduleEditMode[activeModuleEdit.value] : null,
  (isEditable) => {
    if (monacoEditorRef.value) {
      monacoEditorRef.value.updateOptions({ readOnly: !isEditable })
    }
  },
)

const monacoInstance = ref<any>(null)

async function handleEditorMount(editor: any) {
  monacoEditorRef.value = editor

  const monaco = await useMonaco()
  monacoInstance.value = monaco

  defineNuxtUITheme(monaco)
  editor.updateOptions({ theme: 'nuxt-ui' })

  if (activeModuleEdit.value) {
    editor.updateOptions({ readOnly: !props.moduleEditMode[activeModuleEdit.value] })
  }
  isMonacoLoading.value = false
}

const colorMode = useColorMode()

watch(() => colorMode.value, async () => {
  if (!monacoInstance.value) return
  await nextTick()
  defineNuxtUITheme(monacoInstance.value)
  monacoEditorRef.value?.updateOptions({ theme: 'nuxt-ui' })
  
})


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

      <button
        class="w-full flex items-center gap-2 px-4 py-3 text-left hover:bg-(--ui-bg-muted) transition-colors"
        :class="editorOpen ? 'border-b border-(--ui-border)' : ''"
        @click="editorOpen = !editorOpen"
      >
        <UIcon name="i-lucide-file-code-2" class="text-primary w-4 h-4 shrink-0" />
        <span class="text-sm font-semibold text-muted uppercase tracking-wide">Module Configuration</span>
        <UBadge :label="String(editableModules.length)" color="primary" variant="subtle" size="md" />
        <div class="ml-auto flex items-center gap-2">
          <span v-if="!editorOpen" class="text-xs text-muted">Edit modules YAML</span>
          <UIcon :name="editorOpen ? 'i-lucide-chevron-up' : 'i-lucide-pencil'" class="w-3.5 h-3.5 text-muted" />
        </div>
      </button>

      <Transition
        enter-active-class="transition duration-200 ease-out"
        enter-from-class="opacity-0 -translate-y-1"
        enter-to-class="opacity-100 translate-y-0"
        leave-active-class="transition duration-150 ease-in pointer-events-none"
        leave-from-class="opacity-100 translate-y-0"
        leave-to-class="opacity-0 -translate-y-1"
      >
        <div v-if="editorOpen">

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

          <div v-if="activeModuleEdit && editableModules.includes(activeModuleEdit)" class="p-4 space-y-3">

            <div v-if="!moduleYamlMap[activeModuleEdit]" class="flex items-center gap-2 text-xs text-muted py-6 justify-center">
              <UIcon name="i-lucide-loader-circle" class="w-3.5 h-3.5 animate-spin" />
                Loading module configuration...
            </div>

            <template v-else>
              <MonacoEditor
                v-model="currentYaml"
                lang="yaml"
                :options="editorOptions"
                class="w-full"
                style="height: 320px"
                @load="handleEditorMount"
              />
              <div v-if="isMonacoLoading" class="flex items-center gap-2 text-xs text-muted py-6 justify-center">
                <UIcon name="i-lucide-loader-circle" class="w-3.5 h-3.5 animate-spin" />
                Loading editor...
              </div>

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