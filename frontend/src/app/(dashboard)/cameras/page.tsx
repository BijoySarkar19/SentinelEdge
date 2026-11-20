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
