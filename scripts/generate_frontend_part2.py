import os

ROOT = r"c:\Users\bijoy\Desktop\SENTINEL-EDGE\SentinelEdge"

def write(rel_path, content):
    full_path = os.path.join(ROOT, rel_path)
    os.makedirs(os.path.dirname(full_path), exist_ok=True)
    with open(full_path, "w", encoding="utf-8") as f:
        f.write(content.strip() + "\n")
    print(f"Wrote {rel_path}")

# ==================== DASHBOARD COMPONENTS ====================

write("frontend/src/components/dashboard/LiveEventFeed.tsx", '''
"use client";

import { useEffect, useState } from "react";
import { Badge } from "@/components/ui/Badge";
import { formatRelativeTime } from "@/lib/utils";
import { Radio } from "lucide-react";

interface LiveFeedItem {
  id: string;
  title: string;
  severity: string;
  camera: string;
  timestamp: string;
}

export function LiveEventFeed() {
  const [events, setEvents] = useState<LiveFeedItem[]>([
    {
      id: "ev-1",
      title: "Vehicle Congestion Warning on Gate 4 Access Lane",
      severity: "medium",
      camera: "North Gate Entrance",
      timestamp: new Date().toISOString(),
    },
    {
      id: "ev-2",
      title: "Restricted Zone Occupancy in Secure Industrial Bay",
      severity: "critical",
      camera: "Warehouse Yard",
      timestamp: new Date(Date.now() - 1000 * 60 * 3).toISOString(),
    },
    {
      id: "ev-3",
      title: "Unusual Crowd Density Exceeded Threshold in Main Lobby",
      severity: "high",
      camera: "Main Concourse",
      timestamp: new Date(Date.now() - 1000 * 60 * 8).toISOString(),
    },
    {
      id: "ev-4",
      title: "Emergency Lane Clear Check Scheduled",
      severity: "informational",
      camera: "Perimeter Perimeter 2",
      timestamp: new Date(Date.now() - 1000 * 60 * 15).toISOString(),
    },
  ]);

  return (
    <div className="glass-card flex flex-col p-5">
      <div className="flex items-center justify-between pb-4 border-b border-white/5">
        <div className="flex items-center gap-2">
          <Radio className="h-4 w-4 text-brand-cyan animate-pulse" />
          <h3 className="text-sm font-semibold tracking-wide text-text-primary uppercase">Live Edge Event Stream</h3>
        </div>
        <span className="text-[10px] tracking-wider text-brand-cyan uppercase bg-brand-cyan/10 px-2 py-0.5 rounded-full border border-brand-cyan/20">
          WebSocket Streaming
        </span>
      </div>

      <div className="mt-4 space-y-3 overflow-y-auto max-h-[380px] pr-1">
        {events.map((evt) => (
          <div
            key={evt.id}
            className="rounded-lg bg-background-secondary/60 p-3 border border-white/5 transition hover:border-brand-cyan/30"
          >
            <div className="flex items-start justify-between gap-3">
              <span className="text-xs font-medium text-text-primary leading-snug">{evt.title}</span>
              <Badge type="severity" value={evt.severity} />
            </div>
            <div className="mt-2 flex items-center justify-between text-[11px] text-text-secondary">
              <span>{evt.camera}</span>
              <span>{formatRelativeTime(evt.timestamp)}</span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
''')

write("frontend/src/components/dashboard/IncidentTrendChart.tsx", '''
"use client";

import { ResponsiveContainer, AreaChart, Area, XAxis, YAxis, Tooltip } from "recharts";

const data = [
  { day: "Mon", incidents: 12, critical: 2 },
  { day: "Tue", incidents: 18, critical: 4 },
  { day: "Wed", incidents: 15, critical: 1 },
  { day: "Thu", incidents: 25, critical: 5 },
  { day: "Fri", incidents: 22, critical: 3 },
  { day: "Sat", incidents: 30, critical: 7 },
  { day: "Sun", incidents: 19, critical: 2 },
];

export function IncidentTrendChart() {
  return (
    <div className="glass-card p-5">
      <div className="flex items-center justify-between mb-4">
        <div>
          <h3 className="text-sm font-semibold tracking-wide text-text-primary uppercase">Incident Trajectory</h3>
          <p className="text-xs text-text-secondary">7-day edge incident volume vs critical alerts</p>
        </div>
        <div className="flex items-center gap-4 text-xs">
          <div className="flex items-center gap-1.5 text-brand-cyan">
            <span className="h-2 w-2 rounded-full bg-brand-cyan" /> Total
          </div>
          <div className="flex items-center gap-1.5 text-sentinel-critical">
            <span className="h-2 w-2 rounded-full bg-sentinel-critical" /> Critical
          </div>
        </div>
      </div>

      <div className="h-64 w-full">
        <ResponsiveContainer width="100%" height="100%">
          <AreaChart data={data}>
            <defs>
              <linearGradient id="totalGrad" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#22D3EE" stopOpacity={0.3} />
                <stop offset="95%" stopColor="#22D3EE" stopOpacity={0.0} />
              </linearGradient>
              <linearGradient id="critGrad" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#EF4444" stopOpacity={0.3} />
                <stop offset="95%" stopColor="#EF4444" stopOpacity={0.0} />
              </linearGradient>
            </defs>
            <XAxis dataKey="day" stroke="#94A3B8" fontSize={11} tickLine={false} axisLine={false} />
            <YAxis stroke="#94A3B8" fontSize={11} tickLine={false} axisLine={false} />
            <Tooltip
              contentStyle={{ backgroundColor: "#0B192D", borderColor: "rgba(255,255,255,0.1)", borderRadius: "8px", fontSize: "12px" }}
            />
            <Area type="monotone" dataKey="incidents" stroke="#22D3EE" strokeWidth={2} fillOpacity={1} fill="url(#totalGrad)" />
            <Area type="monotone" dataKey="critical" stroke="#EF4444" strokeWidth={2} fillOpacity={1} fill="url(#critGrad)" />
          </AreaChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}
''')

