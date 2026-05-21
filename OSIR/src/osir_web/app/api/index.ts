import { OsirClient } from './client'
import { ProfileApi } from './profile.api'
import { CaseApi } from './case.api'
import { FilesApi } from './files.api'
import { TasksApi } from './tasks.api'
import { HandlerApi } from './handler.api'
import { ModuleApi } from './module.api'
import { SystemApi } from './system.api'

export * from './types'
export { OsirClient, ProfileApi, CaseApi, FilesApi, TasksApi, HandlerApi, ModuleApi, SystemApi }

export class OsirApi {
  readonly profile: ProfileApi
  readonly case: CaseApi
  readonly files: FilesApi
  readonly tasks: TasksApi
  readonly handler: HandlerApi
  readonly module: ModuleApi
  readonly system: SystemApi

  constructor(baseURL = 'http://localhost:8502') {
    const client = new OsirClient(baseURL)
    this.profile = new ProfileApi(client)
    this.case = new CaseApi(client)
    this.files = new FilesApi(client)
    this.tasks = new TasksApi(client)
    this.handler = new HandlerApi(client)
    this.module = new ModuleApi(client)
    this.system = new SystemApi(client)
  }
}

let _instance: OsirApi | null = null

export function useOsirApi(baseURL = 'http://localhost:8502'): OsirApi {
  if (!_instance) _instance = new OsirApi(baseURL)
  return _instance
}
