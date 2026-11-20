import { type ClassValue, clsx } from 'clsx';
import { twMerge } from 'tailwind-merge';
import { formatDistanceToNow, format } from 'date-fns';
import type { IncidentSeverity, IncidentStatus, CameraStatus } from '@/types';

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

export function formatDate(date: string): string {
  return format(new Date(date), 'MMM d, yyyy HH:mm');
}

export function formatRelativeTime(date: string): string {
  return formatDistanceToNow(new Date(date), { addSuffix: true });
}

export function truncate(str: string, length: number): string {
  return str.length > length ? str.slice(0, length) + '...' : str;
}

export function formatLatency(ms: number): string {
  return ms >= 1000 ? `${(ms / 1000).toFixed(2)}s` : `${ms.toFixed(0)}ms`;
}

export function debounce<T extends (...args: unknown[]) => unknown>(
  fn: T,
  delay: number
): (...args: Parameters<T>) => void {
  let timer: ReturnType<typeof setTimeout>;
  return (...args) => {
    clearTimeout(timer);
    timer = setTimeout(() => fn(...args), delay);
  };
}

export const SEVERITY_COLORS: Record<IncidentSeverity, string> = {
  critical: '#EF4444',
  high: '#F97316',
  medium: '#F59E0B',
  low: '#10B981',
  informational: '#3B82F6',
};

export const SEVERITY_BADGE: Record<IncidentSeverity, string> = {
  critical: 'severity-critical',
  high: 'severity-high',
  medium: 'severity-medium',
  low: 'severity-low',
  informational: 'severity-informational',
};

export const STATUS_COLORS: Record<IncidentStatus, string> = {
  open: '#EF4444',
  acknowledged: '#F59E0B',
  investigating: '#3B82F6',
  resolved: '#10B981',
  false_positive: '#94A3B8',
};

export const CAMERA_STATUS_COLORS: Record<CameraStatus, string> = {
  online: '#10B981',
  offline: '#EF4444',
  processing: '#22D3EE',
  error: '#F97316',
};

export function getSeverityColor(s: IncidentSeverity): string {
  return SEVERITY_COLORS[s] ?? '#94A3B8';
}

export function getSeverityBadgeClass(s: IncidentSeverity): string {
  return SEVERITY_BADGE[s] ?? '';
}

export const STATUS_BADGE: Record<IncidentStatus, string> = {
  open: 'status-open',
  acknowledged: 'status-acknowledged',
  investigating: 'status-investigating',
  resolved: 'status-resolved',
  false_positive: 'status-false-positive',
};

export function getStatusBadgeClass(s: IncidentStatus): string {
  return STATUS_BADGE[s] ?? '';
}

export function getStatusColor(s: IncidentStatus): string {
  return STATUS_COLORS[s] ?? '#94A3B8';
}
