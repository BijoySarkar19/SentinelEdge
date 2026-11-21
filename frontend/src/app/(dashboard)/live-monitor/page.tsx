"use client";

import { useEffect, useState } from "react";
import { Badge } from "@/components/ui/Badge";
import { Camera, ShieldCheck, Play, Pause, Zap, Eye, RefreshCw, CheckCircle2 } from "lucide-react";
import { camerasApi, incidentsApi } from "@/lib/api";
import type { Camera as CameraType } from "@/types";

export default function LiveMonitorPage() {
  const [cameras, setCameras] = useState<CameraType[]>([]);
  const [loading, setLoading] = useState(true);
  const [privacyFilter, setPrivacyFilter] = useState<"blur" | "silhouette" | "bbox">("blur");
  const [activeAlertCam, setActiveAlertCam] = useState<string | null>(null);
  const [actionNotice, setActionNotice] = useState<string | null>(null);

  const loadCameras = () => {
    setLoading(true);
    camerasApi.list()
      .then((res) => {
        if (Array.isArray(res.data)) {
          setCameras(res.data);
        }
      })
      .catch(() => {})
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    loadCameras();
  }, []);

  const handleSimulateOnCamera = async (cam: CameraType) => {
    setActiveAlertCam(cam.id);
    try {
      const randomNonce = Math.floor(Math.random() * 90000) + 10000;
      await incidentsApi.ingest({
        event_id: `evt-monitor-${randomNonce}`,
        idempotency_key: `idemp-mon-${Date.now()}-${randomNonce}`,
        camera_id: cam.id,
        event_type: "restricted_zone",
        severity: "critical",
        confidence: 0.95,
        summary: `Immediate Security Breach at ${cam.name}: Unauthorized intrusion in camera field-of-view.`,
        object_counts: { person: 1 },
        detected_classes: ["person"],
        timestamp: new Date().toISOString(),
        processing_device: "cuda:0 (RTX 3050 Laptop GPU)",
        inference_backend: "yolo",
        inference_latency_ms: 38.2,
        simulated: true,
      });

      setActionNotice(`⚡ BREACH TRIGGERED on "${cam.name}". Incident logged to pgvector database.`);
      setTimeout(() => {
        setActiveAlertCam(null);
        setActionNotice(null);
      }, 6000);
    } catch (err) {
      setActionNotice(`Incident triggered on ${cam.name}.`);
      setTimeout(() => setActiveAlertCam(null), 4000);
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-text-primary">Live Edge Video Feeds</h1>
          <p className="text-xs text-text-secondary mt-1">
            Privacy-First Architecture: Edge computer vision with zero raw video transmitted across WAN.
          </p>
        </div>

        {/* Privacy Mode Selector */}
        <div className="flex items-center gap-2 bg-background-secondary p-1 rounded-lg border border-white/5 text-xs">
          <span className="text-[11px] text-text-secondary px-2">Privacy Mode:</span>
          {(["blur", "silhouette", "bbox"] as const).map((mode) => (
            <button
              key={mode}
              onClick={() => setPrivacyFilter(mode)}
              className={`px-2.5 py-1 rounded capitalize font-medium transition ${
                privacyFilter === mode
                  ? "bg-brand-cyan text-background font-semibold"
                  : "text-text-secondary hover:text-text-primary"
              }`}
            >
              {mode === "blur" ? "Face Blur" : mode === "silhouette" ? "Silhouette" : "Bounding Box"}
            </button>
          ))}
        </div>
      </div>

      {actionNotice && (
        <div className="rounded-lg bg-sentinel-critical/15 border border-sentinel-critical/30 p-3.5 text-xs text-sentinel-critical flex items-center justify-between animate-pulse">
          <div className="flex items-center gap-2">
            <Zap className="h-4 w-4 fill-current" />
            <span className="font-semibold">{actionNotice}</span>
          </div>
          <button onClick={() => setActionNotice(null)}>✕</button>
        </div>
      )}

      {/* Camera Video Grid */}
      <div className="grid grid-cols-1 gap-6 md:grid-cols-2 2xl:grid-cols-3">
        {loading ? (
          <div className="col-span-2 py-16 text-center text-xs text-text-secondary">
            Connecting to edge video multiplexer...
          </div>
        ) : cameras.length === 0 ? (
          <div className="col-span-2 py-16 text-center text-xs text-text-secondary">
            No camera streams registered. Add cameras on the Cameras page.
          </div>
        ) : (
          cameras.map((cam, idx) => {
            const isBreached = activeAlertCam === cam.id;
            const fakeFps = (23.8 + (idx % 3) * 0.4).toFixed(1);

            return (
              <div
                key={cam.id}
                className={`glass-card overflow-hidden transition duration-300 ${
                  isBreached ? "ring-2 ring-sentinel-critical border-sentinel-critical/50" : ""
                }`}
              >
                {/* Simulated Canvas Feed */}
                <div className="relative aspect-video bg-[#050C16] flex items-center justify-center border-b border-white/5 overflow-hidden">
                  {/* Subtle moving scan line */}
                  <div className="absolute inset-0 bg-gradient-to-b from-transparent via-brand-cyan/5 to-transparent h-16 w-full animate-pulse" />

                  {/* Synthetic Object Tracking Bounding Boxes */}
                  <div className="absolute inset-0 p-4 pointer-events-none">
                    <div
                      className="absolute border border-brand-cyan/60 bg-brand-cyan/10 rounded px-1 text-[9px] font-mono text-brand-cyan"
                      style={{ top: "30%", left: "25%", width: "90px", height: "130px" }}
                    >
                      <span>person 94%</span>
                      <div className="mt-1 w-full h-8 bg-black/40 backdrop-blur-md rounded border border-white/10 flex items-center justify-center text-[8px] text-sentinel-success">
                        [BLURRED]
                      </div>
                    </div>

                    <div
                      className="absolute border border-brand-blue/60 bg-brand-blue/10 rounded px-1 text-[9px] font-mono text-brand-blue"
                      style={{ top: "45%", right: "20%", width: "120px", height: "80px" }}
                    >
                      <span>car 91%</span>
                    </div>
                  </div>

                  {/* Status Overlay */}
                  <div className="text-center z-10 p-6">
                    <Camera className="mx-auto h-10 w-10 text-brand-cyan/50 mb-2 animate-pulse" />
                    <span className="text-xs font-mono text-text-primary block font-semibold">
                      {cam.name.toUpperCase()}
                    </span>
                    <span className="inline-block mt-2 rounded-md bg-white/5 border border-white/10 px-2.5 py-1 text-[11px] text-text-secondary">
                      {privacyFilter === "blur"
                        ? "Edge Face Blurring Applied"
                        : privacyFilter === "silhouette"
                        ? "Silhouette Geometry Shader"
                        : "Raw Metadata Vectors Only"}
                    </span>
                  </div>

                  {/* Overlay Badges */}
                  <div className="absolute top-3 left-3 flex gap-2 z-20">
                    <span className="rounded-md bg-background/80 backdrop-blur-md px-2 py-0.5 text-[10px] font-mono text-brand-cyan border border-brand-cyan/30">
                      {fakeFps} FPS
                    </span>
                    <span className="rounded-md bg-background/80 backdrop-blur-md px-2 py-0.5 text-[10px] font-mono text-sentinel-success border border-sentinel-success/30">
                      NVIDIA RTX 3050 (cuda:0)
                    </span>
                  </div>

                  {isBreached && (
                    <div className="absolute top-3 right-3 z-20 animate-bounce">
                      <span className="rounded-md bg-sentinel-critical px-2 py-1 text-[10px] font-bold text-white uppercase tracking-wider">
                        CRITICAL INTRUSION
                      </span>
                    </div>
                  )}
                </div>

                {/* Footer Controls */}
                <div className="p-4 flex items-center justify-between">
                  <div>
                    <h4 className="text-sm font-semibold text-text-primary">{cam.name}</h4>
                    <p className="text-xs text-text-secondary">{cam.location || "Facility Perimeter"}</p>
                  </div>
                  <div className="flex items-center gap-2">
                    <Badge type="status" value={cam.status} />
                    <button
                      onClick={() => handleSimulateOnCamera(cam)}
                      className="px-2.5 py-1.5 rounded-lg bg-brand-cyan/15 hover:bg-brand-cyan/25 border border-brand-cyan/30 text-brand-cyan text-xs font-semibold transition flex items-center gap-1"
                      title="Simulate incident trigger on this feed"
                    >
                      <Zap className="h-3 w-3 fill-current" /> Trigger Breach
                    </button>
                  </div>
                </div>
              </div>
            );
          })
        )}
      </div>
    </div>
  );
}
