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
