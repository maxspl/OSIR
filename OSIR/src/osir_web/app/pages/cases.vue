<script setup lang="ts">
import type { TableRow } from '@nuxt/ui'
import { useCaseStore } from '~/stores/case'
import { useModuleStore } from '~/stores/module'
import { useProfileStore } from '~/stores/profile'
import OrchestratorControls from '~/components/orchestration/OrchestratorControls.vue'
import YamlEditor from '~/components/YamlEditor.vue'
import ModuleTable from '~/components/orchestration/ModuleTable.vue'
import OrchestrationFooter from '~/components/orchestration/OrchestrationFooter.vue'

useSeoMeta({ title: 'OSIR — Profile & Modules' })

// ── Stores ────────────────────────────────────────────────────────────────────
const caseStore = useCaseStore()
const moduleStore = useModuleStore()
const profileStore = useProfileStore()

// ── Initial data fetch ────────────────────────────────────────────────────────
await Promise.all([
  caseStore.fetchCases(),
  moduleStore.fetchModules(),
  profileStore.fetchProfiles(),
])
moduleStore.fetchModuleInfos()

onMounted(() => {
  caseStore.startPolling(50000)
  moduleStore.startPolling(50000)
  profileStore.startPolling(50000)
})
onUnmounted(() => {
  caseStore.stopPolling()
  moduleStore.stopPolling()
  profileStore.stopPolling()
})

// ── State ─────────────────────────────────────────────────────────────────────
const selectedCase = ref<string | undefined>()
const selectedProfile = ref<string | null>(null)
const selectedModules = ref<string[]>([])
const modulesToAdd = ref<string[]>([])
const modulesToRemove = ref<string[]>([])
const reprocessFile = ref(false)
const rowSelection = ref<Record<string, boolean>>({})

type ModuleModel = { module_path: string; description: string; processor: string }

const tableRows = computed<ModuleModel[]>(() =>
  moduleStore.modules.map(m => ({
    module_path: m,
    description: moduleStore.moduleInfoMap[m]?.metadata?.description ?? '—',
    processor: (moduleStore.moduleInfoMap[m]?.configuration?.processor_type ?? []).join(' / ') || '—',
  }))
)



// ── Profile watch ─────────────────────────────────────────────────────────────
watch(selectedProfile, async (name) => {
  if (!name) {
    selectedModules.value = []
    modulesToAdd.value = []
    modulesToRemove.value = []
    rowSelection.value = {}
    return
  }
  await profileStore.fetchProfileInfo(name)
  selectedModules.value = moduleStore.getInProfileModuleOptions(profileStore.profileInfoMap[name]?.modules ?? []).map(o => o.value)
  modulesToAdd.value = []
  modulesToRemove.value = []
  selectByPath(selectedModules.value)
})

// ── Table row selection helpers ───────────────────────────────────────────────
function selectByPath(paths: string[]) {
  rowSelection.value = {}
  paths.forEach(path => {
    const index = tableRows.value.findIndex(r => r.module_path === path)
    if (index !== -1) rowSelection.value[index.toString()] = true
  })
}

function onTableSelect(event: Event, row: TableRow<ModuleModel>) {
  if (!row.getIsSelected()) {
    selectedModules.value.push(row.original.module_path)
  } else {
    selectedModules.value = selectedModules.value.filter(p => p !== row.original.module_path)
  }
  row.toggleSelected(!row.getIsSelected())
}

// ── YAML editor ───────────────────────────────────────────────────────────────
const {
  activeModuleEdit,
  moduleYamlMap,
  yamlErrors,
  moduleEditMode,
  editorOpen,
  editableModules,
  resetModule,
  onYamlInput,
  getModifiedModules,
} = useModuleYamlEditor(selectedModules, modulesToAdd, modulesToRemove)

// ── Submit ────────────────────────────────────────────────────────────────────
const { isSubmitting, handleSubmit } = useOrchestrationSubmit(
  selectedCase,
  selectedProfile,
  selectedModules,
  modulesToAdd,
  modulesToRemove,
  reprocessFile,
  getModifiedModules,
)
</script>

<template>
  <UPage>
    <div class="max-w-6xl mx-auto px-4 py-10 space-y-8">

      <OsirHeader
        badge="Cases Orchestration"
        title="Profile & Modules"
        description="Execute Profile & Modules on case."
      />

      <USeparator />

      <OrchestratorControls
        v-model:selected-case="selectedCase"
        v-model:selected-profile="selectedProfile"
        v-model:selected-modules="selectedModules"
        v-model:modules-to-add="modulesToAdd"
        v-model:modules-to-remove="modulesToRemove"
        @select-by-path="selectByPath"
      />

      <YamlEditor
        v-model:active-module-edit="activeModuleEdit"
        v-model:editor-open="editorOpen"
        :editable-modules="editableModules"
        :module-yaml-map="moduleYamlMap"
        :yaml-errors="yamlErrors"
        :module-edit-mode="moduleEditMode"
        @reset="resetModule"
        @yaml-input="onYamlInput"
        @toggle-edit="(m) => moduleEditMode[m] = !moduleEditMode[m]"
      />

      <USeparator />

      <ModuleTable
        v-model:row-selection="rowSelection"
        :table-rows="tableRows"
        :is-loading-infos="moduleStore.isLoadingInfos"
        :selected-count="selectedModules.length"
        @select="onTableSelect"
      />

      <OrchestrationFooter
        v-model:reprocess-file="reprocessFile"
        :is-submitting="isSubmitting"
        @run="handleSubmit"
      />

    </div>
  </UPage>
</template>