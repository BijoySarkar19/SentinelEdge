"use client";

import { useEffect, useState } from "react";
import { ResponsiveContainer, PieChart, Pie, Cell, Tooltip } from "recharts";
import { analyticsApi } from "@/lib/api";

const SEVERITY_COLORS: Record<string, string> = {
  critical: "#EF4444",
  high: "#F97316",
  medium: "#F59E0B",
  low: "#10B981",
  informational: "#3B82F6",
};

interface SeverityItem {
  name: string;
  value: number;
  color: string;
}

export function SeverityChart({ refreshKey }: { refreshKey?: number }) {
  const [data, setData] = useState<SeverityItem[]>([
    { name: "Critical", value: 3, color: "#EF4444" },
    { name: "High", value: 2, color: "#F97316" },
    { name: "Medium", value: 2, color: "#F59E0B" },
    { name: "Low", value: 1, color: "#10B981" },
  ]);

  useEffect(() => {
    analyticsApi.severity()
      .then((res) => {
        if (Array.isArray(res.data) && res.data.length > 0) {
          const formatted = res.data.map((item: any) => {
            const sevKey = (item.severity || "").toLowerCase();
            return {
              name: sevKey ? sevKey.charAt(0).toUpperCase() + sevKey.slice(1) : "Unknown",
              value: item.count ?? item.value ?? 0,
              color: SEVERITY_COLORS[sevKey] || "#94A3B8",
            };
          }).filter(d => d.value > 0);
          if (formatted.length > 0) {
            setData(formatted);
          }
        }
      })
      .catch(() => {});
  }, [refreshKey]);

  return (
    <div className="glass-card flex flex-col justify-between p-5">
      <div>
        <h3 className="text-sm font-semibold tracking-wide text-text-primary uppercase">Severity Composition</h3>
        <p className="text-xs text-text-secondary">Real-time incident distribution</p>
      </div>

      <div className="h-48 w-full mt-2">
        <ResponsiveContainer width="100%" height="100%">
          <PieChart>
            <Tooltip
              contentStyle={{ backgroundColor: "#0B192D", borderColor: "rgba(255,255,255,0.1)", borderRadius: "8px", fontSize: "12px" }}
            />
            <Pie
              data={data}
              innerRadius={50}
              outerRadius={75}
              paddingAngle={4}
              dataKey="value"
            >
              {data.map((entry, index) => (
                <Cell key={`cell-${index}`} fill={entry.color} />
              ))}
            </Pie>
          </PieChart>
        </ResponsiveContainer>
      </div>

      <div className="grid grid-cols-2 gap-2 pt-2 border-t border-white/5 text-[11px]">
        {data.map((d) => (
          <div key={d.name} className="flex items-center gap-2">
            <span className="h-2 w-2 rounded-full" style={{ backgroundColor: d.color }} />
            <span className="text-text-secondary">{d.name}:</span>
            <span className="font-semibold text-text-primary">{d.value}</span>
          </div>
        ))}
      </div>
    </div>
  );
}
