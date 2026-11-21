"use client";

import { useEffect, useState } from "react";
import { Badge } from "@/components/ui/Badge";
import { Camera, Plus, Trash2, CheckCircle2, X, RefreshCw, Radio } from "lucide-react";
import { camerasApi } from "@/lib/api";
import type { Camera as CameraType } from "@/types";

export default function CamerasPage() {
  const [cameras, setCameras] = useState<CameraType[]>([]);
  const [loading, setLoading] = useState(true);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [newName, setNewName] = useState("");
  const [newLocation, setNewLocation] = useState("");
  const [newSource, setNewSource] = useState("rtsp://edge-gateway:8554/cam_live");
  const [newType, setNewType] = useState<"rtsp" | "webcam" | "file" | "usb">("rtsp");
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

  const handleAddCamera = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newName.trim()) return;

    try {
      const res = await camerasApi.create({
        name: newName,
        location: newLocation || "Main Facility",
        source_type: newType,
        status: "processing",
        processing_enabled: true,
      });

      if (res.data) {
        setCameras((prev) => [res.data, ...prev]);
        setActionNotice(`Camera node "${newName}" provisioned successfully.`);
      }
      setIsModalOpen(false);
      setNewName("");
      setNewLocation("");
      setTimeout(() => setActionNotice(null), 4000);
    } catch (err: any) {
      setActionNotice("Failed to provision camera node. Please verify network credentials.");
      setTimeout(() => setActionNotice(null), 4000);
    }
  };

  const handleDeleteCamera = async (id: string, name: string) => {
    if (!confirm(`Are you sure you want to decommission camera node "${name}"?`)) return;

    try {
      await camerasApi.delete(id);
      setCameras((prev) => prev.filter((c) => c.id !== id));
      setActionNotice(`Camera "${name}" decommissioned.`);
      setTimeout(() => setActionNotice(null), 3000);
    } catch (err) {
      setActionNotice("Error deleting camera node.");
      setTimeout(() => setActionNotice(null), 3000);
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-text-primary">Camera Node Configuration</h1>
          <p className="text-xs text-text-secondary mt-1">Manage network video sources, RTSP streams, and local edge devices.</p>
        </div>
        <div className="flex items-center gap-3">
          <button
            onClick={loadCameras}
            className="inline-flex items-center gap-1.5 rounded-lg bg-background-secondary border border-white/10 px-3 py-2 text-xs font-semibold text-text-secondary hover:text-text-primary hover:border-brand-cyan/40 transition"
          >
            <RefreshCw className="h-3.5 w-3.5" /> Refresh
          </button>
          <button
            onClick={() => setIsModalOpen(true)}
            className="inline-flex items-center gap-2 rounded-lg bg-brand-cyan px-4 py-2 text-xs font-semibold text-background hover:bg-brand-cyan/80 transition glow-cyan"
          >
            <Plus className="h-4 w-4" /> Add Camera Node
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

      <div className="glass-card overflow-x-auto">
        <table className="w-full min-w-[650px] text-left text-sm">
          <thead className="bg-background-secondary text-xs uppercase tracking-wider text-text-secondary border-b border-white/5">
            <tr>
              <th className="px-6 py-3.5 font-semibold">Camera Node</th>
              <th className="px-6 py-3.5 font-semibold">Protocol / Source</th>
              <th className="px-6 py-3.5 font-semibold">Location</th>
              <th className="px-6 py-3.5 font-semibold">Status</th>
              <th className="px-6 py-3.5 font-semibold text-right">Actions</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-white/5 text-text-primary">
            {loading ? (
              <tr>
                <td colSpan={5} className="px-6 py-8 text-center text-xs text-text-secondary">
                  Scanning camera fleet...
                </td>
              </tr>
            ) : cameras.length === 0 ? (
              <tr>
                <td colSpan={5} className="px-6 py-8 text-center text-xs text-text-secondary">
                  No active cameras configured. Click "Add Camera Node" to register a feed.
                </td>
              </tr>
            ) : (
              cameras.map((c) => (
                <tr key={c.id} className="hover:bg-white/5 transition">
                  <td className="px-6 py-4">
                    <div className="flex items-center gap-2.5">
                      <div className="p-1.5 rounded-md bg-brand-cyan/10 text-brand-cyan">
                        <Camera className="h-4 w-4" />
                      </div>
                      <span className="font-semibold text-text-primary">{c.name}</span>
                    </div>
                  </td>
                  <td className="px-6 py-4 font-mono text-xs text-text-secondary">
                    {c.source_type.toUpperCase()} • {c.location || "Local Pipeline"}
                  </td>
                  <td className="px-6 py-4 text-xs text-text-secondary">{c.location || "Facility Zone"}</td>
                  <td className="px-6 py-4">
                    <Badge type="status" value={c.status} />
                  </td>
                  <td className="px-6 py-4 text-right">
                    <button
                      onClick={() => handleDeleteCamera(c.id, c.name)}
                      className="p-1.5 rounded hover:bg-sentinel-critical/10 text-text-secondary hover:text-sentinel-critical transition"
                      title="Decommission camera node"
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

      {/* Add Camera Modal Dialog */}
      {isModalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm p-4">
          <div className="glass-card max-w-md w-full p-6 space-y-4 animate-in fade-in zoom-in-95">
            <div className="flex items-center justify-between pb-3 border-b border-white/10">
              <h3 className="text-base font-bold text-text-primary">Provision Camera Node</h3>
              <button onClick={() => setIsModalOpen(false)} className="text-text-secondary hover:text-text-primary">
                <X className="h-5 w-5" />
              </button>
            </div>

            <form onSubmit={handleAddCamera} className="space-y-4 text-xs">
              <div>
                <label className="block font-semibold uppercase tracking-wider text-text-secondary mb-1">Camera Name</label>
                <input
                  type="text"
                  required
                  placeholder="e.g. Loading Dock Gate 2"
                  value={newName}
                  onChange={(e) => setNewName(e.target.value)}
                  className="w-full rounded-lg bg-background-secondary border border-white/10 px-3.5 py-2 text-text-primary placeholder:text-text-secondary/40 focus:border-brand-cyan focus:outline-none"
                />
              </div>

              <div>
                <label className="block font-semibold uppercase tracking-wider text-text-secondary mb-1">Facility Location</label>
                <input
                  type="text"
                  placeholder="e.g. Building B, West Wing"
                  value={newLocation}
                  onChange={(e) => setNewLocation(e.target.value)}
                  className="w-full rounded-lg bg-background-secondary border border-white/10 px-3.5 py-2 text-text-primary placeholder:text-text-secondary/40 focus:border-brand-cyan focus:outline-none"
                />
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block font-semibold uppercase tracking-wider text-text-secondary mb-1">Protocol Type</label>
                  <select
                    value={newType}
                    onChange={(e: any) => setNewType(e.target.value)}
                    className="w-full rounded-lg bg-background-secondary border border-white/10 px-3 py-2 text-text-primary focus:border-brand-cyan focus:outline-none"
                  >
                    <option value="rtsp">RTSP Stream</option>
                    <option value="webcam">USB / Webcam</option>
                    <option value="file">Synthetic Simulation</option>
                  </select>
                </div>

                <div>
                  <label className="block font-semibold uppercase tracking-wider text-text-secondary mb-1">Target FPS</label>
                  <input
                    type="number"
                    defaultValue={24}
                    className="w-full rounded-lg bg-background-secondary border border-white/10 px-3 py-2 text-text-primary"
                  />
                </div>
              </div>

              <div>
                <label className="block font-semibold uppercase tracking-wider text-text-secondary mb-1">Stream Endpoint URI</label>
                <input
                  type="text"
                  value={newSource}
                  onChange={(e) => setNewSource(e.target.value)}
                  className="w-full rounded-lg bg-background-secondary border border-white/10 px-3.5 py-2 font-mono text-text-primary focus:border-brand-cyan focus:outline-none"
                />
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
                  Register Node
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
