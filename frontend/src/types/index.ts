export type UserRole = 'admin' | 'operator' | 'viewer';
export type IncidentSeverity = 'informational' | 'low' | 'medium' | 'high' | 'critical';
export type IncidentStatus = 'open' | 'acknowledged' | 'investigating' | 'resolved' | 'false_positive';
export type CameraStatus = 'online' | 'offline' | 'processing' | 'error';
export type CameraSourceType = 'rtsp' | 'file' | 'webcam' | 'usb';
export type RuleType = 'crowd_density' | 'restricted_zone' | 'vehicle_congestion' | 'access_lane' | 'custom';
export type ZoneType = 'crowd' | 'restricted' | 'vehicle' | 'access_lane' | 'custom';
export type BrokerType = 'redis' | 'kafka';

export interface User {
  id: string;
  username: string;
  email: string;
  role: UserRole;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface Camera {
  id: string;
  name: string;
  description?: string;
  source_type: CameraSourceType;
  location?: string;
  latitude?: number;
  longitude?: number;
  status: CameraStatus;
  processing_enabled: boolean;
  created_at: string;
  updated_at: string;
}

export interface Zone {
  id: string;
  camera_id: string;
  name: string;
  polygon_coordinates: [number, number][];
  zone_type: ZoneType;
  created_at: string;
}

export interface Incident {
  id: string;
  event_id: string;
  camera_id: string;
  zone_id?: string;
  title: string;
  description?: string;
  severity: IncidentSeverity;
  status: IncidentStatus;
  confidence: number;
  latitude?: number;
  longitude?: number;
  rule_id?: string;
  simulated: boolean;
  object_counts?: Record<string, number>;
  detected_classes?: string[];
  inference_latency_ms?: number;
  created_at: string;
  updated_at: string;
}

export interface IncidentAudit {
  id: string;
  incident_id: string;
  user_id: string;
  username?: string;
  previous_status: IncidentStatus | null;
  new_status: IncidentStatus;
  comment?: string;
  timestamp: string;
}

export interface Rule {
  id: string;
  camera_id: string;
  zone_id?: string;
  name: string;
  rule_type: RuleType;
  configuration: RuleConfiguration;
  severity: IncidentSeverity;
  is_enabled: boolean;
  created_at: string;
}

export interface RuleConfiguration {
  threshold: number;
  duration_seconds: number;
  cooldown_seconds: number;
  polygon_coordinates?: [number, number][];
}

export interface DetectionEvent {
  id: string;
  event_id: string;
  camera_id: string;
  event_type: string;
  object_counts: Record<string, number>;
  confidence: number;
  event_timestamp: string;
  simulated: boolean;
}

export interface AnalyticsSummary {
  total_cameras: number;
  active_cameras: number;
  total_incidents: number;
  open_incidents: number;
  critical_incidents: number;
  resolved_incidents: number;
  avg_inference_latency_ms: number;
  event_volume_24h: number;
}

export interface TrendPoint {
  date: string;
  total: number;
  critical: number;
  resolved: number;
}

export interface SeverityDistribution {
  severity: IncidentSeverity;
  count: number;
  percentage: number;
}

export interface CameraActivity {
  camera_id: string;
  camera_name: string;
  incident_count: number;
}

export interface SearchResult {
  incident: Incident;
  similarity_score: number;
  camera_name?: string;
}

export interface ComponentHealth {
  name: string;
  status: 'healthy' | 'degraded' | 'unhealthy';
  latency_ms?: number;
  message?: string;
  last_checked: string;
}

export interface SystemHealth {
  status: 'healthy' | 'degraded' | 'unhealthy';
  version: string;
  components: ComponentHealth[];
  uptime_seconds: number;
  active_ws_connections: number;
  queue_lag: number;
  dlq_count: number;
}

export interface WebSocketMessage {
  type: 'incident.new' | 'incident.updated' | 'camera.status' | 'system.metrics' | 'ping';
  data: unknown;
  timestamp: string;
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  page_size: number;
  pages: number;
}

export interface ApiError {
  detail: string;
  status_code: number;
}
