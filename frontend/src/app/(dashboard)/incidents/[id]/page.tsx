"use client";

import { useState } from "react";
import Link from "next/link";
import { Badge } from "@/components/ui/Badge";
import { CheckCircle2, Search, ArrowLeft, Clock } from "lucide-react";

export default function IncidentDetailPage({ params }: { params: { id: string } }) {
  const [status, setStatus] = useState("open");

  return (
    <div className="space-y-6 max-w-4xl">
      <Link href="/incidents" className="inline-flex items-center gap-1.5 text-xs text-text-secondary hover:text-brand-cyan transition">
        <ArrowLeft className="h-4 w-4" /> Back to Incident List
      </Link>

      <div className="glass-card p-6">
        <div className="flex items-start justify-between">
          <div>
            <div className="flex items-center gap-2 mb-2">
              <Badge type="severity" value="critical" />
              <Badge type="status" value={status} />
            </div>
            <h1 className="text-xl font-bold text-text-primary">Restricted Zone Occupancy in Secure Industrial Bay</h1>
            <p className="text-xs text-text-secondary mt-1">Incident ID: {params.id || "inc-02"} • Generated via Edge CV ByteTrack</p>
          </div>
        </div>

        <div className="mt-6 grid grid-cols-2 gap-4 border-t border-b border-white/5 py-4 text-xs">
          <div>
            <span className="text-text-secondary block">Camera Source</span>
            <span className="font-semibold text-text-primary">Industrial Logistics Bay (CAM-02)</span>
          </div>
          <div>
            <span className="text-text-secondary block">Confidence Score</span>
            <span className="font-semibold text-text-primary">94.2%</span>
          </div>
          <div>
            <span className="text-text-secondary block">Detected Objects</span>
            <span className="font-semibold text-text-primary">2 Persons (Dwell Time: 4.8s)</span>
          </div>
          <div>
            <span className="text-text-secondary block">Privacy Filter Status</span>
            <span className="font-semibold text-sentinel-success">Faces Blurred • Zero Raw Video Uploaded</span>
          </div>
        </div>

        <div className="mt-6 flex gap-3">
          <button
            onClick={() => setStatus("acknowledged")}
            className="rounded-lg bg-sentinel-warning/20 border border-sentinel-warning/30 px-4 py-2 text-xs font-semibold text-sentinel-warning hover:bg-sentinel-warning/30 transition"
          >
            Acknowledge Incident
          </button>
          <button
            onClick={() => setStatus("investigating")}
            className="rounded-lg bg-brand-blue/20 border border-brand-blue/30 px-4 py-2 text-xs font-semibold text-brand-blue hover:bg-brand-blue/30 transition"
          >
            Mark Investigating
          </button>
          <button
            onClick={() => setStatus("resolved")}
            className="rounded-lg bg-sentinel-success/20 border border-sentinel-success/30 px-4 py-2 text-xs font-semibold text-sentinel-success hover:bg-sentinel-success/30 transition"
          >
            Resolve Incident
          </button>
        </div>
      </div>

      {/* Audit Log */}
      <div className="glass-card p-6">
        <h3 className="text-sm font-semibold tracking-wide text-text-primary uppercase mb-4">Operator Audit Log</h3>
        <div className="space-y-3 text-xs">
          <div className="flex items-center gap-3 text-text-secondary">
            <Clock className="h-4 w-4 text-brand-cyan" />
            <span>Automated rule triggered by ByteTrack multi-object tracker</span>
            <span className="ml-auto text-[11px]">35 mins ago</span>
          </div>
          <div className="flex items-center gap-3 text-text-secondary">
            <Clock className="h-4 w-4 text-brand-cyan" />
            <span>Incident metadata ingested to central PostgreSQL database</span>
            <span className="ml-auto text-[11px]">35 mins ago</span>
          </div>
        </div>
      </div>
    </div>
  );
}
