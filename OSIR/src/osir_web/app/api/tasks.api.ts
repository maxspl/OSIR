import type { OsirClient } from './client'
import type { GetTaskInfoResponse } from './types'

export class TasksApi {
  constructor(private client: OsirClient) {}

  info(taskId: string): Promise<GetTaskInfoResponse> {
    return this.client.get(`/api/tasks/${taskId}/info`)
  }
}
