import type { OsirClient } from './client'
import type { OsirIpcResponse } from './types'

export class SystemApi {
  constructor(private client: OsirClient) {}

  isActive(): Promise<OsirIpcResponse> {
    return this.client.get('/api/active')
  }

  version(): Promise<OsirIpcResponse> {
    return this.client.get('/api/version')
  }
}
