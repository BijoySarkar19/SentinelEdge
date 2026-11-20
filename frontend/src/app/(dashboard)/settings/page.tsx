"use client";

import { useState, useEffect } from "react";
import { ShieldCheck, Sliders, Lock, Save, RotateCcw, Download, CheckCircle2 } from "lucide-react";

export default function SettingsPage() {
  const [retention, setRetention] = useState(30);
  const [device, setDevice] = useState("auto");
  const [privacyStrict, setPrivacyStrict] = useState(true);
  const [confidenceThreshold, setConfidenceThreshold] = useState(85);
  const [savedNotice, setSavedNotice] = useState<string | null>(null);

  useEffect(() => {
    const saved = localStorage.getItem("sentinel_settings");
    if (saved) {
      try {
        const parsed = JSON.parse(saved);
        if (parsed.retention) setRetention(parsed.retention);
        if (parsed.device) setDevice(parsed.device);
        if (parsed.confidenceThreshold) setConfidenceThreshold(parsed.confidenceThreshold);
        if (parsed.privacyStrict !== undefined) setPrivacyStrict(parsed.privacyStrict);
      } catch (e) {}
    }
  }, []);

  const handleSave = (e: React.FormEvent) => {
    e.preventDefault();
    const config = { retention, device, privacyStrict, confidenceThreshold, updatedAt: new Date().toISOString() };
    localStorage.setItem("sentinel_settings", JSON.stringify(config));
    setSavedNotice("Operational settings successfully applied to edge fleet.");
    setTimeout(() => setSavedNotice(null), 3500);
  };

  const handleReset = () => {
    setRetention(30);
    setDevice("auto");
    setPrivacyStrict(true);
    setConfidenceThreshold(85);
    localStorage.removeItem("sentinel_settings");
    setSavedNotice("Settings restored to factory defaults.");
    setTimeout(() => setSavedNotice(null), 3500);
  };

  const handleExport = () => {
    const config = {
      platform: "SentinelEdge v1.0",
      retention_days: retention,
      inference_target: device,
      privacy_enforced: privacyStrict,
      detection_threshold_percent: confidenceThreshold,
      exported_at: new Date().toISOString(),
    };
    const blob = new Blob([JSON.stringify(config, null, 2)], { type: "application/json" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `sentineledge_config_${Date.now()}.json`;
    a.click();
    URL.revokeObjectURL(url);
  };

  return (
    <div className="space-y-6 max-w-3xl">
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-text-primary">System Settings</h1>
          <p className="text-xs text-text-secondary mt-1">Configure edge inference targets, retention windows, and privacy compliance options.</p>
        </div>
        <div className="flex items-center gap-2">
          <button
            type="button"
            onClick={handleExport}
            className="inline-flex items-center gap-1.5 rounded-lg bg-background-secondary border border-white/10 px-3 py-2 text-xs font-semibold text-text-secondary hover:text-text-primary transition"
          >
            <Download className="h-3.5 w-3.5" /> Export JSON
          </button>
        </div>
      </div>

      {savedNotice && (
        <div className="rounded-lg bg-brand-cyan/10 border border-brand-cyan/30 p-3 text-xs text-brand-cyan flex items-center justify-between">
          <div className="flex items-center gap-2">
            <CheckCircle2 className="h-4 w-4" />
            <span>{savedNotice}</span>
          </div>
          <button onClick={() => setSavedNotice(null)}>✕</button>
        </div>
      )}

      <form onSubmit={handleSave} className="glass-card p-6 space-y-6">
        {/* Privacy Compliance */}
        <div>
          <h3 className="text-sm font-semibold text-text-primary uppercase tracking-wide">Privacy Compliance</h3>
          <p className="text-xs text-text-secondary mt-1">Strict metadata-only edge processing guarantees.</p>
          <div className="mt-4 flex items-center justify-between p-3.5 rounded-lg bg-background-secondary border border-white/5">
            <div>
              <span className="text-sm font-medium text-text-primary block">Metadata-Only Transmission</span>
              <span className="text-xs text-text-secondary">Raw video is strictly retained on edge RAM, never transmitted over WAN.</span>
            </div>
            <button
              type="button"
              onClick={() => setPrivacyStrict(!privacyStrict)}
              className={`text-xs font-semibold px-3 py-1.5 rounded-full border transition ${
                privacyStrict
                  ? "text-sentinel-success bg-sentinel-success/10 border-sentinel-success/30"
                  : "text-text-secondary bg-white/5 border-white/10"
              }`}
            >
              {privacyStrict ? "Enforced (Active)" : "Relaxed Mode"}
            </button>
          </div>
        </div>

        {/* Data Retention */}
        <div className="border-t border-white/5 pt-6">
          <h3 className="text-sm font-semibold text-text-primary uppercase tracking-wide">Data Retention Policy</h3>
          <p className="text-xs text-text-secondary mt-1">Automatic pruning of incident metadata from PostgreSQL.</p>
          <div className="mt-3 flex items-center gap-4">
            <input
              type="number"
              min={7}
              max={365}
              value={retention}
              onChange={(e) => setRetention(Number(e.target.value))}
              className="w-24 rounded-lg bg-background-secondary border border-white/10 px-3 py-2 text-sm text-text-primary focus:border-brand-cyan focus:outline-none"
            />
            <span className="text-xs text-text-secondary">Days before historical incident audit trails are archived</span>
          </div>
        </div>

        {/* Confidence Threshold */}
        <div className="border-t border-white/5 pt-6">
          <h3 className="text-sm font-semibold text-text-primary uppercase tracking-wide">Detection Confidence Threshold</h3>
          <p className="text-xs text-text-secondary mt-1">Minimum YOLOv8 model confidence required to trigger an operator alert.</p>
          <div className="mt-3 flex items-center gap-4">
            <input
              type="range"
              min={50}
              max={99}
              value={confidenceThreshold}
              onChange={(e) => setConfidenceThreshold(Number(e.target.value))}
              className="w-48 accent-brand-cyan"
            />
            <span className="text-xs font-mono text-brand-cyan font-semibold">{confidenceThreshold}%</span>
          </div>
        </div>

        {/* Inference Target */}
        <div className="border-t border-white/5 pt-6">
          <h3 className="text-sm font-semibold text-text-primary uppercase tracking-wide">Inference Hardware Target</h3>
          <p className="text-xs text-text-secondary mt-1">GPU Acceleration (NVIDIA CUDA) vs CPU fallback target.</p>
          <select
            value={device}
            onChange={(e) => setDevice(e.target.value)}
            className="mt-3 rounded-lg bg-background-secondary border border-white/10 px-3.5 py-2 text-xs text-text-primary focus:border-brand-cyan focus:outline-none"
          >
            <option value="auto">Auto (Detect NVIDIA RTX 3050 Laptop GPU, fallback to CPU)</option>
            <option value="cuda">Force CUDA (NVIDIA GPU Only)</option>
            <option value="cpu">Force CPU Fallback</option>
          </select>
        </div>

        {/* Submit Actions */}
        <div className="border-t border-white/5 pt-6 flex justify-between items-center">
          <button
            type="button"
            onClick={handleReset}
            className="inline-flex items-center gap-1.5 px-3 py-2 rounded-lg text-xs text-text-secondary hover:text-text-primary hover:bg-white/5 transition"
          >
            <RotateCcw className="h-3.5 w-3.5" /> Restore Defaults
          </button>
          <button
            type="submit"
            className="inline-flex items-center gap-2 px-5 py-2 rounded-lg bg-brand-cyan text-background font-semibold text-xs hover:bg-brand-cyan/80 transition glow-cyan"
          >
            <Save className="h-4 w-4" /> Save Configuration
          </button>
        </div>
      </form>
    </div>
  );
}
