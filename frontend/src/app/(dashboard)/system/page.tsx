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
