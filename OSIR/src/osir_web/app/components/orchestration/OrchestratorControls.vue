<script setup lang="ts">
import { useCaseStore } from '~/stores/case'

interface Option {
  label: string
  value: string
}

const props = defineProps<{
  profileOptions: Option[]
  moduleOptions: Option[]
  nonProfileModuleOptions: Option[]
  inProfileModuleOptions: Option[]
}>()

const caseStore = useCaseStore()

const selectedCase = defineModel<string | undefined>('selectedCase')
const selectedProfile = defineModel<string | null>('selectedProfile')
const selectedModules = defineModel<string[]>('selectedModules')
const modulesToAdd = defineModel<string[]>('modulesToAdd')
const modulesToRemove = defineModel<string[]>('modulesToRemove')

function getBasename(modulePath: string): string {
  return modulePath.split('/').pop() || modulePath
}

function onModulesUpdate(val: string[]) {
  selectedModules.value = val
  emit('select-by-path', val)
}

const emit = defineEmits<{
  'select-by-path': [paths: string[]]
}>()
</script>

<template>
  <div class="space-y-4">

    <!-- Case -->
    <div class="rounded-lg bg-(--ui-bg-elevated) border border-(--ui-border)">
      <div class="flex items-center gap-4 px-4 py-3">
        <div class="flex items-center gap-2 shrink-0">
          <UIcon name="i-lucide-folder-open" class="text-primary w-4 h-4 shrink-0" />
          <span class="text-sm font-semibold text-muted tracking-wide uppercase">Case</span>
        </div>
        <USelectMenu
          v-model="selectedCase"
          :items="caseStore.caseOptions"
          value-key="value"
          label-key="label"
          placeholder="Select a case…"
          size="xl"
          class="w-full"
          :loading="caseStore.isLoading"
        />
      </div>
    </div>

    <USeparator />
    
    <!-- Profile -->
    <div class="rounded-lg bg-(--ui-bg-elevated) border border-(--ui-border)">
      <div class="flex items-center gap-4 px-4 py-3">
        <div class="flex items-center gap-2 shrink-0">
          <UIcon name="i-lucide-workflow" class="text-primary w-4 h-4 shrink-0" />
          <span class="text-sm font-semibold text-muted tracking-wide uppercase">Profile</span>
        </div>
        <USelectMenu
          v-model="selectedProfile"
          :items="profileOptions"
          value-key="value"
          label-key="label"
          placeholder="Select a profile…"
          size="xl"
          class="w-full"
          clear
          clear-icon="i-lucide-trash"
        />
      </div>
    </div>

    <!-- Modules (no profile) -->
    <Transition
      enter-active-class="transition duration-200 ease-out"
      enter-from-class="opacity-0 -translate-y-1"
      enter-to-class="opacity-100 translate-y-0"
      leave-active-class="transition duration-150 ease-in pointer-events-none"
      leave-from-class="opacity-100 translate-y-0"
      leave-to-class="opacity-0 -translate-y-1"
    >
      <div v-if="!selectedProfile" class="rounded-lg bg-(--ui-bg-elevated) border border-(--ui-border)">
        <div class="flex items-center gap-4 px-4 py-3">
          <div class="flex items-center gap-2 shrink-0">
            <UIcon name="i-lucide-list-checks" class="text-primary w-4 h-4 shrink-0" />
            <span class="text-sm font-semibold text-muted tracking-wide uppercase">Modules</span>
          </div>
          <USelectMenu
            :model-value="selectedModules"
            :items="moduleOptions"
            value-key="value"
            label-key="label"
            multiple
            placeholder="Select modules…"
            size="xl"
            class="w-full"
            @update:model-value="onModulesUpdate"
          >
            <template #default="{ modelValue }">
              <div v-if="modelValue?.length" class="flex items-center gap-1 flex-wrap">
                <UBadge
                  v-for="v in (modelValue as string[]).slice(0, 5)"
                  :key="v"
                  :label="getBasename(v)"
                  color="primary"
                  variant="solid"
                  size="md"
                  class="rounded-full"
                />
                <UBadge
                  v-if="(modelValue as string[]).length > 5"
                  :label="`+${(modelValue as string[]).length - 5}`"
                  color="primary"
                  variant="subtle"
                  size="md"
                  class="rounded-full"
                />
              </div>
            </template>
          </USelectMenu>
        </div>
      </div>
    </Transition>

    <!-- Add / Remove (with profile) -->
    <Transition
      enter-active-class="transition duration-200 ease-out"
      enter-from-class="opacity-0 -translate-y-1"
      enter-to-class="opacity-100 translate-y-0"
      leave-active-class="transition duration-150 ease-in pointer-events-none"
      leave-from-class="opacity-100 translate-y-0"
      leave-to-class="opacity-0 -translate-y-1"
    >
      <div v-if="selectedProfile" class="space-y-4">

        <!-- Add modules not in profile -->
        <div class="rounded-lg border border-(--ui-border) bg-(--ui-bg-elevated)">
          <div class="flex items-center gap-4 px-4 py-3">
            <div class="flex items-center gap-2 shrink-0">
              <UIcon name="i-lucide-plus" class="text-primary w-4 h-4 shrink-0" />
              <span class="text-sm font-semibold text-muted uppercase tracking-wide">Add Modules Not In Profile</span>
            </div>
            <USelectMenu
              v-model="modulesToAdd"
              :items="nonProfileModuleOptions"
              value-key="value"
              label-key="label"
              multiple
              placeholder="Select modules to add…"
              size="lg"
              class="w-full"
            >
              <template #default="{ modelValue }">
                <div v-if="modelValue?.length" class="flex items-center gap-1 flex-wrap">
                  <UBadge
                    v-for="v in (modelValue as string[]).slice(0, 5)"
                    :key="v"
                    :label="getBasename(v)"
                    color="primary"
                    variant="solid"
                    size="md"
                    class="rounded-full"
                  />
                  <UBadge
                    v-if="(modelValue as string[]).length > 5"
                    :label="`+${(modelValue as string[]).length - 5}`"
                    color="primary"
                    variant="subtle"
                    size="md"
                    class="rounded-full"
                  />
                </div>
                <span v-else class="text-muted truncate">Select modules to add…</span>
              </template>
            </USelectMenu>
          </div>
        </div>

        <!-- Remove modules in profile -->
        <div class="rounded-lg border border-(--ui-border) bg-(--ui-bg-elevated)">
          <div class="flex items-center gap-4 px-4 py-3">
            <div class="flex items-center gap-2 shrink-0">
              <UIcon name="i-lucide-minus" class="text-error w-4 h-4 shrink-0" />
              <span class="text-sm font-semibold text-muted uppercase tracking-wide">Remove Modules In Profile</span>
            </div>
            <USelectMenu
              v-model="modulesToRemove"
              :items="inProfileModuleOptions"
              value-key="value"
              label-key="label"
              multiple
              placeholder="Select modules to remove…"
              size="lg"
              class="w-full"
            >
              <template #default="{ modelValue }">
                <div v-if="modelValue?.length" class="flex items-center gap-1 flex-wrap">
                  <UBadge
                    v-for="v in (modelValue as string[]).slice(0, 5)"
                    :key="v"
                    :label="getBasename(v)"
                    color="primary"
                    variant="solid"
                    size="md"
                    class="rounded-full"
                  />
                  <UBadge
                    v-if="(modelValue as string[]).length > 5"
                    :label="`+${(modelValue as string[]).length - 5}`"
                    color="primary"
                    variant="subtle"
                    size="md"
                    class="rounded-full"
                  />
                </div>
                <span v-else class="text-muted truncate">Select modules to remove…</span>
              </template>
            </USelectMenu>
          </div>
        </div>

      </div>
    </Transition>

  </div>
</template>
