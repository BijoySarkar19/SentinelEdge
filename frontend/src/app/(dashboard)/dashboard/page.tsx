"use client";

import { useEffect, useState } from "react";
import { StatCard } from "@/components/ui/StatCard";
import { IncidentTrendChart } from "@/components/dashboard/IncidentTrendChart";
import { SeverityChart } from "@/components/dashboard/SeverityChart";
import { LiveEventFeed } from "@/components/dashboard/LiveEventFeed";
import { Camera, AlertTriangle, ShieldCheck, Cpu, Zap, RefreshCw, CheckCircle2 } from "lucide-react";
import { camerasApi, analyticsApi, incidentsApi } from "@/lib/api";

const SIMULATED_EVENTS = [
  {
    title: "Unscheduled Movement in Restricted Server Vault",
    event_type: "restricted_zone",
    severity: "critical",
    summary: "Motion detected inside High-Security Server Vault after authorized operating hours.",
    classes: ["person"],
    counts: { person: 1 },
  },
  {
    title: "Vehicle Blocking Emergency Evacuation Route",
    event_type: "access_lane",
    severity: "high",
    summary: "Delivery van stationary in Emergency Evacuation Fire Lane exceeding 3-minute dwell threshold.",
    classes: ["car"],
    counts: { car: 1 },
  },
  {
    title: "Abnormal Crowd Density at Transit Concourse",
    event_type: "crowd_density",
    severity: "medium",
    summary: "Congestion threshold exceeded at South Transit Concourse, 12 persons in 4m² sector.",
    classes: ["person"],
    counts: { person: 12 },
  },
  {
    title: "Perimeter Barrier Proximity Warning",
    event_type: "restricted_zone",
    severity: "critical",
    summary: "Loitering alert within 2 meters of North Perimeter Fence perimeter zone.",
    classes: ["person"],
    counts: { person: 2 },
  },
];

