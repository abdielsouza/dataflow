const API_BASE_URL =
  (import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000")
  .replace(/\/$/, "");

const TOKEN_KEY = "dataflow_access_token";

export interface LoginRequest {
  email:    string;
  password: string;
}

export interface RegisterRequest {
  username: string;
  email:    string;
  password: string;
}

export interface TokenResponse {
  access_token:  string;
  token_type:    string;
}

export interface DatasetDefinition {
  name:   string;
  source: string;
}

export interface OperationDefinition {
  id:         string;
  type:       string;
  parameters: Record<string, unknown>;
}

export interface OperationEdge {
  source: string;
  target: string;
}

export interface AnalysisDefinition {
  name:       string;
  dataset:    DatasetDefinition;
  operations: OperationDefinition[];
  edges:      OperationEdge[];
}

export interface SavedAnalysis {
  id:         string;
  dataset_id:  string;
  name:       string;
  dataset:    DatasetDefinition;
  definition: AnalysisDefinition;
  created_at:  string;
  updated_at:  string;
}

export interface AnalysisListItem {
  id:         string;
  dataset_id:  string;
  name:       string;
  dataset:    DatasetDefinition;
  created_at:  string;
  updated_at:  string;
}

export interface AnalysisExecutionResponse {
  id: string;
  analysis_id: string;
  status: string;
  error?: string | null;
}

export class ApiError extends Error {
  readonly status: number;

  constructor(message: string, status: number) {
    super(message);
    this.name = "ApiError";
    this.status = status;
  }
}

export function getAccessToken(): string | null {
  if (typeof window === "undefined") return null;
  return localStorage.getItem(TOKEN_KEY);
}

export function setAccessToken(token: string): void {
  if (typeof window === "undefined") return;
  localStorage.setItem(TOKEN_KEY, token);
}

export function clearAccessToken(): void {
  if (typeof window === "undefined") return;
  localStorage.removeItem(TOKEN_KEY);
}

export async function apiRequest<T>(
  path: string,
  options: RequestInit = {},
): Promise<T> {
  const token = getAccessToken();
  const headers = new Headers(options.headers ?? {});

  if (!headers.has("Content-Type") && !(options.body instanceof FormData)) {
    headers.set("Content-Type", "application/json");
  }

  if (token) {
    headers.set("Authorization", `Bearer ${token}`);
  }

  const response = await fetch(`${API_BASE_URL}${path}`, {
    ...options,
    headers,
  });

  if (response.status === 401) {
    clearAccessToken();
  }

  if (!response.ok) {
    const body = await response.json().catch(() => null);

    const message =
      typeof body?.detail === "string"
        ? body.detail
        : `API request failed (${response.status})`;

    throw new ApiError(message, response.status);
  }

  if (response.status === 204 || response.headers.get("content-length") === "0") {
    return undefined as T;
  }

  return response.json() as Promise<T>;
}

export const api = {
  register(data: RegisterRequest) {
    return apiRequest<{id: string; username: string; email: string}>(
      "/auth/register",
      {
        method: "POST",
        body: JSON.stringify(data),
      },
    );
  },

  async login(data: LoginRequest) {
    const result = await apiRequest<TokenResponse>(
      "/auth/login",
      {
        method: "POST",
        body: JSON.stringify(data),
      },
    );

    setAccessToken(result.access_token);
    
    return result;
  },

  logout() {
    clearAccessToken();
  },

  listAnalyses() {
    return apiRequest<AnalysisListItem[]>("/analyses");
  },

  getAnalysis(id: string) {
    return apiRequest<SavedAnalysis>(`/analyses/${encodeURIComponent(id)}`);
  },

  createAnalysis(definition: AnalysisDefinition) {
    return apiRequest<SavedAnalysis>(
      "/analyses",
      {
        method: "POST",
        body: JSON.stringify(definition),
      },
    );
  },

  executeAnalysis(definition: AnalysisDefinition) {
    return apiRequest<AnalysisExecutionResponse>(
      "/executions",
      {
        method: "POST",
        body: JSON.stringify({ analysis: definition }),
      },
    );
  }
};