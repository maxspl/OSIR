import type { OsirClient } from './client'
import type {
  GetCaseListResponse,
  PostCaseCreateResponse,
  GetCaseHandlerResponse,
  GetTasksListResponse,
} from './types'

export class CaseApi {
  constructor(private client: OsirClient) {}

  list(): Promise<GetCaseListResponse> {
    return this.client.get('/api/case')
  }

  create(caseName: string): Promise<PostCaseCreateResponse> {
    return this.client.post(`/api/case/${caseName}`)
  }

  handlers(caseName: string): Promise<GetCaseHandlerResponse> {
    return this.client.post(`/api/case/${caseName}/handler`)
  }

  tasks(caseName: string, page: number = 1, pageSize: number = 20): Promise<GetTasksListResponse> {
    return this.client.get(`/api/case/${caseName}/tasks`, { page, page_size: pageSize })
  }

  tasksAll(
    caseNames: string[] | null = null,
    status: string | null = null,
    input: string | null = null,
    page: number = 1,
    pageSize: number = 20
  ): Promise<GetTasksListResponse> {
    const params: Record<string, unknown> = { page, page_size: pageSize }
    if (caseNames && caseNames.length > 0) {
      params.case_names = caseNames.join(',')
    }
    if (status) {
      params.status = status
    }
    if (input) {
      params.input = input
    }
    return this.client.get('/api/tasks', params)
  }

  upload(caseName: string, file: File, chunkNumber = 0, totalChunks = 1): Promise<unknown> {
    const form = new FormData()
    form.append('file', file)
    form.append('name', file.name)
    form.append('chunk_number', String(chunkNumber))
    form.append('total_chunks', String(totalChunks))
    return this.client.postForm(`/api/case/${caseName}/uploads`, form)
  }
}
