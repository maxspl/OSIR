import type { OsirClient } from './client'
import type {
  GetModuleListResponse,
  GetModuleExistsResponse,
  PostModuleInfoRequest,
} from './types'

export class ModuleApi {
  constructor(private client: OsirClient) {}

  list(): Promise<GetModuleListResponse> {
    return this.client.get('/api/module')
  }

  info(body: PostModuleInfoRequest): Promise<GetModuleExistsResponse> {
    return this.client.post('/api/module/info', body)
  }
}
