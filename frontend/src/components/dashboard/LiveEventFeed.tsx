"use client";

import { useEffect, useState } from "react";
import { Badge } from "@/components/ui/Badge";
import { formatRelativeTime } from "@/lib/utils";
import { Radio } from "lucide-react";

interface LiveFeedItem {
  id: string;
  title: string;
  severity: string;
  camera: string;
  timestamp: string;
}

export function LiveEventFeed() {
  const [events, setEvents] = useState<LiveFeedItem[]>([
    {
      id: "ev-1",
      title: "Vehicle Congestion Warning on Gate 4 Access Lane",
      severity: "medium",
      camera: "North Gate Entrance",
      timestamp: new Date().toISOString(),
    },
    {
      id: "ev-2",
      title: "Restricted Zone Occupancy in Secure Industrial Bay",
      severity: "critical",
      camera: "Warehouse Yard",
      timestamp: new Date(Date.now() - 1000 * 60 * 3).toISOString(),
    },
    {
      id: "ev-3",
      title: "Unusual Crowd Density Exceeded Threshold in Main Lobby",
      severity: "high",
      camera: "Main Concourse",
      timestamp: new Date(Date.now() - 1000 * 60 * 8).toISOString(),
    },
    {
      id: "ev-4",
      title: "Emergency Lane Clear Check Scheduled",
      severity: "informational",
      camera: "Perimeter Perimeter 2",
      timestamp: new Date(Date.now() - 1000 * 60 * 15).toISOString(),
    },
  ]);

  return (
    <div className="glass-card flex flex-col p-5">
      <div className="flex items-center justify-between pb-4 border-b border-white/5">
        <div className="flex items-center gap-2">
          <Radio className="h-4 w-4 text-brand-cyan animate-pulse" />
          <h3 className="text-sm font-semibold tracking-wide text-text-primary uppercase">Live Edge Event Stream</h3>
        </div>
        <span className="text-[10px] tracking-wider text-brand-cyan uppercase bg-brand-cyan/10 px-2 py-0.5 rounded-full border border-brand-cyan/20">
          WebSocket Streaming
        </span>
      </div>

      <div className="mt-4 space-y-3 overflow-y-auto max-h-[380px] pr-1">
        {events.map((evt) => (
          <div
            key={evt.id}
            className="rounded-lg bg-background-secondary/60 p-3 border border-white/5 transition hover:border-brand-cyan/30"
          >
            <div className="flex items-start justify-between gap-3">
              <span className="text-xs font-medium text-text-primary leading-snug">{evt.title}</span>
              <Badge type="severity" value={evt.severity} />
            </div>
            <div className="mt-2 flex items-center justify-between text-[11px] text-text-secondary">
              <span>{evt.camera}</span>
              <span>{formatRelativeTime(evt.timestamp)}</span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
