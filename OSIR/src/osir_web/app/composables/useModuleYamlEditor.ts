import { stringify as yamlStringify, parse as yamlParse } from 'yaml'
import { useModuleStore } from '~/stores/module'

export function useModuleYamlEditor(
  selectedModules: Ref<string[]>,
  modulesToAdd: Ref<string[]>,
  modulesToRemove: Ref<string[]>,
) {
  const moduleStore = useModuleStore()

  const activeModuleEdit = ref<string>('')
  const moduleYamlMap = ref<Record<string, string>>({})
  const moduleOriginalYamlMap = ref<Record<string, string>>({})
  const yamlErrors = ref<Record<string, string>>({})
  const moduleEditMode = ref<Record<string, boolean>>({})
  const editorOpen = ref(false)

  const editableModules = computed(() => [
    ...new Set([...selectedModules.value, ...modulesToAdd.value]),
  ].filter(m => !modulesToRemove.value.includes(m)))

  function getBasename(modulePath: string): string {
    return modulePath.split('/').pop() || modulePath
  }

  function wrapLines(html: string): string {
    return html.split('\n').map(line => `<span class="hl-line">${line || '&ZeroWidthSpace;'}</span>`).join('')
  }

  function getHighlighted(modulePath: string): string {
    import('highlight.js/lib/core').then(async ({ default: hljs }) => {
      const { default: yamlLang } = await import('highlight.js/lib/languages/yaml')
      hljs.registerLanguage('yaml', yamlLang)
    })
    const content = moduleYamlMap.value[modulePath] ?? ''
    // Lazy import — hljs should already be registered by the page
    try {
      const hljs = (globalThis as any).__hljs
      if (hljs) return wrapLines(hljs.highlight(content, { language: 'yaml' }).value)
    } catch {}
    return wrapLines(content)
  }

  function initModuleYaml(modulePath: string) {
    const info = moduleStore.moduleInfoMap[modulePath]
    if (info) {
      const yamlContent = yamlStringify(info, { indent: 2 })
      moduleYamlMap.value[modulePath] = yamlContent
      moduleOriginalYamlMap.value[modulePath] = yamlContent
      delete yamlErrors.value[modulePath]
    }
  }

  function resetModule(modulePath: string) {
    initModuleYaml(modulePath)
    moduleEditMode.value[modulePath] = false
  }

  function onYamlInput(modulePath: string) {
    const content = moduleYamlMap.value[modulePath]
    if (!content) return
    try {
      yamlParse(content)
      delete yamlErrors.value[modulePath]
    } catch (e) {
      yamlErrors.value[modulePath] = (e as Error).message
    }
  }

  function removeModuleYaml(modulePath: string) {
    delete moduleYamlMap.value[modulePath]
    delete moduleOriginalYamlMap.value[modulePath]
    delete yamlErrors.value[modulePath]
    delete moduleEditMode.value[modulePath]
  }

  function getModifiedModules(): any[] | null {
    const modified: any[] = []
    for (const [modulePath, yamlContent] of Object.entries(moduleYamlMap.value)) {
      if (yamlContent && moduleOriginalYamlMap.value[modulePath]) {
        if (yamlContent !== moduleOriginalYamlMap.value[modulePath]) {
          try {
            modified.push(yamlParse(yamlContent))
          } catch (e) {
            console.error(`Failed to parse YAML for module ${modulePath}:`, e)
          }
        }
      }
    }
    return modified.length > 0 ? modified : null
  }

  // Watchers
  watch(modulesToAdd, (newModulesToAdd) => {
    newModulesToAdd.forEach(m => {
      if (!moduleYamlMap.value[m]) initModuleYaml(m)
    })
  }, { deep: true })

  watch(modulesToRemove, (newModulesToRemove) => {
    newModulesToRemove.forEach(m => removeModuleYaml(m))
  }, { deep: true })

  watch(selectedModules, (newModules) => {
    for (const modulePath in moduleYamlMap.value) {
      if (!newModules.includes(modulePath)) removeModuleYaml(modulePath)
    }
    newModules.forEach(m => {
      if (!moduleYamlMap.value[m]) initModuleYaml(m)
    })
    if (editableModules.value.length === 0) {
      activeModuleEdit.value = ''
      editorOpen.value = false
    } else if (!activeModuleEdit.value || !editableModules.value.includes(activeModuleEdit.value)) {
      activeModuleEdit.value = editableModules.value[0] ?? ''
    }
  }, { deep: true })

  watch(() => moduleStore.moduleInfoMap, (map) => {
    selectedModules.value.forEach(m => {
      if (map[m] && !moduleYamlMap.value[m]) initModuleYaml(m)
    })
  }, { deep: true })

  return {
    activeModuleEdit,
    moduleYamlMap,
    yamlErrors,
    moduleEditMode,
    editorOpen,
    editableModules,
    getBasename,
    getHighlighted,
    initModuleYaml,
    resetModule,
    onYamlInput,
    getModifiedModules,
  }
}
