import { useHandlerStore } from '~/stores/handler'
import type { PostHandlerCreateRequest } from '~/api/types'

export function useOrchestrationSubmit(
  selectedCase: Ref<string | undefined>,
  selectedProfile: Ref<string | null>,
  selectedModules: Ref<string[]>,
  modulesToAdd: Ref<string[]>,
  modulesToRemove: Ref<string[]>,
  reprocessFile: Ref<boolean>,
  getModifiedModules: () => any[] | null,
) {
  const handlerStore = useHandlerStore()
  const toast = useToast()
  const isSubmitting = ref(false)

  async function handleSubmit() {
    if (!selectedCase.value) {
      toast.add({ title: 'Error', description: 'Please select a case', color: 'error' })
      return
    }
    if (isSubmitting.value) return
    isSubmitting.value = true

    const request: PostHandlerCreateRequest = {
      case_name: selectedCase.value,
      profile: selectedProfile.value ?? null,
      profile_module_to_add: modulesToAdd.value.length > 0 ? modulesToAdd.value : null,
      profile_module_to_remove: modulesToRemove.value.length > 0 ? modulesToRemove.value : null,
      modules: selectedModules.value.length > 0 ? selectedModules.value : null,
      modified_modules: getModifiedModules(),
      reprocess: reprocessFile.value,
    }

    try {
      const handler = await handlerStore.createHandler(request)
      if (handler) {
        toast.add({
          title: 'Handler created',
          description: `Handler ${handler.handler_id} created successfully`,
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
    } catch {
      toast.add({ title: 'Error', description: 'Failed to create handler', color: 'error' })
    } finally {
      isSubmitting.value = false
    }
  }

  return { isSubmitting, handleSubmit }
}
