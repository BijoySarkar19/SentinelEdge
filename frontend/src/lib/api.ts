import axios, { AxiosInstance, AxiosError } from 'axios';
import type {
  Camera,
  Incident,
  PaginatedResponse,
  AnalyticsSummary,
  TrendPoint,
  SeverityDistribution,
  CameraActivity,
  SearchResult,
  SystemHealth,
  User,
} from '@/types';

const BASE_URL = process.env.NEXT_PUBLIC_API_URL ?? 'http://localhost:8000';

const api: AxiosInstance = axios.create({
  baseURL: `${BASE_URL}/api/v1`,
  withCredentials: true,
  headers: { 'Content-Type': 'application/json' },
  timeout: 30000,
});

api.interceptors.response.use(
  (res) => res,
  (error: AxiosError) => {
    if (error.response?.status === 401 && typeof window !== 'undefined') {
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// Auth
export const authApi = {
  login: (username: string, password: string) =>
    api.post('/auth/login', { username, password }),
  logout: () => api.post('/auth/logout'),
  me: () => api.get<User>('/auth/me'),
};

// Cameras
export const camerasApi = {
  list: (page = 1, pageSize = 20) =>
    api.get<PaginatedResponse<Camera>>('/cameras', {
      params: { page, page_size: pageSize },
    }),
  get: (id: string) => api.get<Camera>(`/cameras/${id}`),
  create: (data: Partial<Camera>) => api.post<Camera>('/cameras', data),
  update: (id: string, data: Partial<Camera>) =>
    api.patch<Camera>(`/cameras/${id}`, data),
  delete: (id: string) => api.delete(`/cameras/${id}`),
};

// Incidents
export const incidentsApi = {
  list: (params?: Record<string, unknown>) =>
    api.get<PaginatedResponse<Incident>>('/incidents', { params }),
  get: (id: string) => api.get<Incident>(`/incidents/${id}`),
  acknowledge: (id: string, comment?: string) =>
    api.post(`/incidents/${id}/acknowledge`, { comment }),
  resolve: (id: string, comment?: string) =>
    api.post(`/incidents/${id}/resolve`, { comment }),
  update: (id: string, data: Partial<Incident>) =>
    api.patch(`/incidents/${id}`, data),
};

// Analytics
export const analyticsApi = {
  summary: () => api.get<AnalyticsSummary>('/analytics/summary'),
  trends: (days = 7) =>
    api.get<TrendPoint[]>('/analytics/trends', { params: { days } }),
  severity: () => api.get<SeverityDistribution[]>('/analytics/severity'),
  cameras: () => api.get<CameraActivity[]>('/analytics/cameras'),
};

// Search
export const searchApi = {
  semantic: (query: string, filters?: Record<string, unknown>) =>
    api.post<{ results: SearchResult[]; latency_ms: number }>('/search/semantic', {
      query,
      filters,
    }),
};

// Health
export const healthApi = {
  health: () => api.get<{ status: string }>('/health'),
  ready: () => api.get<SystemHealth>('/health/ready'),
};

export default api;
