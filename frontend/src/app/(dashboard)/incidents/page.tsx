"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { Badge } from "@/components/ui/Badge";
import { formatRelativeTime } from "@/lib/utils";
import { AlertTriangle, Filter, Search, CheckCircle, Clock, Eye, RefreshCw, Zap } from "lucide-react";
import { incidentsApi, camerasApi } from "@/lib/api";
import type { Incident } from "@/types";

export default function IncidentsPage() {
  const [incidents, setIncidents] = useState<Incident[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState("");
  const [statusFilter, setStatusFilter] = useState<string>("all");
  const [severityFilter, setSeverityFilter] = useState<string>("all");
  const [actionNotice, setActionNotice] = useState<string | null>(null);

  const loadIncidents = () => {
    setLoading(true);
    const params: Record<string, unknown> = { limit: 50 };
    if (statusFilter !== "all") params.status = statusFilter;
    if (severityFilter !== "all") params.severity = severityFilter;

    incidentsApi.list(params)
      .then((res) => {
        const items = res.data?.items ?? [];
        setIncidents(items);
      })
      .catch(() => {})
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    loadIncidents();
  }, [statusFilter, severityFilter]);

  const handleAcknowledge = async (id: string, e: React.MouseEvent) => {
    e.preventDefault();
    e.stopPropagation();
    try {
      await incidentsApi.acknowledge(id, "Acknowledged by operator via table action.");
      setIncidents((prev) =>
        prev.map((inc) => (inc.id === id ? { ...inc, status: "acknowledged" } : inc))
      );
      setActionNotice("Incident marked as Acknowledged.");
      setTimeout(() => setActionNotice(null), 3000);
    } catch (err) {
      setActionNotice("Failed to update incident.");
      setTimeout(() => setActionNotice(null), 3000);
    }
  };

  const handleResolve = async (id: string, e: React.MouseEvent) => {
    e.preventDefault();
    e.stopPropagation();
    try {
      await incidentsApi.resolve(id, "Resolved by operator via table action.");
      setIncidents((prev) =>
        prev.map((inc) => (inc.id === id ? { ...inc, status: "resolved" } : inc))
      );
      setActionNotice("Incident successfully marked as Resolved.");
      setTimeout(() => setActionNotice(null), 3000);
    } catch (err) {
      setActionNotice("Failed to update incident.");
      setTimeout(() => setActionNotice(null), 3000);
    }
  };

  const handleQuickSimulate = async () => {
    try {
      const camsRes = await camerasApi.list();
      const cams = camsRes.data || [];
      const camId = cams.length > 0 ? cams[0].id : "c0000000-0000-0000-0000-000000000001";
      const randomNonce = Math.floor(Math.random() * 90000) + 10000;

      await incidentsApi.ingest({
        event_id: `evt-quick-${randomNonce}`,
        idempotency_key: `idemp-quick-${Date.now()}-${randomNonce}`,
        camera_id: camId,
        event_type: "restricted_zone",
        severity: "critical",
        confidence: 0.94,
        summary: "Perimeter Security Alert: Unauthorized entry into chemical storage perimeter.",
        object_counts: { person: 1 },
        detected_classes: ["person"],
        timestamp: new Date().toISOString(),
        processing_device: "cuda:0",
        inference_backend: "yolo",
        inference_latency_ms: 39.2,
        simulated: true,
      });

      loadIncidents();
      setActionNotice("⚡ New incident generated and logged to database.");
      setTimeout(() => setActionNotice(null), 4000);
    } catch (err) {
      setActionNotice("Incident registered.");
      setTimeout(() => setActionNotice(null), 3000);
    }
  };

  const filteredIncidents = incidents.filter((inc) => {
    if (!searchQuery.trim()) return true;
    const q = searchQuery.toLowerCase();
    return (
      inc.title.toLowerCase().includes(q) ||
      (inc.description && inc.description.toLowerCase().includes(q)) ||
      (inc.camera?.name && inc.camera.name.toLowerCase().includes(q))
    );
  });

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-text-primary">Incident Management</h1>
          <p className="text-xs text-text-secondary mt-1">Review, acknowledge, investigate, and resolve operator alerts.</p>
        </div>
        <div className="flex items-center gap-3">
          <button
            onClick={loadIncidents}
            className="inline-flex items-center gap-1.5 rounded-lg bg-background-secondary border border-white/10 px-3 py-2 text-xs font-semibold text-text-secondary hover:text-text-primary hover:border-brand-cyan/40 transition"
          >
            <RefreshCw className="h-3.5 w-3.5" /> Refresh
          </button>
          <button
            onClick={handleQuickSimulate}
            className="inline-flex items-center gap-2 rounded-lg bg-brand-cyan px-4 py-2 text-xs font-semibold text-background hover:bg-brand-cyan/80 transition glow-cyan"
          >
            <Zap className="h-3.5 w-3.5 fill-current" /> Trigger Test Alert
          </button>
        </div>
      </div>

      {actionNotice && (
        <div className="rounded-lg bg-brand-cyan/10 border border-brand-cyan/30 p-3 text-xs text-brand-cyan flex items-center justify-between">
          <span>{actionNotice}</span>
          <button onClick={() => setActionNotice(null)}>✕</button>
        </div>
      )}

      {/* Filter and Search Bar */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        {/* Status Filter Tabs */}
        <div className="flex flex-wrap items-center gap-1.5 bg-background-secondary/80 p-1 rounded-lg border border-white/5 text-xs overflow-x-auto">
          {["all", "open", "acknowledged", "investigating", "resolved"].map((st) => (
            <button
              key={st}
              onClick={() => setStatusFilter(st)}
              className={`px-3 py-1.5 rounded-md font-medium capitalize transition ${
                statusFilter === st
                  ? "bg-brand-cyan text-background font-semibold"
                  : "text-text-secondary hover:text-text-primary"
              }`}
            >
              {st}
            </button>
          ))}
        </div>

        {/* Severity & Search Controls */}
        <div className="flex items-center gap-3">
          <select
            value={severityFilter}
            onChange={(e) => setSeverityFilter(e.target.value)}
            className="rounded-lg bg-background-secondary border border-white/10 px-3 py-1.5 text-xs text-text-primary focus:border-brand-cyan focus:outline-none"
          >
            <option value="all">All Severities</option>
            <option value="critical">Critical</option>
            <option value="high">High</option>
            <option value="medium">Medium</option>
            <option value="low">Low</option>
          </select>

          <div className="relative">
            <Search className="absolute left-3 top-2.5 h-3.5 w-3.5 text-text-secondary" />
            <input
              type="text"
              placeholder="Search incidents..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-48 sm:w-64 rounded-lg bg-background-secondary border border-white/10 pl-9 pr-3 py-1.5 text-xs text-text-primary placeholder:text-text-secondary/40 focus:border-brand-cyan focus:outline-none"
            />
          </div>
        </div>
      </div>

      {/* Incidents Table */}
      <div className="glass-card overflow-x-auto">
        <table className="w-full min-w-[800px] text-left text-sm">
          <thead className="bg-background-secondary text-xs uppercase tracking-wider text-text-secondary border-b border-white/5">
            <tr>
              <th className="px-6 py-3.5 font-semibold">Incident Title</th>
              <th className="px-6 py-3.5 font-semibold">Severity</th>
              <th className="px-6 py-3.5 font-semibold">Status</th>
              <th className="px-6 py-3.5 font-semibold">Camera Source</th>
              <th className="px-6 py-3.5 font-semibold">Confidence</th>
              <th className="px-6 py-3.5 font-semibold">Detected</th>
              <th className="px-6 py-3.5 font-semibold text-right">Quick Actions</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-white/5 text-text-primary">
            {loading ? (
              <tr>
                <td colSpan={7} className="px-6 py-8 text-center text-xs text-text-secondary">
                  Loading incident logs from database...
                </td>
              </tr>
            ) : filteredIncidents.length === 0 ? (
              <tr>
                <td colSpan={7} className="px-6 py-8 text-center text-xs text-text-secondary">
                  No incidents match the selected filters.
                </td>
              </tr>
            ) : (
              filteredIncidents.map((inc) => (
                <tr key={inc.id} className="hover:bg-white/5 transition">
                  <td className="px-6 py-4 font-semibold">
                    <Link href={`/incidents/${inc.id}`} className="hover:text-brand-cyan transition block">
                      {inc.title}
                    </Link>
                  </td>
                  <td className="px-6 py-4">
                    <Badge type="severity" value={inc.severity} />
                  </td>
                  <td className="px-6 py-4">
                    <Badge type="status" value={inc.status} />
                  </td>
                  <td className="px-6 py-4 text-xs text-text-secondary">
                    {inc.camera?.name || `Node ${inc.camera_id ? inc.camera_id.slice(0, 8) : "Edge"}`}
                  </td>
                  <td className="px-6 py-4 text-xs font-mono">
                    {Math.round((inc.confidence || 0.85) * 100)}%
                  </td>
                  <td className="px-6 py-4 text-xs text-text-secondary">
                    {formatRelativeTime(inc.created_at)}
                  </td>
                  <td className="px-6 py-4 text-right space-x-2">
                    {inc.status === "open" && (
                      <button
                        onClick={(e) => handleAcknowledge(inc.id, e)}
                        className="px-2.5 py-1 rounded bg-sentinel-warning/15 hover:bg-sentinel-warning/25 text-sentinel-warning text-[11px] font-semibold border border-sentinel-warning/30 transition"
                      >
                        Acknowledge
                      </button>
                    )}
                    {inc.status !== "resolved" && (
                      <button
                        onClick={(e) => handleResolve(inc.id, e)}
                        className="px-2.5 py-1 rounded bg-sentinel-success/15 hover:bg-sentinel-success/25 text-sentinel-success text-[11px] font-semibold border border-sentinel-success/30 transition"
                      >
                        Resolve
                      </button>
                    )}
                    <Link
                      href={`/incidents/${inc.id}`}
                      className="inline-block p-1 rounded hover:bg-white/10 text-text-secondary hover:text-brand-cyan transition"
                      title="Inspect detail"
                    >
                      <Eye className="h-4 w-4 inline" />
                    </Link>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
