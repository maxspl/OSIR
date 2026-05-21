import type { OsirClient } from './client'
import type {
  GetModuleListResponse,
  GetModuleExistsResponse,
  PostModuleInfoRequest,
  PostModuleRunRequest,
  PostModuleRunResponse,
  PostModuleRunOnFileResponse,
} from './types'

export class ModuleApi {
  constructor(private client: OsirClient) {}

  list(): Promise<GetModuleListResponse> {
    return this.client.get('/api/module')
  }

  info(body: PostModuleInfoRequest): Promise<GetModuleExistsResponse> {
    return this.client.post('/api/module/info', body)
  }

  run(body: PostModuleRunRequest): Promise<PostModuleRunResponse> {
    return this.client.post('/api/module/run', body)
  }

  runOnFile(body: PostModuleRunRequest): Promise<PostModuleRunOnFileResponse> {
    return this.client.post('/api/module/run_on_file', body)
  }
}