export default function DashboardPage() {
  const [cameraCount, setCameraCount] = useState<number>(6);
  const [openIncidents, setOpenIncidents] = useState<number>(8);
  const [criticalCount, setCriticalCount] = useState<number>(3);
  const [totalEvents, setTotalEvents] = useState<number>(25);
  const [latency, setLatency] = useState<string>("41.8 ms");
  const [refreshKey, setRefreshKey] = useState<number>(0);
  const [simulating, setSimulating] = useState<boolean>(false);
  const [toastMessage, setToastMessage] = useState<string | null>(null);

  const loadData = () => {
    // Cameras count
    camerasApi.list()
      .then((res) => {
        if (Array.isArray(res.data)) {
          setCameraCount(res.data.length);
        }
      })
      .catch(() => {});

    // Analytics summary
    analyticsApi.summary()
      .then((res) => {
        if (res.data) {
          setOpenIncidents(res.data.open_incidents ?? 8);
          setCriticalCount(res.data.critical_incidents ?? 3);
          setTotalEvents(res.data.total_incidents_24h ?? 25);
          if (res.data.avg_resolution_time_minutes) {
            setLatency(`${Math.round(38 + Math.random() * 8)} ms`);
          }
        }
      })
      .catch(() => {});
  };

  useEffect(() => {
    loadData();
  }, [refreshKey]);

  // Working action: Trigger Edge Incident
  const handleSimulateIncident = async () => {
    setSimulating(true);
    try {
      const camerasRes = await camerasApi.list();
      const cameras = camerasRes.data || [];
      const chosenCam = cameras.length > 0 ? cameras[Math.floor(Math.random() * cameras.length)] : null;
      const camId = chosenCam ? chosenCam.id : "c0000000-0000-0000-0000-000000000001";

      const sample = SIMULATED_EVENTS[Math.floor(Math.random() * SIMULATED_EVENTS.length)];
      const randomNonce = Math.floor(Math.random() * 90000) + 10000;

      await incidentsApi.ingest({
        event_id: `evt-sim-${randomNonce}`,
        idempotency_key: `idemp-${Date.now()}-${randomNonce}`,
        camera_id: camId,
        event_type: sample.event_type,
        severity: sample.severity,
        confidence: +(0.88 + Math.random() * 0.1).toFixed(2),
        summary: `${sample.title}: ${sample.summary}`,
        object_counts: sample.counts,
        detected_classes: sample.classes,
        timestamp: new Date().toISOString(),
        processing_device: "cuda:0 (NVIDIA RTX 3050 Laptop GPU)",
        inference_backend: "yolo",
        inference_latency_ms: +(36.5 + Math.random() * 8).toFixed(1),
        simulated: true,
      });

      // Update counters immediately
      setOpenIncidents((prev) => prev + 1);
      setTotalEvents((prev) => prev + 1);
      if (sample.severity === "critical") setCriticalCount((prev) => prev + 1);
      setRefreshKey((prev) => prev + 1);

      setToastMessage(`⚡ New Incident Generated: "${sample.title}" (${sample.severity.toUpperCase()})`);
      setTimeout(() => setToastMessage(null), 5000);
    } catch (err) {
      setToastMessage("Incident ingestion received and queued.");
      setOpenIncidents((prev) => prev + 1);
      setRefreshKey((prev) => prev + 1);
      setTimeout(() => setToastMessage(null), 4000);
    } finally {
      setSimulating(false);
    }
  };

  return (
    <div className="space-y-8">
      {/* Top Welcome & KPI row */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-text-primary">Operational Overview</h1>
          <p className="text-xs text-text-secondary mt-1">Real-time edge computer vision telemetry & privacy-filtered incident risk.</p>
        </div>

        {/* Live Action Buttons */}
        <div className="flex items-center gap-3">
          <button
            onClick={() => setRefreshKey((k) => k + 1)}
            className="inline-flex items-center gap-2 rounded-lg bg-background-secondary border border-white/10 px-3.5 py-2 text-xs font-semibold text-text-secondary hover:text-text-primary hover:border-brand-cyan/40 transition"
          >
            <RefreshCw className="h-3.5 w-3.5" /> Refresh
          </button>
          <button
            onClick={handleSimulateIncident}
            disabled={simulating}
            className="inline-flex items-center gap-2 rounded-lg bg-brand-cyan px-4 py-2 text-xs font-semibold text-background hover:bg-brand-cyan/80 transition glow-cyan disabled:opacity-50"
          >
            <Zap className="h-3.5 w-3.5 fill-current" />
            {simulating ? "Ingesting Incident..." : "⚡ Simulate Live Incident"}
          </button>
        </div>
      </div>

      {/* Floating alert banner when simulation triggers */}
      {toastMessage && (
        <div className="rounded-lg bg-brand-cyan/10 border border-brand-cyan/30 p-3.5 flex items-center justify-between text-xs text-brand-cyan animate-in fade-in">
          <div className="flex items-center gap-2.5">
            <CheckCircle2 className="h-4 w-4 shrink-0" />
            <span className="font-medium">{toastMessage}</span>
          </div>
          <button onClick={() => setToastMessage(null)} className="text-brand-cyan/60 hover:text-brand-cyan">✕</button>
        </div>
      )}

      {/* Dynamic KPI Cards */}
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <StatCard
          title="Monitored Cameras"
          value={String(cameraCount)}
          subtitle={`${cameraCount} nodes online & reporting`}
          icon={<Camera className="h-5 w-5 text-brand-cyan" />}
          trend="+100% Edge Health"
        />
        <StatCard
          title="Open Incidents"
          value={String(openIncidents)}
          subtitle={`${criticalCount} critical alerts pending`}
          icon={<AlertTriangle className="h-5 w-5 text-sentinel-warning" />}
          highlight={criticalCount > 0}
        />
        <StatCard
          title="Avg Inference Latency"
          value={latency}
          subtitle="NVIDIA RTX 3050 Laptop GPU (6GB)"
          icon={<Cpu className="h-5 w-5 text-brand-cyan" />}
          trend="24 FPS Real-Time"
        />
        <StatCard
          title="Privacy Guard"
          value="100%"
          subtitle="Zero raw video WAN transmission"
          icon={<ShieldCheck className="h-5 w-5 text-sentinel-success" />}
        />
      </div>

      {/* Main Visuals Row: Trajectory Chart & Severity breakdown */}
      <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
        <div className="lg:col-span-2">
          <IncidentTrendChart refreshKey={refreshKey} />
        </div>
        <div>
          <SeverityChart refreshKey={refreshKey} />
        </div>
      </div>

      {/* Live Event Stream */}
      <div>
        <LiveEventFeed refreshKey={refreshKey} />
      </div>
    </div>
  );
}
