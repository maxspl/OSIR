// ── Shared envelope ──────────────────────────────────────────────────────────

export interface OsirIpcResponse<T = Record<string, unknown> | unknown[] | null> {
  version: number
  status?: number | null
  message?: string | null
  response: T
}

export interface UnexpectedExceptionResponseCore { error: string }
export interface UnexpectedExceptionResponse extends OsirIpcResponse<UnexpectedExceptionResponseCore> {}

// ── Domain models ─────────────────────────────────────────────────────────────

export interface OsirDbCaseModel {
  case_uuid: string
  name: string
}

export type OsirDbStatusModel =
  | 'task_created'
  | 'processing_started'
  | 'processing_done'
  | 'processing_failed'

export interface OsirTaskTraceModel {
  logs: string[]
  start_time: string
  end_time: string
  function: string
  duration_seconds: number
}

export interface OsirDbTaskModel {
  task_id: string
  case_uuid: string
  agent: string
  module: string
  input: string
  output?: string | null
  processing_status?: OsirDbStatusModel
  timestamp: string
  trace?: OsirTaskTraceModel | null
}

export interface OsirDbHandlerModel {
  handler_id: string
  case_uuid: string
  modules: string[]
  task_id: string[]
  processing_status: string
  created_at?: string | null
  case_name?: string | null
}

// ── Profile ───────────────────────────────────────────────────────────────────

export interface OsirProfileModel {
  version?: number | null
  author?: string | null
  description?: string | null
  os?: string | null
  modules: string[]
  filename?: string | null
}

export interface GetProfileListResponse extends OsirIpcResponse<string[]> {}
export interface GetProfileInfoResponse extends OsirIpcResponse<OsirProfileModel | null> {}
export interface PostProfileRunRequest { case_name: string }
export interface PostProfileRunResponse extends OsirIpcResponse<OsirDbHandlerModel> {}

// ── Case ──────────────────────────────────────────────────────────────────────

export interface GetCaseListResponse extends OsirIpcResponse<OsirDbCaseModel[]> {}
export interface PostCaseCreateResponse extends OsirIpcResponse<OsirDbCaseModel> {}
export interface GetCaseHandlerResponse extends OsirIpcResponse<OsirDbHandlerModel[]> {}
export interface GetTasksListResponse extends OsirIpcResponse<OsirDbTaskModel[]> {}

// ── Task ──────────────────────────────────────────────────────────────────────

export interface GetTaskInfoResponse extends OsirIpcResponse<OsirDbTaskModel> {}

// ── Handler ───────────────────────────────────────────────────────────────────

export interface GetHandlerStatusResponse extends OsirIpcResponse<OsirDbHandlerModel> {}
export interface GetHandlerTaskInfoResponse extends OsirIpcResponse<OsirDbTaskModel[]> {}

// ── Module ────────────────────────────────────────────────────────────────────

export interface OsirMetadataModel {
  version: string
  author: string
  description: string
  os?: string | null
}

export interface OsirConfigurationModel {
  module: string
  type: 'pre-process' | 'process' | 'post-process' | 'post_parsing'
  disk_only: boolean
  no_multithread: boolean
  processor_type: ('internal' | 'external')[]
  processor_os: 'windows' | 'unix'
  alt_module?: string | null
}

export interface OsirInputModel {
  type: 'file' | 'dir'
  path?: string | null
  name?: string | null
  file?: string | null
  dir?: string | null
  paths?: string[] | null
  match?: string | null
}

export interface OsirOutputModel {
  type?: 'single_file' | 'None' | 'multiple_files' | null
  format?: string | null
  output_dir?: string | null
  output_file?: string | null
  output_prefix?: string | null
}

export interface OsirToolModel {
  path: string
  cmd: string
  source?: string | null
  version?: string | number | null
  license?: string | null
  env?: string[] | null
}

export interface OsirEndpointModel {
  patterns?: string[] | null
  default?: string | null
}

