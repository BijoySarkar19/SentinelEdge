"use client";

import { useEffect, useState } from "react";
import MapView from "@/components/maps/MapView";
import { camerasApi, incidentsApi } from "@/lib/api";
import { RefreshCw } from "lucide-react";

export default function GISMapPage() {
  const [cameraPins, setCameraPins] = useState<any[]>([]);
  const [incidentPins, setIncidentPins] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  const loadPins = () => {
    setLoading(true);
    Promise.all([camerasApi.list(), incidentsApi.list({ limit: 10 })])
      .then(([camsRes, incsRes]) => {
        const cams = camsRes.data || [];
        const incs = incsRes.data?.items || [];

        // Distribute cameras across SVG canvas
        const camCoords = [
          { x: 190, y: 130 },
          { x: 580, y: 240 },
          { x: 260, y: 410 },
          { x: 670, y: 360 },
          { x: 420, y: 110 },
          { x: 340, y: 290 },
        ];

        setCameraPins(
          cams.map((c, i) => ({
            id: c.id,
            name: c.name,
            status: c.status,
            location: c.location,
            x: camCoords[i % camCoords.length].x,
            y: camCoords[i % camCoords.length].y,
          }))
        );

        // Distribute incidents
        const incCoords = [
          { x: 240, y: 170 },
          { x: 620, y: 290 },
          { x: 290, y: 440 },
          { x: 500, y: 380 },
          { x: 470, y: 140 },
        ];

        setIncidentPins(
          incs.slice(0, 5).map((inc, i) => ({
            id: inc.id,
            title: inc.title,
            severity: inc.severity,
            status: inc.status,
            cameraName: inc.camera?.name,
            x: incCoords[i % incCoords.length].x,
            y: incCoords[i % incCoords.length].y,
          }))
        );
      })
      .catch(() => {})
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    loadPins();
  }, []);

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-text-primary">Geospatial Intelligence Map</h1>
          <p className="text-xs text-text-secondary mt-1">
            OpenStreetMap coordinates, monitored sector zones, camera placements, and active alert markers.
          </p>
        </div>
        <button
          onClick={loadPins}
          className="inline-flex items-center gap-1.5 rounded-lg bg-background-secondary border border-white/10 px-3 py-2 text-xs font-semibold text-text-secondary hover:text-text-primary hover:border-brand-cyan/40 transition"
        >
          <RefreshCw className="h-3.5 w-3.5" /> Refresh Coordinates
        </button>
      </div>

      <MapView cameras={cameraPins} incidents={incidentPins} />
    </div>
  );
}
