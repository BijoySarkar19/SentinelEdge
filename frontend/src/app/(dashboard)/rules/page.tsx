"use client";

import { useEffect, useState } from "react";
import { Badge } from "@/components/ui/Badge";
import { Plus, Sliders, Trash2, CheckCircle2, X, RefreshCw, Power } from "lucide-react";
import { rulesApi, camerasApi } from "@/lib/api";
import type { Rule, Camera } from "@/types";

export default function RulesEnginePage() {
  const [rules, setRules] = useState<Rule[]>([]);
  const [cameras, setCameras] = useState<Camera[]>([]);
  const [loading, setLoading] = useState(true);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [actionNotice, setActionNotice] = useState<string | null>(null);

  // New Rule Form State
  const [ruleName, setRuleName] = useState("");
  const [selectedCameraId, setSelectedCameraId] = useState("");
  const [ruleType, setRuleType] = useState<string>("restricted_zone");
  const [threshold, setThreshold] = useState<number>(1);
  const [dwellTime, setDwellTime] = useState<number>(3.0);
  const [severity, setSeverity] = useState<"critical" | "high" | "medium" | "low">("high");

  const loadData = () => {
    setLoading(true);
    Promise.all([rulesApi.list(), camerasApi.list()])
      .then(([rulesRes, camerasRes]) => {
        if (Array.isArray(rulesRes.data)) setRules(rulesRes.data);
        if (Array.isArray(camerasRes.data)) {
          setCameras(camerasRes.data);
          if (camerasRes.data.length > 0 && !selectedCameraId) {
            setSelectedCameraId(camerasRes.data[0].id);
          }
        }
      })
      .catch(() => {})
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    loadData();
  }, []);

  const handleCreateRule = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!ruleName.trim() || !selectedCameraId) return;

    try {
      const res = await rulesApi.create({
        name: ruleName,
        camera_id: selectedCameraId,
        rule_type: ruleType as any,
        severity: severity,
        is_enabled: true,
        configuration: {
          threshold: Number(threshold),
          duration_seconds: Number(dwellTime),
          cooldown_seconds: 30,
        },
      });

      if (res.data) {
        setRules((prev) => [res.data, ...prev]);
        setActionNotice(`Rule "${ruleName}" successfully compiled into edge detection engine.`);
      }
      setIsModalOpen(false);
      setRuleName("");
      setTimeout(() => setActionNotice(null), 4000);
    } catch (err) {
      setActionNotice("Failed to create rule. Verify camera mapping.");
      setTimeout(() => setActionNotice(null), 4000);
    }
  };

  const handleToggleRule = async (r: Rule) => {
    try {
      const newEnabled = !r.is_enabled;
      await rulesApi.update(r.id, { is_enabled: newEnabled });
      setRules((prev) =>
        prev.map((item) => (item.id === r.id ? { ...item, is_enabled: newEnabled } : item))
      );
      setActionNotice(`Rule "${r.name}" is now ${newEnabled ? "ACTIVATED" : "DEACTIVATED"}.`);
      setTimeout(() => setActionNotice(null), 3000);
    } catch (err) {
      setActionNotice("Error updating rule status.");
      setTimeout(() => setActionNotice(null), 3000);
    }
  };

  const handleDeleteRule = async (id: string, name: string) => {
    if (!confirm(`Are you sure you want to delete rule "${name}"?`)) return;
    try {
      await rulesApi.delete(id);
      setRules((prev) => prev.filter((r) => r.id !== id));
      setActionNotice(`Rule "${name}" deleted.`);
      setTimeout(() => setActionNotice(null), 3000);
    } catch (err) {
      setActionNotice("Error deleting rule.");
      setTimeout(() => setActionNotice(null), 3000);
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-text-primary">Incident Rules Engine</h1>
          <p className="text-xs text-text-secondary mt-1">Define polygon zones, dwell thresholds, and automated incident severity triggers.</p>
        </div>
        <div className="flex items-center gap-3">
          <button
            onClick={loadData}
            className="inline-flex items-center gap-1.5 rounded-lg bg-background-secondary border border-white/10 px-3 py-2 text-xs font-semibold text-text-secondary hover:text-text-primary hover:border-brand-cyan/40 transition"
          >
            <RefreshCw className="h-3.5 w-3.5" /> Refresh
          </button>
          <button
            onClick={() => setIsModalOpen(true)}
            className="inline-flex items-center gap-2 rounded-lg bg-brand-cyan px-4 py-2 text-xs font-semibold text-background hover:bg-brand-cyan/80 transition glow-cyan"
          >
            <Plus className="h-4 w-4" /> Add Detection Rule
          </button>
        </div>
      </div>

      {actionNotice && (
        <div className="rounded-lg bg-brand-cyan/10 border border-brand-cyan/30 p-3 text-xs text-brand-cyan flex items-center justify-between">
          <div className="flex items-center gap-2">
            <CheckCircle2 className="h-4 w-4" />
            <span>{actionNotice}</span>
          </div>
          <button onClick={() => setActionNotice(null)}>✕</button>
        </div>
      )}

      <div className="glass-card overflow-hidden">
        <table className="w-full text-left text-sm">
          <thead className="bg-background-secondary text-xs uppercase tracking-wider text-text-secondary border-b border-white/5">
            <tr>
              <th className="px-6 py-3.5 font-semibold">Rule Name</th>
              <th className="px-6 py-3.5 font-semibold">Type</th>
              <th className="px-6 py-3.5 font-semibold">Threshold</th>
              <th className="px-6 py-3.5 font-semibold">Dwell Time</th>
              <th className="px-6 py-3.5 font-semibold">Severity</th>
              <th className="px-6 py-3.5 font-semibold">Status</th>
              <th className="px-6 py-3.5 font-semibold text-right">Actions</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-white/5 text-text-primary">
            {loading ? (
              <tr>
                <td colSpan={7} className="px-6 py-8 text-center text-xs text-text-secondary">
                  Loading rules engine configuration...
                </td>
              </tr>
            ) : rules.length === 0 ? (
              <tr>
                <td colSpan={7} className="px-6 py-8 text-center text-xs text-text-secondary">
                  No detection rules defined. Click "Add Detection Rule" to configure an event trigger.
                </td>
              </tr>
            ) : (
              rules.map((r) => (
                <tr key={r.id} className="hover:bg-white/5 transition">
                  <td className="px-6 py-4 font-semibold">{r.name}</td>
                  <td className="px-6 py-4 text-xs font-mono text-text-secondary">{r.rule_type}</td>
                  <td className="px-6 py-4 text-xs">
                    {r.configuration?.threshold ? `${r.configuration.threshold} objects` : "≥ 1 object"}
                  </td>
                  <td className="px-6 py-4 text-xs">
                    {r.configuration?.duration_seconds ? `${r.configuration.duration_seconds}s` : "3.0s"}
                  </td>
                  <td className="px-6 py-4">
                    <Badge type="severity" value={r.severity} />
                  </td>
                  <td className="px-6 py-4">
                    <button
                      onClick={() => handleToggleRule(r)}
                      className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-semibold border transition ${
                        r.is_enabled
                          ? "bg-sentinel-success/10 text-sentinel-success border-sentinel-success/30 hover:bg-sentinel-success/20"
                          : "bg-white/5 text-text-secondary border-white/10 hover:bg-white/10"
                      }`}
                    >
                      <Power className="h-3 w-3" />
                      {r.is_enabled ? "Active" : "Disabled"}
                    </button>
                  </td>
                  <td className="px-6 py-4 text-right">
                    <button
                      onClick={() => handleDeleteRule(r.id, r.name)}
                      className="p-1.5 rounded hover:bg-sentinel-critical/10 text-text-secondary hover:text-sentinel-critical transition"
                      title="Delete rule"
                    >
                      <Trash2 className="h-4 w-4 inline" />
                    </button>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>

      {/* Add Rule Modal */}
      {isModalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm p-4">
          <div className="glass-card max-w-md w-full p-6 space-y-4 animate-in fade-in zoom-in-95">
            <div className="flex items-center justify-between pb-3 border-b border-white/10">
              <h3 className="text-base font-bold text-text-primary">Configure Incident Rule</h3>
              <button onClick={() => setIsModalOpen(false)} className="text-text-secondary hover:text-text-primary">
                <X className="h-5 w-5" />
              </button>
            </div>

            <form onSubmit={handleCreateRule} className="space-y-4 text-xs">
              <div>
                <label className="block font-semibold uppercase tracking-wider text-text-secondary mb-1">Rule Name</label>
                <input
                  type="text"
                  required
                  placeholder="e.g. Server Vault Loitering Intrusion"
                  value={ruleName}
                  onChange={(e) => setRuleName(e.target.value)}
                  className="w-full rounded-lg bg-background-secondary border border-white/10 px-3.5 py-2 text-text-primary placeholder:text-text-secondary/40 focus:border-brand-cyan focus:outline-none"
                />
              </div>

              <div>
                <label className="block font-semibold uppercase tracking-wider text-text-secondary mb-1">Target Camera Node</label>
                <select
                  value={selectedCameraId}
                  onChange={(e) => setSelectedCameraId(e.target.value)}
                  className="w-full rounded-lg bg-background-secondary border border-white/10 px-3 py-2 text-text-primary focus:border-brand-cyan focus:outline-none"
                >
                  {cameras.map((c) => (
                    <option key={c.id} value={c.id}>
                      {c.name} ({c.location || "Facility"})
                    </option>
                  ))}
                </select>
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block font-semibold uppercase tracking-wider text-text-secondary mb-1">Rule Type</label>
                  <select
                    value={ruleType}
                    onChange={(e) => setRuleType(e.target.value)}
                    className="w-full rounded-lg bg-background-secondary border border-white/10 px-3 py-2 text-text-primary focus:border-brand-cyan focus:outline-none"
                  >
                    <option value="restricted_zone">Restricted Zone</option>
                    <option value="crowd_density">Crowd Density</option>
                    <option value="vehicle_congestion">Vehicle Congestion</option>
                    <option value="access_lane">Emergency Lane</option>
                  </select>
                </div>

                <div>
                  <label className="block font-semibold uppercase tracking-wider text-text-secondary mb-1">Severity Trigger</label>
                  <select
                    value={severity}
                    onChange={(e: any) => setSeverity(e.target.value)}
                    className="w-full rounded-lg bg-background-secondary border border-white/10 px-3 py-2 text-text-primary focus:border-brand-cyan focus:outline-none"
                  >
                    <option value="critical">Critical</option>
                    <option value="high">High</option>
                    <option value="medium">Medium</option>
                    <option value="low">Low</option>
                  </select>
                </div>
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block font-semibold uppercase tracking-wider text-text-secondary mb-1">Threshold (Objects)</label>
                  <input
                    type="number"
                    min={1}
                    value={threshold}
                    onChange={(e) => setThreshold(Number(e.target.value))}
                    className="w-full rounded-lg bg-background-secondary border border-white/10 px-3 py-2 text-text-primary"
                  />
                </div>

                <div>
                  <label className="block font-semibold uppercase tracking-wider text-text-secondary mb-1">Dwell Time (Seconds)</label>
                  <input
                    type="number"
                    step="0.5"
                    min={0.5}
                    value={dwellTime}
                    onChange={(e) => setDwellTime(Number(e.target.value))}
                    className="w-full rounded-lg bg-background-secondary border border-white/10 px-3 py-2 text-text-primary"
                  />
                </div>
              </div>

              <div className="pt-2 flex justify-end gap-2">
                <button
                  type="button"
                  onClick={() => setIsModalOpen(false)}
                  className="px-4 py-2 rounded-lg bg-background-secondary border border-white/10 text-text-secondary hover:text-text-primary"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-4 py-2 rounded-lg bg-brand-cyan text-background font-semibold hover:bg-brand-cyan/80 glow-cyan"
                >
                  Save Rule
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
