const API_BASE = import.meta.env.VITE_API_BASE_URL ?? '/api/v1';

export type Project = {
  name: string;
  path: string;
  template: string;
  workflow: string;
  reports_count: number;
  database_id?: string | null;
};

export type Run = {
  status: string;
  project_name: string;
  run_id: string;
  workflow: string;
  profile: string;
  dry_run: boolean;
  command: string[];
  log_path: string;
  report_json_path: string;
  report_html_path: string;
  return_code?: number | null;
  database_id?: string | null;
  job_id?: string | null;
  created_at?: string | null;
  updated_at?: string | null;
};

export type ReportSummary = {
  project_name: string;
  run_id: string;
  status: string;
  workflow: string;
  started_at: string;
  json_path: string;
  html_path?: string | null;
};

export type ReportDetail = {
  project_name: string;
  run_id: string;
  metadata: Record<string, unknown>;
};

export type ExplainResponse = {
  status: string;
  project_name: string;
  run_id: string;
  provider: string;
  clinical_warning: string;
  explanation: string;
};

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE}${path}`, {
    headers: { 'Content-Type': 'application/json', ...(options?.headers ?? {}) },
    ...options
  });

  if (!response.ok) {
    const detail = await response.text();
    throw new Error(detail || `HTTP ${response.status}`);
  }

  if (response.status === 204) return undefined as T;
  return response.json() as Promise<T>;
}

export const api = {
  health: () => request<{ status: string }>('/health'),
  listProjects: () => request<Project[]>('/projects'),
  createProject: (payload: { name: string; template: string; force: boolean }) =>
    request<{ status: string; project: Project }>('/projects', {
      method: 'POST',
      body: JSON.stringify(payload)
    }),
  listRuns: (projectName?: string) => {
    const query = projectName ? `?project_name=${encodeURIComponent(projectName)}` : '';
    return request<Run[]>(`/runs${query}`);
  },
  createRun: (payload: { project_name: string; dry_run: boolean }) =>
    request<Run>('/runs', { method: 'POST', body: JSON.stringify(payload) }),
  listReports: (projectName?: string) => {
    const query = projectName ? `?project_name=${encodeURIComponent(projectName)}` : '';
    return request<ReportSummary[]>(`/reports${query}`);
  },
  getReport: (projectName: string, run: string) =>
    request<ReportDetail>(`/reports/${encodeURIComponent(projectName)}/${encodeURIComponent(run)}`),
  explain: (payload: { project_name: string; run: string; provider: string }) =>
    request<ExplainResponse>('/explain', { method: 'POST', body: JSON.stringify(payload) })
};
