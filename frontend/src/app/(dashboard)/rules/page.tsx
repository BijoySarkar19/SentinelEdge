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
