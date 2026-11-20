'use client';
import useSWR from 'swr';
import { camerasApi } from '@/lib/api';
import type { PaginatedResponse, Camera } from '@/types';

export function useCameras() {
  const { data, error, isLoading, mutate } = useSWR<PaginatedResponse<Camera>>(
    'cameras',
    () => camerasApi.list().then((r) => r.data),
    { refreshInterval: 15000 }
  );

  return {
    cameras: data?.items ?? [],
    total: data?.total ?? 0,
    isLoading,
    error,
    refresh: mutate,
  };
}
