"use client";

import MapView from "@/components/maps/MapView";

export default function GISMapPage() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold tracking-tight text-text-primary">Geospatial Intelligence Map</h1>
        <p className="text-xs text-text-secondary mt-1">
          OpenStreetMap coordinates, monitored sector zones, camera placements, and active alert markers.
        </p>
      </div>

      <MapView />
    </div>
  );
}
