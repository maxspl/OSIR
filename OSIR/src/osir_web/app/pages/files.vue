<script setup lang="ts">
import { RemoteDriver } from 'vuefinder'
import { useOsirApi } from '~/api'
import { useCaseStore } from '~/stores/case'
import { useModuleStore } from '~/stores/module'
import { useProfileStore } from '~/stores/profile'
import { useHandlerStore } from '~/stores/handler'
import type { PostHandlerAdvancedCreateRequest } from '~/api/types'
import TreeSelector from '~/components/TreeSelector.vue'
import { buildTreeFromPaths } from '~/utils/tree'

useSeoMeta({ title: 'OSIR — Files' })

const selectedCase = ref('all')

// ── Stores & API ─────────────────────────────────────────────────────────────
const api = useOsirApi()
const caseStore = useCaseStore()
const moduleStore = useModuleStore()
const profileStore = useProfileStore()
const handlerStore = useHandlerStore()

onMounted(() => moduleStore.startPolling(50000))
onUnmounted(() => moduleStore.stopPolling())

const toast = useToast()

const { data: casesData } = await useAsyncData('cases', () => api.case.list())

const caseOptions = computed(() => [
  { label: 'All cases', value: 'all' },
  ...(casesData.value?.response ?? []).map(c => ({ label: c.name, value: c.name })),
])

// Fetch initial data
await Promise.all([
  caseStore.fetchCases(),
  moduleStore.fetchModules(),
  profileStore.fetchProfiles()
])
moduleStore.fetchModuleInfos()

const selectedExpanded = ref(false)

const fileAction = ref<string[]>([])
const folderAction = ref<string[]>([])
const folderAllFilesAction = ref<string[]>([])

const fileModules = computed(() =>
  moduleStore.modules.filter(m => moduleStore.moduleInfoMap[m]?.input?.type === 'file')
)

const dirModules = computed(() =>
  moduleStore.modules.filter(m => moduleStore.moduleInfoMap[m]?.input?.type === 'dir')
)

const fileModuleTree = computed<TreeItem[]>(() => buildTreeFromPaths(fileModules.value))
const dirModuleTree = computed<TreeItem[]>(() => buildTreeFromPaths(dirModules.value))

// Keep old options for compatibility if needed
const fileModuleOptions = computed(() =>
  fileModules.value.map(m => ({ label: m, value: m }))
)

const dirModuleOptions = computed(() =>
  dirModules.value.map(m => ({ label: m, value: m }))
)
const hostname = ref('UNKNOWN')

function getBasename(modulePath: string): string {
  return modulePath.split('/').pop() || modulePath
}

function extractVal(val: unknown): string {
  if (val === null || val === undefined) return 'all'
  if (typeof val === 'object' && 'value' in (val as object)) return (val as { value: string }).value
  return String(val)
}

// ── Handler creation ────────────────────────────────────────────────────────
async function handleRunOrchestration() {
  const files = selectedItems.value.filter(item => item.type === 'file').map(item => item.path)
  const folders = selectedItems.value.filter(item => item.type === 'dir').map(item => item.path)

  const request: PostHandlerAdvancedCreateRequest = {
    case_name: selectedCase.value !== 'all' ? selectedCase.value : null,
    files_modules: fileAction.value.length > 0 ? fileAction.value[0] : null,
    files_input: files.length > 0 ? files : null,
    folders_modules: folderAction.value.length > 0 ? folderAction.value[0] : null,
    files_in_folder_modules: folderAllFilesAction.value.length > 0 ? folderAllFilesAction.value[0] : null,
    folders_input: folders.length > 0 ? folders : null,
    endpoint_name: hostname.value !== 'UNKNOWN' ? hostname.value : null,
  }

  try {
    const handler = await handlerStore.createHandlerAdvanced(request)
    if (handler) {
      toast.add({
        title: 'Handler created',
        description: `Handler created successfully`,
        color: 'success',
        icon: 'i-lucide-check-circle',
        actions: [{
          label: 'View in Monitoring',
          onClick: async () => {
            await navigateTo(`/monitoring/orchestration?handler_id=${handler.handler_id}`)
          },
        }],
      })
    } else {
      toast.add({ title: 'Error', description: 'Failed to create handler', color: 'error' })
    }
  } catch (e) {
    toast.add({ title: 'Error', description: 'Failed to create handler', color: 'error' })
  }
}


const finderRef = ref()
const selectedItems = ref<{ type: 'file' | 'dir'; path: string; basename: string }[]>([])

// Update selected items when drawer opens or selection changes
function updateSelectedItems(selected: any[]) {
  selectedItems.value = selected
}

const driver = new RemoteDriver({
  baseURL: '/proxy/api/files',
  url: {
    list: '/',
    upload: '/upload',
    delete: '/delete',
    rename: '/rename',
    copy: '/copy',
    move: '/move',
    archive: '/archive',
    unarchive: '/unarchive',
    createFile: '/create-file',
    createFolder: '/create-folder',
    preview: '/preview',
    download: '/download',
    search: '/search',
    save: '/save',
  },
})