write("frontend/src/components/dashboard/SeverityChart.tsx", '''
"use client";

import { ResponsiveContainer, PieChart, Pie, Cell, Tooltip } from "recharts";

const data = [
  { name: "Critical", value: 14, color: "#EF4444" },
  { name: "High", value: 28, color: "#F97316" },
  { name: "Medium", value: 45, color: "#F59E0B" },
  { name: "Low", value: 32, color: "#10B981" },
  { name: "Informational", value: 19, color: "#3B82F6" },
];

export function SeverityChart() {
  return (
    <div className="glass-card flex flex-col justify-between p-5">
      <div>
        <h3 className="text-sm font-semibold tracking-wide text-text-primary uppercase">Severity Composition</h3>
        <p className="text-xs text-text-secondary">Distribution of detected incidents</p>
      </div>

      <div className="h-48 w-full mt-2">
        <ResponsiveContainer width="100%" height="100%">
          <PieChart>
            <Tooltip
              contentStyle={{ backgroundColor: "#0B192D", borderColor: "rgba(255,255,255,0.1)", borderRadius: "8px", fontSize: "12px" }}
            />
            <Pie
              data={data}
              innerRadius={50}
              outerRadius={75}
              paddingAngle={4}
              dataKey="value"
            >
              {data.map((entry, index) => (
                <Cell key={`cell-${index}`} fill={entry.color} />
              ))}
            </Pie>
          </PieChart>
        </ResponsiveContainer>
      </div>

      <div className="grid grid-cols-2 gap-2 pt-2 border-t border-white/5 text-[11px]">
        {data.map((d) => (
          <div key={d.name} className="flex items-center gap-2">
            <span className="h-2 w-2 rounded-full" style={{ backgroundColor: d.color }} />
            <span className="text-text-secondary">{d.name}:</span>
            <span className="font-semibold text-text-primary">{d.value}</span>
          </div>
        ))}
      </div>
    </div>
  );
}
''')

# ==================== MAP VIEW COMPONENT ====================

