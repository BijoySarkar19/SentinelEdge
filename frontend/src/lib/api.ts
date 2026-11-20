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
  Rule,
} from '@/types';

const BASE_URL = process.env.NEXT_PUBLIC_API_URL ?? 'http://localhost:8000';

const api: AxiosInstance = axios.create({
  baseURL: `${BASE_URL}/api/v1`,
  withCredentials: true,
  headers: { 'Content-Type': 'application/json' },
  timeout: 30000,
});

// Interceptors
api.interceptors.request.use((config) => {
  if (typeof window !== 'undefined') {
    const token = localStorage.getItem('sentinel_token');
    if (token && config.headers) {
      config.headers.Authorization = `Bearer ${token}`;
    }
  }
  return config;
});

api.interceptors.response.use(
  (res) => res,
  (error: AxiosError) => {
    if (error.response?.status === 401 && typeof window !== 'undefined') {
      localStorage.removeItem('sentinel_token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// Auth
export const authApi = {
  login: async (username: string, password: string) => {
    const res = await api.post('/auth/login', { username, password });
    if (res.data?.access_token && typeof window !== 'undefined') {
      localStorage.setItem('sentinel_token', res.data.access_token);
    }
    return res;
  },
  logout: async () => {
    try {
      await api.post('/auth/logout');
    } finally {
      if (typeof window !== 'undefined') {
        localStorage.removeItem('sentinel_token');
      }
    }
  },
  me: () => api.get<User>('/auth/me'),
};

// Cameras
export const camerasApi = {
  list: (skip = 0, limit = 100) =>
    api.get<Camera[]>('/cameras', {
      params: { skip, limit },
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
    api.post<Incident>(`/incidents/${id}/acknowledge`, { comment }),
  resolve: (id: string, comment?: string) =>
    api.post<Incident>(`/incidents/${id}/resolve`, { comment }),
  update: (id: string, data: Partial<Incident> & { comment?: string }) =>
    api.patch<Incident>(`/incidents/${id}`, data),
  ingest: (eventData: Record<string, unknown>) =>
    api.post<Incident>('/incidents/ingest', eventData),
};

// Rules
export const rulesApi = {
  list: (cameraId?: string) =>
    api.get<Rule[]>('/rules', { params: cameraId ? { camera_id: cameraId } : {} }),
  create: (data: Partial<Rule>) => api.post<Rule>('/rules', data),
  update: (id: string, data: Partial<Rule>) => api.patch<Rule>(`/rules/${id}`, data),
  delete: (id: string) => api.delete(`/rules/${id}`),
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
    api.post<{ results: SearchResult[]; search_latency_ms: number; latency_ms?: number }>('/search/semantic', {
      query,
      ...filters,
    }),
};

// Health
export const healthApi = {
  health: () => api.get<{ status: string }>('/health'),
  ready: () => api.get<SystemHealth>('/health/ready'),
};

export default api;
