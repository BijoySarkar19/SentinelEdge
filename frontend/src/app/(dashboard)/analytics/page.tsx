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
