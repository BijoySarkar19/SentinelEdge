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
