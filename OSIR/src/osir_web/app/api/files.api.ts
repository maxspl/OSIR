import type { OsirClient } from './client'
import type {
  FsData,
  DeleteRequest,
  DeleteResult,
  RenameRequest,
  FileOperationResult,
  TransferRequest,
  ArchiveRequest,
  UnarchiveRequest,
  CreateItemRequest,
  SaveRequest,
  SearchResult,
  SearchParams,
} from './types'

export class FilesApi {
  constructor(private client: OsirClient) {}

  list(path: string): Promise<FsData> {
    return this.client.get('/api/files', { path })
  }

  upload(path: string, file: File): Promise<unknown> {
    const form = new FormData()
    form.append('path', path)
    form.append('file', file)
    return this.client.postForm('/api/files/upload', form)
  }

  delete(body: DeleteRequest): Promise<DeleteResult> {
    return this.client.post('/api/files/delete', body)
  }

  rename(body: RenameRequest): Promise<FileOperationResult> {
    return this.client.post('/api/files/rename', body)
  }

  copy(body: TransferRequest): Promise<FileOperationResult> {
    return this.client.post('/api/files/copy', body)
  }

  move(body: TransferRequest): Promise<FileOperationResult> {
    return this.client.post('/api/files/move', body)
  }

  archive(body: ArchiveRequest): Promise<FileOperationResult> {
    return this.client.post('/api/files/archive', body)
  }

  unarchive(body: UnarchiveRequest): Promise<FileOperationResult> {
    return this.client.post('/api/files/unarchive', body)
  }

  createFile(body: CreateItemRequest): Promise<FileOperationResult> {
    return this.client.post('/api/files/create-file', body)
  }

  createFolder(body: CreateItemRequest): Promise<FileOperationResult> {
    return this.client.post('/api/files/create-folder', body)
  }

  preview(path: string): Promise<unknown> {
    return this.client.get('/api/files/preview', { path })
  }

  download(path: string): Promise<unknown> {
    return this.client.get('/api/files/download', { path })
  }

  search(params: SearchParams): Promise<SearchResult> {
    return this.client.get('/api/files/search', params as unknown as Record<string, unknown>)
  }

  save(body: SaveRequest): Promise<unknown> {
    return this.client.post('/api/files/save', body)
  }
}
