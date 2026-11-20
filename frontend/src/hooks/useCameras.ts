'use client';
import useSWR from 'swr';
import { camerasApi } from '@/lib/api';
import type { Camera } from '@/types';

export function useCameras() {
  const { data, error, isLoading, mutate } = useSWR<Camera[]>(
    'cameras',
    () => camerasApi.list().then((r) => r.data),
    { refreshInterval: 15000 }
  );

  return {
    cameras: data ?? [],
    total: data?.length ?? 0,
    isLoading,
    error,
    refresh: mutate,
  };
}
