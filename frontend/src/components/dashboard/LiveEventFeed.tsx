"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { Badge } from "@/components/ui/Badge";
import { formatRelativeTime } from "@/lib/utils";
import { Radio, RefreshCw, ExternalLink } from "lucide-react";
import { incidentsApi } from "@/lib/api";

interface LiveFeedItem {
  id: string;
  title: string;
  severity: string;
  camera: string;
  timestamp: string;
}

export function LiveEventFeed({ refreshKey }: { refreshKey?: number }) {
  const [events, setEvents] = useState<LiveFeedItem[]>([]);
  const [loading, setLoading] = useState(true);

  const fetchEvents = () => {
    incidentsApi.list({ limit: 8 })
      .then((res) => {
        const items = res.data?.items ?? [];
        if (Array.isArray(items) && items.length > 0) {
          setEvents(items.map((i: any) => ({
            id: i.id,
            title: i.title,
            severity: i.severity,
            camera: i.camera?.name || `Camera Node ${i.camera_id ? i.camera_id.slice(0, 8) : "Edge"}`,
            timestamp: i.created_at || new Date().toISOString(),
          })));
        }
      })
      .catch(() => {})
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    fetchEvents();
    // Poll every 10 seconds for real-time edge activity
    const interval = setInterval(fetchEvents, 10000);
    return () => clearInterval(interval);
  }, [refreshKey]);

  return (
    <div className="glass-card flex flex-col p-5">
      <div className="flex items-center justify-between pb-4 border-b border-white/5">
        <div className="flex items-center gap-2">
          <Radio className="h-4 w-4 text-brand-cyan animate-pulse" />
          <h3 className="text-sm font-semibold tracking-wide text-text-primary uppercase">Live Edge Event Stream</h3>
        </div>
        <div className="flex items-center gap-2">
          <button 
            onClick={fetchEvents}
            className="p-1 rounded-md text-text-secondary hover:text-brand-cyan transition hover:bg-white/5"
            title="Refresh feed"
          >
            <RefreshCw className="h-3.5 w-3.5" />
          </button>
          <span className="text-[10px] tracking-wider text-sentinel-success uppercase bg-sentinel-success/10 px-2 py-0.5 rounded-full border border-sentinel-success/20">
            Live Connected
          </span>
        </div>
      </div>

      <div className="mt-4 space-y-3 overflow-y-auto max-h-[380px] pr-1">
        {loading && events.length === 0 ? (
          <div className="py-8 text-center text-xs text-text-secondary">Connecting to edge streams...</div>
        ) : events.length === 0 ? (
          <div className="py-8 text-center text-xs text-text-secondary">No incidents reported recently. System normal.</div>
        ) : (
          events.map((evt) => (
            <Link
              key={evt.id}
              href={`/incidents/${evt.id}`}
              className="block rounded-lg bg-background-secondary/60 p-3 border border-white/5 transition hover:border-brand-cyan/40 hover:bg-background-secondary group"
            >
              <div className="flex items-start justify-between gap-3">
                <span className="text-xs font-medium text-text-primary leading-snug group-hover:text-brand-cyan transition">
                  {evt.title}
                </span>
                <Badge type="severity" value={evt.severity} />
              </div>
              <div className="mt-2 flex items-center justify-between text-[11px] text-text-secondary">
                <span>{evt.camera}</span>
                <span className="flex items-center gap-1">
                  {formatRelativeTime(evt.timestamp)}
                  <ExternalLink className="h-2.5 w-2.5 opacity-0 group-hover:opacity-100 transition" />
                </span>
              </div>
            </Link>
          ))
        )}
      </div>
    </div>
  );
}
