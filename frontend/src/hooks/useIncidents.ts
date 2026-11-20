'use client';
import useSWR from 'swr';
import { incidentsApi } from '@/lib/api';
import type { PaginatedResponse, Incident } from '@/types';

interface UseIncidentsParams {
  page?: number;
  page_size?: number;
  severity?: string;
  status?: string;
  camera_id?: string;
  date_from?: string;
  date_to?: string;
}

export function useIncidents(params: UseIncidentsParams = {}) {
  const key = JSON.stringify({ endpoint: '/incidents', ...params });

  const { data, error, isLoading, mutate } = useSWR<PaginatedResponse<Incident>>(
    key,
    () =>
      incidentsApi
        .list(params as Record<string, unknown>)
        .then((r) => r.data),
    { refreshInterval: 30000 }
  );

  return {
    incidents: data?.items ?? [],
    total: data?.total ?? 0,
    pages: data?.pages ?? 0,
    isLoading,
    error,
    refresh: mutate,
  };
}