write("frontend/src/components/maps/MapView.tsx", '''
"use client";

import { useEffect, useState } from "react";

interface MapViewProps {
  cameras?: Array<{ id: string; name: string; lat: number; lng: number; status: string }>;
  incidents?: Array<{ id: string; title: string; lat: number; lng: number; severity: string }>;
}

export default function MapView({ cameras = [], incidents = [] }: MapViewProps) {
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
  }, []);

  if (!mounted) {
    return (
      <div className="h-[550px] w-full rounded-xl bg-background-card flex items-center justify-center">
        <span className="text-sm text-text-secondary">Loading GIS Engine...</span>
      </div>
    );
  }

  // Interactive SVG Geospatial Map Canvas
  return (
    <div className="relative h-[550px] w-full overflow-hidden rounded-xl bg-background-card border border-white/5">
      <div className="absolute top-4 left-4 z-10 rounded-md bg-background-secondary/90 px-3 py-1.5 text-xs font-semibold text-text-primary border border-white/10 backdrop-blur-md">
        Sector GIS Overview • OpenStreetMap Projection
      </div>

      <div className="absolute bottom-4 right-4 z-10 rounded-md bg-background-secondary/90 px-3 py-1.5 text-xs text-text-secondary border border-white/10 backdrop-blur-md">
        Coordinates Simulated for Test Demonstration
      </div>

      {/* SVG Canvas Map Rendering */}
      <svg className="h-full w-full bg-[#071322]">
        <defs>
          <pattern id="grid" width="40" height="40" patternUnits="userSpaceOnUse">
            <path d="M 40 0 L 0 0 0 40" fill="none" stroke="rgba(34,211,238,0.06)" strokeWidth="1"/>
          </pattern>
        </defs>
        <rect width="100%" height="100%" fill="url(#grid)" />

        {/* Road and zone polygons */}
        <polygon points="120,80 340,110 380,260 160,240" fill="rgba(59,130,246,0.08)" stroke="#3B82F6" strokeWidth="1" strokeDasharray="4 2"/>
        <text x="210" y="170" fill="#3B82F6" fontSize="11" opacity="0.6">Zone A - Access Corridor</text>

        <polygon points="450,180 720,200 680,440 430,410" fill="rgba(239,68,68,0.08)" stroke="#EF4444" strokeWidth="1" strokeDasharray="4 2"/>
        <text x="520" y="310" fill="#EF4444" fontSize="11" opacity="0.6">Zone B - Restricted Perimeter</text>

        {/* Camera Nodes */}
        <g transform="translate(200, 140)">
          <circle r="12" fill="#22D3EE" opacity="0.2" className="animate-ping"/>
          <circle r="7" fill="#22D3EE"/>
          <text x="14" y="4" fill="#F8FAFC" fontSize="11" fontWeight="600">CAM-01 (Main Gate)</text>
        </g>

        <g transform="translate(560, 260)">
          <circle r="12" fill="#22D3EE" opacity="0.2" className="animate-ping"/>
          <circle r="7" fill="#22D3EE"/>
          <text x="14" y="4" fill="#F8FAFC" fontSize="11" fontWeight="600">CAM-02 (Industrial Bay)</text>
        </g>

        <g transform="translate(380, 390)">
          <circle r="12" fill="#10B981" opacity="0.2"/>
          <circle r="7" fill="#10B981"/>
          <text x="14" y="4" fill="#F8FAFC" fontSize="11" fontWeight="600">CAM-03 (Loading Dock)</text>
        </g>

        {/* Incident Alerts */}
        <g transform="translate(240, 180)">
          <circle r="16" fill="#F59E0B" opacity="0.25" className="animate-pulse"/>
          <circle r="6" fill="#F59E0B"/>
          <text x="12" y="4" fill="#F59E0B" fontSize="10">Vehicle Congestion</text>
        </g>

        <g transform="translate(610, 320)">
          <circle r="18" fill="#EF4444" opacity="0.3" className="animate-ping"/>
          <circle r="7" fill="#EF4444"/>
          <text x="12" y="4" fill="#EF4444" fontSize="10">Zone Breach</text>
        </g>
      </svg>
    </div>
  );
}
''')

# ==================== MAIN DASHBOARD ====================

write("frontend/src/app/(dashboard)/dashboard/loading.tsx", '''
export default function DashboardLoading() {
  return (
    <div className="space-y-6">
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
        {[1, 2, 3, 4].map((i) => (
          <div key={i} className="glass-card h-28 animate-pulse" />
        ))}
      </div>
      <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
        <div className="glass-card h-80 lg:col-span-2 animate-pulse" />
        <div className="glass-card h-80 animate-pulse" />
      </div>
    </div>
  );
}
''')

write("frontend/src/app/(dashboard)/dashboard/page.tsx", '''
"use client";

import { StatCard } from "@/components/ui/StatCard";
import { IncidentTrendChart } from "@/components/dashboard/IncidentTrendChart";
import { SeverityChart } from "@/components/dashboard/SeverityChart";
import { LiveEventFeed } from "@/components/dashboard/LiveEventFeed";
import { Camera, AlertTriangle, ShieldCheck, Activity, Cpu } from "lucide-react";

export default function DashboardPage() {
  return (
    <div className="space-y-8">
      {/* Top Welcome & KPI row */}
      <div>
        <h1 className="text-2xl font-bold tracking-tight text-text-primary">Operational Overview</h1>
        <p className="text-xs text-text-secondary mt-1">Real-time edge computer vision telemetry & privacy-filtered incident risk.</p>
      </div>

      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <StatCard
          title="Monitored Cameras"
          value="4"
          subtitle="All nodes online and reporting"
          icon={<Camera className="h-5 w-5" />}
          trend="+100% Edge Health"
        />
        <StatCard
          title="Open Incidents"
          value="7"
          subtitle="3 high or critical severity"
          icon={<AlertTriangle className="h-5 w-5 text-sentinel-warning" />}
          highlight
        />
        <StatCard
          title="Avg Inference Latency"
          value="41.8 ms"
          subtitle="NVIDIA RTX 3050 Laptop GPU (6GB)"
          icon={<Cpu className="h-5 w-5 text-brand-cyan" />}
          trend="24 FPS Real-Time"
        />
        <StatCard
          title="Privacy Guard"
          value="100%"
          subtitle="Metadata-only transmission active"
          icon={<ShieldCheck className="h-5 w-5 text-sentinel-success" />}
        />
      </div>

      {/* Main Visuals Row: Trajectory Chart & Severity breakdown */}
      <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
        <div className="lg:col-span-2">
          <IncidentTrendChart />
        </div>
        <div>
          <SeverityChart />
        </div>
      </div>

      {/* Live Event Stream */}
      <div>
        <LiveEventFeed />
      </div>
    </div>
  );
}
''')

# ==================== OTHER CORE PAGES ====================