const finderConfig = computed(() => ({
  initialPath: selectedCase.value !== 'all' ? `${selectedCase.value}://` : 'ROOT/OSIR://',
  persist: false,
  showMenuBar: false,
}))

const handlePathChange = (path: string) => {
  const prefix = path?.split('://')[0]
  if (!prefix) return
  const caseName = prefix === 'ROOT/OSIR' ? 'all' : prefix
  if (selectedCase.value !== caseName) {
    selectedCase.value = caseName
  }
}
</script>

<template>
  <UPage>
    <div class="w-full max-w-screen-2xl mx-auto px-6 py-8 space-y-6">

      <!-- Header -->
      <div class="space-y-2">
        <UBadge
          label="File Explorer"
          color="primary"
          variant="subtle"
          size="sm"
          icon="i-lucide-folder-open"
        />
        <h1 class="text-2xl font-bold text-primary uppercase leading-tight font-syne">
          Files
        </h1>
        <p class="text-sm text-muted">
          Browse and manage case files.
        </p>
      </div>

      <USeparator />

      <!-- Case filter -->
      <div class="rounded-lg bg-(--ui-bg-elevated) border border-(--ui-border)">
        <div class="flex items-center gap-3 px-4 py-3">
          <UIcon name="i-lucide-folder-open" class="text-primary w-4 h-4 shrink-0" />
          <span class="text-sm font-semibold text-muted tracking-wide uppercase">Case</span>
          <USelectMenu
            :model-value="selectedCase"
            :items="caseOptions"
            value-key="value"
            label-key="label"
            placeholder="All cases…"
            size="xl"
            class="w-full"
            @update:model-value="selectedCase = extractVal($event)"
          />
          <Transition
            enter-active-class="transition duration-150 ease-out"
            enter-from-class="opacity-0 scale-90"
            enter-to-class="opacity-100 scale-100"
            leave-active-class="transition duration-100 ease-in"
            leave-from-class="opacity-100 scale-100"
            leave-to-class="opacity-0 scale-90"
          >
            <UButton
              v-if="selectedCase !== 'all'"
              icon="i-lucide-x"
              size="sm"
              variant="ghost"
              color="neutral"
              @click="selectedCase = 'all'"
            />
          </Transition>
        </div>
      </div>

      <!-- VueFinder -->
      <div class="rounded-lg border border-(--ui-border) overflow-hidden shadow-sm" style="height: 70vh; min-height: 500px;">
        <vue-finder
          ref="finderRef"
          :key="selectedCase"
          id="large-dataset-example"
          :driver="driver"
          :config="finderConfig"
          style="height: 100%;"
          @path-change="handlePathChange"
          @update:selected="updateSelectedItems"
          :features="{
            search: true,
            preview: false,
            rename: true,
            upload: true,
            delete: true,
            newfile: false,
            newfolder: true,
            download: true,
            edit: false,
            archive: true,
            unarchive: true,
            fullscreen: true,
            language: false,
            move: true,
            copy: true,
            history: false,
            theme: false,
            pinned: true
          }"
        >
          <template #status-bar="{ selected, count }">
            <UDrawer direction="right" :ui="{ content: 'w-[780px]' }" @open="updateSelectedItems(selected)">
              <UButton
                :disabled="count === 0"
                :label="`Orchestration of ${count} Selected`"
                color="neutral"
                variant="subtle"
                @click="updateSelectedItems(selected)"
              />

              <template #body>
                <div class="flex flex-col items-center gap-4 p-6 w-full">

                  <!-- Title -->
                  <div class="w-full">
                    <h2 class="text-lg font-bold text-primary uppercase leading-tight font-syne text-center">Run Module on Files & Folder</h2>
                  </div>
                  <USeparator class="w-full" />

                  <!-- Case encart -->
                  <div class="rounded-lg bg-(--ui-bg-elevated) border border-(--ui-border) w-full">
                    <div class="flex items-center justify-center gap-2 px-4 py-3">
                      <UIcon name="i-lucide-folder-open" class="text-primary w-4 h-4 shrink-0" />
                      <span class="text-xs font-semibold text-muted uppercase tracking-wide">Case</span>
                    </div>
                    <USeparator />
                    <div class="px-4 py-3 text-center">
                      <span class="text-sm font-medium">
                        {{ selectedCase === 'all' ? 'All cases' : selectedCase }}
                      </span>
                    </div>
                  </div>

                  <USeparator />

                  <!-- Selected Input encart -->
                  <div class="rounded-lg bg-(--ui-bg-elevated) border border-(--ui-border) w-full">
                    <div class="flex items-center justify-center gap-2 px-4 py-3">
                      <UIcon name="i-lucide-list-checks" class="text-primary w-4 h-4 shrink-0" />
                      <span class="text-xs font-semibold text-muted uppercase tracking-wide">Selected Input</span>
                    </div>
                    <USeparator />
                    <div class="px-4 py-3">
                      <p v-if="count === 0" class="text-xs text-muted text-center italic">No files selected</p>
                      <div class="grid grid-cols-2 gap-x-4 gap-y-1">
                        <div
                          v-for="item in (selectedExpanded ? selected : selected.slice(0, 12))"
                          :key="item.path"
                          class="flex items-center gap-2 text-xs text-default truncate"
                        >
                          <UIcon
                            :name="item.type === 'dir' ? 'i-lucide-folder' : 'i-lucide-file'"
                            class="w-3.5 h-3.5 shrink-0 text-muted"
                          />
                          <span class="truncate">{{ item.basename }}</span>
                        </div>
                      </div>
                      <button
                        v-if="selected.length > 12"
                        class="flex items-center justify-center gap-1 mt-2 w-full text-xs text-muted hover:text-primary transition-colors"
                        @click="selectedExpanded = !selectedExpanded"
                      >
                        <UIcon
                          :name="selectedExpanded ? 'i-lucide-chevron-up' : 'i-lucide-chevron-down'"
                          class="w-3.5 h-3.5"
                        />
                        <span>{{ selectedExpanded ? 'Show less' : `+${selected.length - 12} more` }}</span>
                      </button>
                    </div>
                  </div>

                  <USeparator />

                  <!-- Hostname encart -->
                  <div class="rounded-lg bg-(--ui-bg-elevated) border border-(--ui-border) w-full">
                    <div class="flex items-center justify-center gap-2 px-4 py-3">
                      <UIcon name="i-lucide-monitor" class="text-primary w-4 h-4 shrink-0" />
                      <span class="text-xs font-semibold text-muted uppercase tracking-wide">Hostname</span>
                    </div>
                    <USeparator />
                    <div class="flex items-center gap-3 px-4 py-3">
                      <span class="text-sm font-medium text-muted shrink-0 w-32">Default Name</span>
                      <UInput
                        v-model="hostname"
                        placeholder="UNKNOWN"
                        size="xl"
                        class="w-full"
                      />
                    </div>
                  </div>

                  <USeparator />

                  <!-- Action On File encart -->
                  <div class="rounded-lg bg-(--ui-bg-elevated) border border-(--ui-border) w-full">
                    <div class="flex items-center justify-center gap-2 px-4 py-3">
                      <UIcon name="i-lucide-file" class="text-primary w-4 h-4 shrink-0" />
                      <span class="text-xs font-semibold text-muted uppercase tracking-wide">Action On File</span>
                    </div>
                    <USeparator />
                    <div class="flex items-center gap-3 px-4 py-3">
                      <span class="text-sm font-medium text-muted shrink-0 w-32">Run on files</span>
                      <TreeSelector
                        v-model="fileAction"
                        :items="fileModuleTree"
                        placeholder="Module…"
                        size="xl"
                        class="w-full"
                        :loading="moduleStore.isLoading"
                      />
                    </div>
                  </div>

                  <USeparator />

                  <!-- Action On Folder encart -->
                  <div class="rounded-lg bg-(--ui-bg-elevated) border border-(--ui-border) w-full">
                    <div class="flex items-center justify-center gap-2 px-4 py-3">
                      <UIcon name="i-lucide-folder" class="text-primary w-4 h-4 shrink-0" />
                      <span class="text-xs font-semibold text-muted uppercase tracking-wide">Action On Folder</span>
                    </div>
                    <USeparator />
                    <div class="flex flex-col gap-3 px-4 py-3">
                      <div class="flex items-center gap-3">
                        <span class="text-sm font-medium text-muted shrink-0 w-32">Only on Folder</span>
                        <TreeSelector
                          v-model="folderAction"
                          :items="dirModuleTree"
                          placeholder="Module…"
                          size="xl"
                          class="w-full"
                          :loading="moduleStore.isLoading"
                        />
                      </div>
                      <div class="flex items-center gap-3">
                        <span class="text-sm font-medium text-muted shrink-0 w-32">All files in folder</span>
                        <TreeSelector
                          v-model="folderAllFilesAction"
                          :items="fileModuleTree"
                          placeholder="Module…"
                          size="xl"
                          class="w-full"
                          :loading="moduleStore.isLoading"
                        />
                      </div>
                    </div>
                  </div>

                  <div class="flex justify-center w-full">
                    <UButton
                      label="Run Orchestration"
                      icon="i-lucide-play"
                      size="xl"
                      :disabled="selectedItems.length === 0 || (fileAction.length === 0 && folderAction.length === 0 && folderAllFilesAction.length === 0)"
                      :loading="handlerStore.isLoading"
                      @click="handleRunOrchestration"
                    />
                  </div>
                </div>
              </template>
            </UDrawer>
          </template>
        </vue-finder>
      </div>

    </div>
  </UPage>
</template>
