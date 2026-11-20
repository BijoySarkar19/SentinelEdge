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