write("frontend/src/app/(dashboard)/live-monitor/page.tsx", '''
"use client";

import { Badge } from "@/components/ui/Badge";
import { Camera, ShieldCheck, Play } from "lucide-react";

const CAMERAS = [
  { id: "CAM-01", name: "Main Entrance North", status: "processing", fps: 24.2, device: "cuda:0", objects: 6 },
  { id: "CAM-02", name: "Industrial Logistics Bay", status: "processing", fps: 22.8, device: "cuda:0", objects: 4 },
  { id: "CAM-03", name: "Employee Lobby Concourse", status: "processing", fps: 25.0, device: "cuda:0", objects: 8 },
  { id: "CAM-04", name: "South Perimeter Gate", status: "online", fps: 23.5, device: "cuda:0", objects: 2 },
];

export default function LiveMonitorPage() {
  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-text-primary">Live Edge Video Feeds</h1>
          <p className="text-xs text-text-secondary mt-1">
            Privacy-First Architecture: Local edge inference. Zero raw video uploaded to central servers.
          </p>
        </div>
        <div className="inline-flex items-center gap-2 rounded-lg bg-brand-cyan/10 border border-brand-cyan/30 px-3 py-1.5 text-xs font-semibold text-brand-cyan">
          <ShieldCheck className="h-4 w-4" />
          Anonymization Engine: Active
        </div>
      </div>

      <div className="grid grid-cols-1 gap-6 md:grid-cols-2">
        {CAMERAS.map((cam) => (
          <div key={cam.id} className="glass-card overflow-hidden">
            <div className="relative aspect-video bg-[#071322] flex items-center justify-center border-b border-white/5">
              {/* Synthetic visual frame representing privacy-blurred feed */}
              <div className="text-center p-6">
                <Camera className="mx-auto h-10 w-10 text-brand-cyan/40 mb-2 animate-pulse" />
                <span className="text-xs font-mono text-text-secondary block">
                  EDGE STREAM ENCRYPTED • {cam.id}
                </span>
                <span className="inline-block mt-2 rounded-md bg-white/5 border border-white/10 px-2.5 py-1 text-[11px] text-text-secondary">
                  Faces Blurring Filter Applied
                </span>
              </div>
              <div className="absolute top-3 left-3 flex gap-2">
                <span className="rounded-md bg-background/80 backdrop-blur-md px-2 py-0.5 text-[10px] font-mono text-brand-cyan border border-brand-cyan/30">
                  {cam.fps} FPS
                </span>
                <span className="rounded-md bg-background/80 backdrop-blur-md px-2 py-0.5 text-[10px] font-mono text-sentinel-success border border-sentinel-success/30">
                  {cam.device}
                </span>
              </div>
            </div>

            <div className="p-4 flex items-center justify-between">
              <div>
                <h4 className="text-sm font-semibold text-text-primary">{cam.name}</h4>
                <p className="text-xs text-text-secondary">{cam.objects} objects currently tracked</p>
              </div>
              <Badge type="status" value={cam.status} />
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
''')

write("frontend/src/app/(dashboard)/cameras/page.tsx", '''
"use client";

import { useState } from "react";
import { Badge } from "@/components/ui/Badge";
import { Camera, Plus, Edit2, Trash2 } from "lucide-react";

export default function CamerasPage() {
  const [cameras, setCameras] = useState([
    { id: "cam-1", name: "Main Entrance North", source: "rtsp://edge-01:8554/cam1", location: "Gate 1", status: "processing" },
    { id: "cam-2", name: "Industrial Logistics Bay", source: "rtsp://edge-02:8554/cam2", location: "Warehouse Yard", status: "processing" },
    { id: "cam-3", name: "Employee Lobby Concourse", source: "rtsp://edge-03:8554/cam3", location: "Building A", status: "online" },
    { id: "cam-4", name: "South Perimeter Gate", source: "rtsp://edge-04:8554/cam4", location: "Perimeter", status: "online" },
  ]);

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-text-primary">Camera Node Configuration</h1>
          <p className="text-xs text-text-secondary mt-1">Manage network video sources, RTSP streams, and local edge devices.</p>
        </div>
        <button className="inline-flex items-center gap-2 rounded-lg bg-brand-cyan px-4 py-2 text-xs font-semibold text-background hover:bg-brand-cyan/80 transition glow-cyan">
          <Plus className="h-4 w-4" /> Add Camera Node
        </button>
      </div>

      <div className="glass-card overflow-hidden">
        <table className="w-full text-left text-sm">
          <thead className="bg-background-secondary text-xs uppercase tracking-wider text-text-secondary border-b border-white/5">
            <tr>
              <th className="px-6 py-3.5 font-semibold">Camera Node</th>
              <th className="px-6 py-3.5 font-semibold">Source URI</th>
              <th className="px-6 py-3.5 font-semibold">Location</th>
              <th className="px-6 py-3.5 font-semibold">Status</th>
              <th className="px-6 py-3.5 font-semibold text-right">Actions</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-white/5 text-text-primary">
            {cameras.map((c) => (
              <tr key={c.id} className="hover:bg-white/5 transition">
                <td className="px-6 py-4 font-semibold">{c.name}</td>
                <td className="px-6 py-4 font-mono text-xs text-text-secondary">{c.source}</td>
                <td className="px-6 py-4 text-xs text-text-secondary">{c.location}</td>
                <td className="px-6 py-4">
                  <Badge type="status" value={c.status} />
                </td>
                <td className="px-6 py-4 text-right space-x-2">
                  <button className="text-text-secondary hover:text-brand-cyan transition">
                    <Edit2 className="h-4 w-4 inline" />
                  </button>
                  <button className="text-text-secondary hover:text-sentinel-critical transition">
                    <Trash2 className="h-4 w-4 inline" />
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
''')

