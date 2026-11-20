"use client";

import { useState } from "react";
import { ShieldCheck, Sliders, Lock } from "lucide-react";

export default function SettingsPage() {
  const [retention, setRetention] = useState(30);
  const [device, setDevice] = useState("auto");

  return (
    <div className="space-y-6 max-w-3xl">
      <div>
        <h1 className="text-2xl font-bold tracking-tight text-text-primary">System Settings</h1>
        <p className="text-xs text-text-secondary mt-1">Configure edge inference targets, retention windows, and privacy compliance options.</p>
      </div>

      <div className="glass-card p-6 space-y-6">
        <div>
          <h3 className="text-sm font-semibold text-text-primary uppercase tracking-wide">Privacy Compliance</h3>
          <p className="text-xs text-text-secondary mt-1">Strict metadata-only edge processing guarantees.</p>
          <div className="mt-4 flex items-center justify-between p-3 rounded-lg bg-background-secondary border border-white/5">
            <div>
              <span className="text-sm font-medium text-text-primary block">Metadata-Only Transmission</span>
              <span className="text-xs text-text-secondary">Raw video is strictly retained on the edge device.</span>
            </div>
            <span className="text-xs font-semibold text-sentinel-success bg-sentinel-success/10 px-3 py-1 rounded-full border border-sentinel-success/20">
              Enforced
            </span>
          </div>
        </div>

        <div className="border-t border-white/5 pt-6">
          <h3 className="text-sm font-semibold text-text-primary uppercase tracking-wide">Data Retention</h3>
          <p className="text-xs text-text-secondary mt-1">Automatic pruning of incident metadata.</p>
          <div className="mt-3 flex items-center gap-4">
            <input
              type="number"
              value={retention}
              onChange={(e) => setRetention(Number(e.target.value))}
              className="w-24 rounded-lg bg-background-secondary border border-white/10 px-3 py-2 text-sm text-text-primary"
            />
            <span className="text-xs text-text-secondary">Days before historical incidents are archived</span>
          </div>
        </div>

        <div className="border-t border-white/5 pt-6">
          <h3 className="text-sm font-semibold text-text-primary uppercase tracking-wide">Inference Hardware Target</h3>
          <p className="text-xs text-text-secondary mt-1">NVIDIA CUDA vs CPU execution target.</p>
          <select
            value={device}
            onChange={(e) => setDevice(e.target.value)}
            className="mt-3 rounded-lg bg-background-secondary border border-white/10 px-3 py-2 text-sm text-text-primary"
          >
            <option value="auto">Auto (CUDA if available, else CPU)</option>
            <option value="cuda">Force CUDA (NVIDIA GPU)</option>
            <option value="cpu">Force CPU Fallback</option>
          </select>
        </div>
      </div>
    </div>
  );
}
