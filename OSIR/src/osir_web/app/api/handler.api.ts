import type { OsirClient } from './client'
import type {
  GetHandlerStatusResponse,
  PostHandlerCreateRequest,
  PostHandlerCreateResponse,
  PostHandlerAdvancedCreateRequest,
  GetHandlerTaskInfoResponse,
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

  delete(handlerUuid: string): Promise<PostHandlerDeleteResponse> {
    return this.client.post('/api/handler/delete', { handler_uuid: handlerUuid })
  }

}