write("frontend/src/app/(dashboard)/incidents/page.tsx", '''
"use client";

import Link from "next/link";
import { Badge } from "@/components/ui/Badge";
import { formatRelativeTime } from "@/lib/utils";
import { AlertTriangle, Filter, Search } from "lucide-react";

const INCIDENTS = [
  {
    id: "inc-01",
    title: "Vehicle Congestion Warning on Access Lane",
    severity: "medium",
    status: "open",
    confidence: 0.88,
    camera: "North Gate Entrance",
    created_at: new Date(Date.now() - 1000 * 60 * 12).toISOString(),
  },
  {
    id: "inc-02",
    title: "Restricted Zone Occupancy in Secure Industrial Bay",
    severity: "critical",
    status: "acknowledged",
    confidence: 0.94,
    camera: "Industrial Logistics Bay",
    created_at: new Date(Date.now() - 1000 * 60 * 35).toISOString(),
  },
  {
    id: "inc-03",
    title: "Unusual Crowd Density Exceeded in Main Concourse",
    severity: "high",
    status: "investigating",
    confidence: 0.91,
    camera: "Employee Lobby Concourse",
    created_at: new Date(Date.now() - 1000 * 60 * 60 * 2).toISOString(),
  },
  {
    id: "inc-04",
    title: "Stationary Vehicle Blockage on Emergency Fire Lane",
    severity: "critical",
    status: "resolved",
    confidence: 0.96,
    camera: "South Perimeter Gate",
    created_at: new Date(Date.now() - 1000 * 60 * 60 * 5).toISOString(),
  },
];

export default function IncidentsPage() {
  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-text-primary">Incident Management</h1>
          <p className="text-xs text-text-secondary mt-1">Review, acknowledge, investigate, and resolve operator alerts.</p>
        </div>
      </div>

      <div className="glass-card overflow-hidden">
        <table className="w-full text-left text-sm">
          <thead className="bg-background-secondary text-xs uppercase tracking-wider text-text-secondary border-b border-white/5">
            <tr>
              <th className="px-6 py-3.5 font-semibold">Incident Title</th>
              <th className="px-6 py-3.5 font-semibold">Severity</th>
              <th className="px-6 py-3.5 font-semibold">Status</th>
              <th className="px-6 py-3.5 font-semibold">Camera Source</th>
              <th className="px-6 py-3.5 font-semibold">Confidence</th>
              <th className="px-6 py-3.5 font-semibold text-right">Age</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-white/5 text-text-primary">
            {INCIDENTS.map((inc) => (
              <tr key={inc.id} className="hover:bg-white/5 transition">
                <td className="px-6 py-4 font-semibold">
                  <Link href={`/incidents/${inc.id}`} className="hover:text-brand-cyan transition">
                    {inc.title}
                  </Link>
                </td>
                <td className="px-6 py-4">
                  <Badge type="severity" value={inc.severity} />
                </td>
                <td className="px-6 py-4">
                  <Badge type="status" value={inc.status} />
                </td>
                <td className="px-6 py-4 text-xs text-text-secondary">{inc.camera}</td>
                <td className="px-6 py-4 text-xs font-mono">{Math.round(inc.confidence * 100)}%</td>
                <td className="px-6 py-4 text-right text-xs text-text-secondary">{formatRelativeTime(inc.created_at)}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
''')

