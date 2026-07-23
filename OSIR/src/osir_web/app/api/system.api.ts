import type { OsirClient } from './client'
import type { OsirIpcResponse, GetSystemMetricsResponse } from './types'

export class SystemApi {
  constructor(private client: OsirClient) {}

  isActive(): Promise<OsirIpcResponse> {
    return this.client.get('/api/active')
  }

  version(): Promise<OsirIpcResponse> {
    return this.client.get('/api/version')
  }

  /** Recent host resource samples (RAM/CPU/load) per agent, for the graphs. */
  metrics(windowSeconds = 900): Promise<GetSystemMetricsResponse> {
    return this.client.get('/api/system/metrics', { window_seconds: windowSeconds })
  }
}
