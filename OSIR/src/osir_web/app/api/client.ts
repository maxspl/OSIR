export class OsirClient {
  readonly baseURL: string

  constructor(baseURL = 'http://master-api:8502') {
    this.baseURL = baseURL
  }

  get<T>(path: string, params?: Record<string, unknown>): Promise<T> {
    return $fetch<T>(path, { baseURL: this.baseURL, params })
  }

  post<T>(path: string, body?: object | null): Promise<T> {
    return $fetch<T>(path, { baseURL: this.baseURL, method: 'POST', body: body as Record<string, unknown> })
  }

  postForm<T>(path: string, form: FormData): Promise<T> {
    return $fetch<T>(path, { baseURL: this.baseURL, method: 'POST', body: form })
  }
}