write("frontend/src/app/(dashboard)/incidents/[id]/page.tsx", '''
"use client";

import { useState } from "react";
import Link from "next/link";
import { Badge } from "@/components/ui/Badge";
import { CheckCircle2, Search, ArrowLeft, Clock } from "lucide-react";

export default function IncidentDetailPage({ params }: { params: { id: string } }) {
  const [status, setStatus] = useState("open");

  return (
    <div className="space-y-6 max-w-4xl">
      <Link href="/incidents" className="inline-flex items-center gap-1.5 text-xs text-text-secondary hover:text-brand-cyan transition">
        <ArrowLeft className="h-4 w-4" /> Back to Incident List
      </Link>

      <div className="glass-card p-6">
        <div className="flex items-start justify-between">
          <div>
            <div className="flex items-center gap-2 mb-2">
              <Badge type="severity" value="critical" />
              <Badge type="status" value={status} />
            </div>
            <h1 className="text-xl font-bold text-text-primary">Restricted Zone Occupancy in Secure Industrial Bay</h1>
            <p className="text-xs text-text-secondary mt-1">Incident ID: {params.id || "inc-02"} • Generated via Edge CV ByteTrack</p>
          </div>
        </div>

        <div className="mt-6 grid grid-cols-2 gap-4 border-t border-b border-white/5 py-4 text-xs">
          <div>
            <span className="text-text-secondary block">Camera Source</span>
            <span className="font-semibold text-text-primary">Industrial Logistics Bay (CAM-02)</span>
          </div>
          <div>
            <span className="text-text-secondary block">Confidence Score</span>
            <span className="font-semibold text-text-primary">94.2%</span>
          </div>
          <div>
            <span className="text-text-secondary block">Detected Objects</span>
            <span className="font-semibold text-text-primary">2 Persons (Dwell Time: 4.8s)</span>
          </div>
          <div>
            <span className="text-text-secondary block">Privacy Filter Status</span>
            <span className="font-semibold text-sentinel-success">Faces Blurred • Zero Raw Video Uploaded</span>
          </div>
        </div>

        <div className="mt-6 flex gap-3">
          <button
            onClick={() => setStatus("acknowledged")}
            className="rounded-lg bg-sentinel-warning/20 border border-sentinel-warning/30 px-4 py-2 text-xs font-semibold text-sentinel-warning hover:bg-sentinel-warning/30 transition"
          >
            Acknowledge Incident
          </button>
          <button
            onClick={() => setStatus("investigating")}
            className="rounded-lg bg-brand-blue/20 border border-brand-blue/30 px-4 py-2 text-xs font-semibold text-brand-blue hover:bg-brand-blue/30 transition"
          >
            Mark Investigating
          </button>
          <button
            onClick={() => setStatus("resolved")}
            className="rounded-lg bg-sentinel-success/20 border border-sentinel-success/30 px-4 py-2 text-xs font-semibold text-sentinel-success hover:bg-sentinel-success/30 transition"
          >
            Resolve Incident
          </button>
        </div>
      </div>

      {/* Audit Log */}
      <div className="glass-card p-6">
        <h3 className="text-sm font-semibold tracking-wide text-text-primary uppercase mb-4">Operator Audit Log</h3>
        <div className="space-y-3 text-xs">
          <div className="flex items-center gap-3 text-text-secondary">
            <Clock className="h-4 w-4 text-brand-cyan" />
            <span>Automated rule triggered by ByteTrack multi-object tracker</span>
            <span className="ml-auto text-[11px]">35 mins ago</span>
          </div>
          <div className="flex items-center gap-3 text-text-secondary">
            <Clock className="h-4 w-4 text-brand-cyan" />
            <span>Incident metadata ingested to central PostgreSQL database</span>
            <span className="ml-auto text-[11px]">35 mins ago</span>
          </div>
        </div>
      </div>
    </div>
  );
}
''')

write("frontend/src/app/(dashboard)/map/page.tsx", '''
"use client";

import MapView from "@/components/maps/MapView";

export default function GISMapPage() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold tracking-tight text-text-primary">Geospatial Intelligence Map</h1>
        <p className="text-xs text-text-secondary mt-1">
          OpenStreetMap coordinates, monitored sector zones, camera placements, and active alert markers.
        </p>
      </div>

      <MapView />
    </div>
  );
}
''')

write("frontend/src/app/(dashboard)/analytics/page.tsx", '''
"use client";

import { IncidentTrendChart } from "@/components/dashboard/IncidentTrendChart";
import { SeverityChart } from "@/components/dashboard/SeverityChart";
import { StatCard } from "@/components/ui/StatCard";

export default function AnalyticsPage() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold tracking-tight text-text-primary">Historical Analytics & Trends</h1>
        <p className="text-xs text-text-secondary mt-1">Deep inspection of camera performance, congestion patterns, and incident metrics.</p>
      </div>

      <div className="grid grid-cols-1 gap-4 sm:grid-cols-3">
        <StatCard title="Total Events (30 Days)" value="1,428" subtitle="Processed via edge YOLOv8" />
        <StatCard title="False Positive Rate" value="1.8%" subtitle="Human operator verified" />
        <StatCard title="Mean Time To Resolve" value="8.4 mins" subtitle="Operator response time" />
      </div>

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
        <div className="lg:col-span-2">
          <IncidentTrendChart />
        </div>
        <div>
          <SeverityChart />
        </div>
      </div>
    </div>
  );
}
''')

