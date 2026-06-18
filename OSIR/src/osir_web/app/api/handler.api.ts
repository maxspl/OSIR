import type { OsirClient } from './client'
import type {
  GetHandlerStatusResponse,
  PostHandlerCreateRequest,
  PostHandlerCreateResponse,
  PostHandlerAdvancedCreateRequest,
  GetHandlerTaskInfoResponse,
  GetHandlerTasksPaginatedResponse,
  GetHandlerStatsResponse,
  PostHandlerDeleteResponse,
} from './types'

export class HandlerApi {
  constructor(private client: OsirClient) {}

  status(handlerId: string): Promise<GetHandlerStatusResponse> {
    return this.client.post(`/api/handler/${handlerId}/info`)
  }

  create(body: PostHandlerCreateRequest): Promise<PostHandlerCreateResponse> {
    return this.client.post('/api/handler/create', body)
  }

  advanced(body: PostHandlerAdvancedCreateRequest): Promise<PostHandlerCreateResponse> {
    return this.client.post('/api/handler/advanced', body)
  }

  get_tasks_logs(handlerId: string): Promise<GetHandlerTaskInfoResponse> {
    return this.client.post(`/api/handler/${handlerId}/task_info`)
  }

  get_tasks(
    handlerId: string,
    page: number = 1,
    pageSize: number = 20,
    status?: string | null,
    module?: string | null
  ): Promise<GetHandlerTasksPaginatedResponse> {
    const params: Record<string, unknown> = { page, page_size: pageSize }
    if (status) {
      params.status = status
    }
    if (module) {
      params.module = module
    }
    return this.client.get(`/api/handler/${handlerId}/tasks`, params)
  }

  delete(handlerUuid: string): Promise<PostHandlerDeleteResponse> {
    return this.client.post('/api/handler/delete', { handler_uuid: handlerUuid })
  }

  stats(handlerId: string): Promise<GetHandlerStatsResponse> {
    return this.client.post(`/api/handler/${handlerId}/stats`)
  }

}
