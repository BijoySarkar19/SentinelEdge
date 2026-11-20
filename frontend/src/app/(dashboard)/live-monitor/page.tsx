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