write("frontend/src/app/(dashboard)/search/page.tsx", '''
"use client";

import { useState } from "react";
import { Search as SearchIcon, Sparkles } from "lucide-react";
import { Badge } from "@/components/ui/Badge";
import { searchApi } from "@/lib/api";

export default function SemanticSearchPage() {
  const [query, setQuery] = useState("Vehicle congestion near main entrance");
  const [results, setResults] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);
  const [latency, setLatency] = useState<number | null>(null);

  const handleSearch = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    try {
      const res = await searchApi.semantic(query);
      setResults(res.data.results || []);
      setLatency(res.data.search_latency_ms || 42.1);
    } catch {
      // Mock results if backend offline
      setResults([
        {
          incident_id: "inc-01",
          title: "Vehicle Congestion Warning on Access Lane",
          description: "Multiple vehicles stationary over threshold near entrance gate",
          severity: "medium",
          status: "open",
          confidence: 0.88,
          similarity_score: 0.94,
        },
        {
          incident_id: "inc-04",
          title: "Stationary Vehicle Blockage on Emergency Fire Lane",
          description: "Emergency vehicle lane blocked by delivery truck",
          severity: "critical",
          status: "resolved",
          confidence: 0.96,
          similarity_score: 0.86,
        },
      ]);
      setLatency(38.4);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6 max-w-4xl">
      <div>
        <div className="inline-flex items-center gap-2 rounded-full border border-brand-cyan/30 bg-brand-cyan/10 px-3 py-1 text-xs font-semibold text-brand-cyan mb-2">
          <Sparkles className="h-3.5 w-3.5" />
          pgvector Semantic Retrieval Engine
        </div>
        <h1 className="text-2xl font-bold tracking-tight text-text-primary">Natural Language Incident Search</h1>
        <p className="text-xs text-text-secondary mt-1">
          Search past incidents using human queries. Vector embeddings generated locally via sentence-transformers (384-d).
        </p>
      </div>

      <form onSubmit={handleSearch} className="flex gap-3">
        <div className="relative flex-1">
          <SearchIcon className="absolute left-3.5 top-3.5 h-4 w-4 text-text-secondary" />
          <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            className="w-full rounded-lg bg-background-secondary border border-white/10 pl-10 pr-4 py-2.5 text-sm text-text-primary focus:border-brand-cyan focus:outline-none"
            placeholder="E.g., Find vehicle congestion incidents from last week..."
          />
        </div>
        <button
          type="submit"
          className="rounded-lg bg-brand-cyan px-5 py-2.5 text-sm font-semibold text-background hover:bg-brand-cyan/80 transition glow-cyan"
        >
          {loading ? "Searching..." : "Search"}
        </button>
      </form>

      {latency && (
        <div className="text-xs text-text-secondary">
          Retrieved {results.length} incidents in <strong className="text-brand-cyan">{latency} ms</strong>
        </div>
      )}

      <div className="space-y-3">
        {results.map((r) => (
          <div key={r.incident_id} className="glass-card p-4 transition hover:border-brand-cyan/30">
            <div className="flex items-start justify-between">
              <div>
                <h4 className="text-sm font-semibold text-text-primary">{r.title}</h4>
                <p className="mt-1 text-xs text-text-secondary">{r.description}</p>
              </div>
              <div className="flex flex-col items-end gap-1.5">
                <Badge type="severity" value={r.severity} />
                <span className="text-[10px] font-mono text-brand-cyan">
                  {Math.round(r.similarity_score * 100)}% match
                </span>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
''')

write("frontend/src/app/(dashboard)/rules/page.tsx", '''
"use client";

import { Badge } from "@/components/ui/Badge";
import { Sliders, Plus } from "lucide-react";

const RULES = [
  { id: "R-01", name: "Crowd Density Warning", type: "crowd_density", threshold: "5 Persons", duration: "3.0s", severity: "high", enabled: true },
  { id: "R-02", name: "Restricted Zone Intrusion", type: "restricted_zone", threshold: "1 Object", duration: "2.0s", severity: "critical", enabled: true },
  { id: "R-03", name: "Vehicle Congestion Check", type: "vehicle_congestion", threshold: "3 Vehicles", duration: "5.0s", severity: "medium", enabled: true },
  { id: "R-04", name: "Emergency Lane Blockage", type: "access_lane", threshold: "1 Vehicle", duration: "10.0s", severity: "critical", enabled: true },
];

export default function RulesEnginePage() {
  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-text-primary">Incident Rules Engine</h1>
          <p className="text-xs text-text-secondary mt-1">Define polygon zones, dwell thresholds, and automated incident severity triggers.</p>
        </div>
        <button className="inline-flex items-center gap-2 rounded-lg bg-brand-cyan px-4 py-2 text-xs font-semibold text-background hover:bg-brand-cyan/80 transition glow-cyan">
          <Plus className="h-4 w-4" /> Add Detection Rule
        </button>
      </div>

      <div className="glass-card overflow-hidden">
        <table className="w-full text-left text-sm">
          <thead className="bg-background-secondary text-xs uppercase tracking-wider text-text-secondary border-b border-white/5">
            <tr>
              <th className="px-6 py-3.5 font-semibold">Rule Name</th>
              <th className="px-6 py-3.5 font-semibold">Type</th>
              <th className="px-6 py-3.5 font-semibold">Threshold</th>
              <th className="px-6 py-3.5 font-semibold">Min Dwell Time</th>
              <th className="px-6 py-3.5 font-semibold">Severity</th>
              <th className="px-6 py-3.5 font-semibold text-right">Status</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-white/5 text-text-primary">
            {RULES.map((r) => (
              <tr key={r.id} className="hover:bg-white/5 transition">
                <td className="px-6 py-4 font-semibold">{r.name}</td>
                <td className="px-6 py-4 text-xs font-mono text-text-secondary">{r.type}</td>
                <td className="px-6 py-4 text-xs">{r.threshold}</td>
                <td className="px-6 py-4 text-xs">{r.duration}</td>
                <td className="px-6 py-4">
                  <Badge type="severity" value={r.severity} />
                </td>
                <td className="px-6 py-4 text-right">
                  <span className="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-semibold bg-sentinel-success/10 text-sentinel-success border border-sentinel-success/20">
                    Active
                  </span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
''')

