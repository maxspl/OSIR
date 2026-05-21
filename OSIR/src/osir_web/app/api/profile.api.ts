import type { OsirClient } from './client'
import type {
  GetProfileListResponse,
  GetProfileInfoResponse,
  PostProfileRunRequest,
  PostProfileRunResponse,
} from './types'

export class ProfileApi {
  constructor(private client: OsirClient) {}

  list(): Promise<GetProfileListResponse> {
    return this.client.get('/api/profile')
  }

  info(profileName: string): Promise<GetProfileInfoResponse> {
    return this.client.get(`/api/profile/${profileName}/info`)
  }

  run(profileName: string, body: PostProfileRunRequest): Promise<PostProfileRunResponse> {
    return this.client.post(`/api/profile/${profileName}/run`, body)
  }
}