export interface Json2SplunkConfigModel {
  source: string
  sourcetype: string
  name_rex: string
  path_suffix?: string | null
  host_rex: string
  timestamp_path?: string[] | null
  timestamp_format: string
  artifact?: string | null
}

export interface Json2ElasticModel {}

export interface OsirConnectorModel {
  json2splunk?: Json2SplunkConfigModel[] | null
  elastic?: Json2ElasticModel[] | null
}

export interface OsirModuleModel {
  metadata: OsirMetadataModel
  configuration: OsirConfigurationModel
  optional?: Record<string, unknown> | null
  env?: string[] | null
  tool?: OsirToolModel | null
  input: OsirInputModel
  output: OsirOutputModel
  endpoint?: OsirEndpointModel | null
  connector?: OsirConnectorModel | null
  splunk?: Record<string, unknown> | null
  filename?: string | null
}

export interface GetModuleListResponse extends OsirIpcResponse<string[]> {}
export interface PostModuleInfoRequest { modules: string[]; keys?: string[] }
export interface GetModuleExistsResponse extends OsirIpcResponse<Record<string, Record<string, unknown>> | null> {}
export interface PostModuleRunRequest { module_name: string; case_name: string; input_path?: string | null }
export interface PostModuleRunResponse extends OsirIpcResponse<OsirDbHandlerModel> {}
export interface PostModuleRunOnFileResponse extends OsirIpcResponse<OsirDbTaskModel> {}

// ── File system ───────────────────────────────────────────────────────────────

export interface DirEntry {
  dir: string
  basename: string
  extension: string
  path: string
  storage: string
  type: 'file' | 'dir'
  visibility: string
  file_size?: number | null
  last_modified?: number | null
  mime_type?: string | null
  read_only?: boolean | null
  previewUrl?: string | null
}

export interface FsData {
  storages: string[]
  dirname: string
  files: DirEntry[]
  read_only: boolean
}

export interface FileOperationResult {
  files: DirEntry[]
  storages: string[]
  read_only: boolean
  dirname: string
}

export interface DeleteItem { path: string; type: 'file' | 'dir' }
export interface DeleteRequest { path: string; items: DeleteItem[] }
export interface DeleteResult extends FileOperationResult { deleted?: DirEntry[] | null }

export interface RenameRequest { path: string; item: string; name: string }

export interface TransferRequest { sources: string[]; destination: string; path: string }

export interface ArchiveItem { path: string; type: 'file' | 'dir' }
export interface ArchiveRequest { items: ArchiveItem[]; path: string; name: string }
export interface UnarchiveRequest { item: string; path: string }

export interface CreateItemRequest { path: string; name: string }
export interface SaveRequest { path: string; content: string }

export interface SearchResult { dirname: string; files: DirEntry[]; storages: string[] }

export interface SearchParams {
  path: string
  filter?: string | null
  deep?: boolean
  size?: 'all' | 'small' | 'medium' | 'large' | null
}

// ── Handler ─────────────────────────────────────────────────────────────────

export interface PostHandlerCreateRequest {
  case_name: string
  profile?: string | null
  profile_module_to_add?: string[] | null
  profile_module_to_remove?: string[] | null
  modules?: string[] | null
  reprocess?: boolean
  modified_modules?: OsirModuleModel[] | null
}

export interface PostHandlerCreateResponse extends OsirIpcResponse<OsirDbHandlerModel> {}

export interface PostHandlerAdvancedCreateRequest {
  files_modules?: string | null
  files_input?: string[] | null
  folders_modules?: string | null
  files_in_folder_modules?: string | null
  folders_input?: string[] | null
  endpoint_name?: string | null
  case_name?: string | null
}

export interface GetHandlerListResponse extends OsirIpcResponse<OsirDbHandlerModel[]> {}

export interface PostHandlerDeleteResponse extends OsirIpcResponse<OsirDbHandlerModel> {}