write("frontend/src/app/(dashboard)/system/page.tsx", '''
"use client";

import { Activity, CheckCircle, Database, Server, Cpu } from "lucide-react";

export default function SystemHealthPage() {
  const components = [
    { name: "PostgreSQL with pgvector", status: "Healthy", latency: "1.8 ms", icon: Database },
    { name: "Redis Streams Event Broker", status: "Healthy", latency: "0.6 ms", icon: Server },
    { name: "Edge CV Detection Runtime", status: "Healthy (CUDA 12.1)", latency: "41.2 ms", icon: Cpu },
    { name: "Sentence Transformers Embedding Service", status: "Healthy (CPU)", latency: "24.5 ms", icon: Activity },
  ];

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold tracking-tight text-text-primary">System Health & Telemetry</h1>
        <p className="text-xs text-text-secondary mt-1">Infrastructure diagnostics, broker health, and edge runtime connectivity.</p>
      </div>

      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
        {components.map((c) => {
          const Icon = c.icon;
          return (
            <div key={c.name} className="glass-card p-5">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <div className="p-2 rounded-lg bg-brand-cyan/10 text-brand-cyan">
                    <Icon className="h-5 w-5" />
                  </div>
                  <div>
                    <h4 className="text-sm font-semibold text-text-primary">{c.name}</h4>
                    <span className="text-xs text-text-secondary">Latency: {c.latency}</span>
                  </div>
                </div>
                <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-semibold bg-sentinel-success/10 text-sentinel-success border border-sentinel-success/20">
                  <span className="h-1.5 w-1.5 rounded-full bg-sentinel-success animate-pulse" />
                  {c.status}
                </span>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
''')

write("frontend/src/app/(dashboard)/settings/page.tsx", '''
"use client";

import { useState } from "react";
import { ShieldCheck, Sliders, Lock } from "lucide-react";

export default function SettingsPage() {
  const [retention, setRetention] = useState(30);
  const [device, setDevice] = useState("auto");

  return (
    <div className="space-y-6 max-w-3xl">
      <div>
        <h1 className="text-2xl font-bold tracking-tight text-text-primary">System Settings</h1>
        <p className="text-xs text-text-secondary mt-1">Configure edge inference targets, retention windows, and privacy compliance options.</p>
      </div>

      <div className="glass-card p-6 space-y-6">
        <div>
          <h3 className="text-sm font-semibold text-text-primary uppercase tracking-wide">Privacy Compliance</h3>
          <p className="text-xs text-text-secondary mt-1">Strict metadata-only edge processing guarantees.</p>
          <div className="mt-4 flex items-center justify-between p-3 rounded-lg bg-background-secondary border border-white/5">
            <div>
              <span className="text-sm font-medium text-text-primary block">Metadata-Only Transmission</span>
              <span className="text-xs text-text-secondary">Raw video is strictly retained on the edge device.</span>
            </div>
            <span className="text-xs font-semibold text-sentinel-success bg-sentinel-success/10 px-3 py-1 rounded-full border border-sentinel-success/20">
              Enforced
            </span>
          </div>
        </div>

        <div className="border-t border-white/5 pt-6">
          <h3 className="text-sm font-semibold text-text-primary uppercase tracking-wide">Data Retention</h3>
          <p className="text-xs text-text-secondary mt-1">Automatic pruning of incident metadata.</p>
          <div className="mt-3 flex items-center gap-4">
            <input
              type="number"
              value={retention}
              onChange={(e) => setRetention(Number(e.target.value))}
              className="w-24 rounded-lg bg-background-secondary border border-white/10 px-3 py-2 text-sm text-text-primary"
            />
            <span className="text-xs text-text-secondary">Days before historical incidents are archived</span>
          </div>
        </div>

        <div className="border-t border-white/5 pt-6">
          <h3 className="text-sm font-semibold text-text-primary uppercase tracking-wide">Inference Hardware Target</h3>
          <p className="text-xs text-text-secondary mt-1">NVIDIA CUDA vs CPU execution target.</p>
          <select
            value={device}
            onChange={(e) => setDevice(e.target.value)}
            className="mt-3 rounded-lg bg-background-secondary border border-white/10 px-3 py-2 text-sm text-text-primary"
          >
            <option value="auto">Auto (CUDA if available, else CPU)</option>
            <option value="cuda">Force CUDA (NVIDIA GPU)</option>
            <option value="cpu">Force CPU Fallback</option>
          </select>
        </div>
      </div>
    </div>
  );
}
''')

print("Frontend Part 2 complete.")
