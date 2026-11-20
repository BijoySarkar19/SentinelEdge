"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { Badge } from "@/components/ui/Badge";
import { Camera, AlertTriangle, ShieldCheck, ExternalLink, X } from "lucide-react";

interface CameraPin {
  id: string;
  name: string;
  status: string;
  location?: string;
  x: number;
  y: number;
}

interface IncidentPin {
  id: string;
  title: string;
  severity: string;
  status: string;
  cameraName?: string;
  x: number;
  y: number;
}

interface MapViewProps {
  cameras?: CameraPin[];
  incidents?: IncidentPin[];
}

export default function MapView({ cameras = [], incidents = [] }: MapViewProps) {
  const [mounted, setMounted] = useState(false);
  const [selectedPin, setSelectedPin] = useState<{
    type: "camera" | "incident";
    id: string;
    title: string;
    subtitle: string;
    severity?: string;
    status: string;
  } | null>(null);

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

  return (
    <div className="relative h-[550px] w-full overflow-hidden rounded-xl bg-background-card border border-white/5">
      <div className="absolute top-4 left-4 z-10 rounded-md bg-background-secondary/90 px-3 py-1.5 text-xs font-semibold text-text-primary border border-white/10 backdrop-blur-md">
        Sector GIS Overview • Facility Polygon Coordinates
      </div>

      <div className="absolute bottom-4 right-4 z-10 rounded-md bg-background-secondary/90 px-3 py-1.5 text-xs text-text-secondary border border-white/10 backdrop-blur-md">
        Click any Camera or Alert Node to inspect telemetry
      </div>

      {/* Selected Node Popup Card */}
      {selectedPin && (
        <div className="absolute top-4 right-4 z-20 max-w-xs w-full glass-card p-4 border border-brand-cyan/40 shadow-xl animate-in fade-in zoom-in-95">
          <div className="flex items-start justify-between pb-2 border-b border-white/10">
            <div>
              <span className="text-[10px] font-mono tracking-wider uppercase text-brand-cyan">
                {selectedPin.type === "camera" ? "Camera Node Sensor" : "Active Incident Alert"}
              </span>
              <h4 className="text-xs font-bold text-text-primary mt-0.5">{selectedPin.title}</h4>
            </div>
            <button onClick={() => setSelectedPin(null)} className="text-text-secondary hover:text-text-primary">
              <X className="h-4 w-4" />
            </button>
          </div>

          <div className="mt-2 space-y-1.5 text-xs">
            <p className="text-text-secondary">{selectedPin.subtitle}</p>
            <div className="flex items-center gap-2 pt-1">
              {selectedPin.severity && <Badge type="severity" value={selectedPin.severity} />}
              <Badge type="status" value={selectedPin.status} />
            </div>
          </div>

          <div className="mt-3 pt-2 border-t border-white/10">
            {selectedPin.type === "incident" ? (
              <Link
                href={`/incidents/${selectedPin.id}`}
                className="w-full inline-flex items-center justify-center gap-1.5 px-3 py-1.5 rounded-lg bg-brand-cyan text-background font-semibold text-xs hover:bg-brand-cyan/80 transition"
              >
                Inspect Incident <ExternalLink className="h-3 w-3" />
              </Link>
            ) : (
              <Link
                href="/live-monitor"
                className="w-full inline-flex items-center justify-center gap-1.5 px-3 py-1.5 rounded-lg bg-brand-cyan text-background font-semibold text-xs hover:bg-brand-cyan/80 transition"
              >
                View Live Stream <ExternalLink className="h-3 w-3" />
              </Link>
            )}
          </div>
        </div>
      )}

      {/* SVG Canvas Map Rendering */}
      <svg className="h-full w-full bg-[#071322]">
        <defs>
          <pattern id="grid" width="40" height="40" patternUnits="userSpaceOnUse">
            <path d="M 40 0 L 0 0 0 40" fill="none" stroke="rgba(34,211,238,0.06)" strokeWidth="1" />
          </pattern>
        </defs>
        <rect width="100%" height="100%" fill="url(#grid)" />

        {/* Road and zone polygons */}
        <polygon points="100,70 340,90 380,260 140,240" fill="rgba(59,130,246,0.08)" stroke="#3B82F6" strokeWidth="1" strokeDasharray="4 2" />
        <text x="180" y="160" fill="#3B82F6" fontSize="11" opacity="0.6">Zone A - Access Corridor</text>

        <polygon points="450,160 760,180 720,440 430,410" fill="rgba(239,68,68,0.08)" stroke="#EF4444" strokeWidth="1" strokeDasharray="4 2" />
        <text x="540" y="290" fill="#EF4444" fontSize="11" opacity="0.6">Zone B - Restricted Perimeter</text>

        <polygon points="120,320 380,310 350,490 100,480" fill="rgba(16,185,129,0.08)" stroke="#10B981" strokeWidth="1" strokeDasharray="4 2" />
        <text x="180" y="410" fill="#10B981" fontSize="11" opacity="0.6">Zone C - Logistics Yard</text>

        {/* Camera Nodes */}
        {cameras.map((cam) => (
          <g
            key={cam.id}
            transform={`translate(${cam.x}, ${cam.y})`}
            className="cursor-pointer group"
            onClick={() =>
              setSelectedPin({
                type: "camera",
                id: cam.id,
                title: cam.name,
                subtitle: cam.location || "Facility Perimeter",
                status: cam.status,
              })
            }
          >
            <circle r="14" fill="#22D3EE" opacity="0.2" className="animate-ping" />
            <circle r="8" fill="#22D3EE" />
            <text x="14" y="4" fill="#F8FAFC" fontSize="11" fontWeight="600" className="group-hover:fill-brand-cyan transition">
              {cam.name}
            </text>
          </g>
        ))}

        {/* Incident Alerts */}
        {incidents.map((inc) => (
          <g
            key={inc.id}
            transform={`translate(${inc.x}, ${inc.y})`}
            className="cursor-pointer group"
            onClick={() =>
              setSelectedPin({
                type: "incident",
                id: inc.id,
                title: inc.title,
                subtitle: inc.cameraName || "Edge Detection Event",
                severity: inc.severity,
                status: inc.status,
              })
            }
          >
            <circle
              r="18"
              fill={inc.severity === "critical" ? "#EF4444" : "#F59E0B"}
              opacity="0.3"
              className="animate-ping"
            />
            <circle r="7" fill={inc.severity === "critical" ? "#EF4444" : "#F59E0B"} />
            <text
              x="12"
              y="4"
              fill={inc.severity === "critical" ? "#EF4444" : "#F59E0B"}
              fontSize="10"
              fontWeight="600"
              className="group-hover:underline"
            >
              {inc.title.slice(0, 22)}...
            </text>
          </g>
        ))}
      </svg>
    </div>
  );
}
