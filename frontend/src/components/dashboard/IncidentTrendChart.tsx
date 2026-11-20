"use client";

import { useEffect, useState } from "react";
import { ResponsiveContainer, AreaChart, Area, XAxis, YAxis, Tooltip } from "recharts";
import { analyticsApi } from "@/lib/api";

interface TrendData {
  day: string;
  incidents: number;
  critical: number;
}

export function IncidentTrendChart({ refreshKey }: { refreshKey?: number }) {
  const [data, setData] = useState<TrendData[]>([
    { day: "Mon", incidents: 4, critical: 1 },
    { day: "Tue", incidents: 8, critical: 2 },
    { day: "Wed", incidents: 6, critical: 1 },
    { day: "Thu", incidents: 12, critical: 3 },
    { day: "Fri", incidents: 10, critical: 2 },
    { day: "Sat", incidents: 15, critical: 4 },
    { day: "Sun", incidents: 8, critical: 1 },
  ]);

  useEffect(() => {
    analyticsApi.trends(7)
      .then((res) => {
        if (Array.isArray(res.data) && res.data.length > 0) {
          const formatted = res.data.map((item: any) => ({
            day: item.date ? new Date(item.date).toLocaleDateString("en-US", { weekday: "short" }) : (item.day || "Day"),
            incidents: item.total_incidents ?? item.incidents ?? 0,
            critical: item.critical_count ?? item.critical ?? 0,
          }));
          setData(formatted);
        }
      })
      .catch(() => {
        // Keep fallback on error
      });
  }, [refreshKey]);

  return (
    <div className="glass-card p-5">
      <div className="flex items-center justify-between mb-4">
        <div>
          <h3 className="text-sm font-semibold tracking-wide text-text-primary uppercase">Incident Trajectory</h3>
          <p className="text-xs text-text-secondary">7-day edge incident volume vs critical alerts</p>
        </div>
        <div className="flex items-center gap-4 text-xs">
          <div className="flex items-center gap-1.5 text-brand-cyan">
            <span className="h-2 w-2 rounded-full bg-brand-cyan" /> Total
          </div>
          <div className="flex items-center gap-1.5 text-sentinel-critical">
            <span className="h-2 w-2 rounded-full bg-sentinel-critical" /> Critical
          </div>
        </div>
      </div>

      <div className="h-64 w-full">
        <ResponsiveContainer width="100%" height="100%">
          <AreaChart data={data}>
            <defs>
              <linearGradient id="totalGrad" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#22D3EE" stopOpacity={0.3} />
                <stop offset="95%" stopColor="#22D3EE" stopOpacity={0.0} />
              </linearGradient>
              <linearGradient id="critGrad" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#EF4444" stopOpacity={0.3} />
                <stop offset="95%" stopColor="#EF4444" stopOpacity={0.0} />
              </linearGradient>
            </defs>
            <XAxis dataKey="day" stroke="#94A3B8" fontSize={11} tickLine={false} axisLine={false} />
            <YAxis stroke="#94A3B8" fontSize={11} tickLine={false} axisLine={false} />
            <Tooltip
              contentStyle={{ backgroundColor: "#0B192D", borderColor: "rgba(255,255,255,0.1)", borderRadius: "8px", fontSize: "12px" }}
            />
            <Area type="monotone" dataKey="incidents" stroke="#22D3EE" strokeWidth={2} fillOpacity={1} fill="url(#totalGrad)" />
            <Area type="monotone" dataKey="critical" stroke="#EF4444" strokeWidth={2} fillOpacity={1} fill="url(#critGrad)" />
          </AreaChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}
