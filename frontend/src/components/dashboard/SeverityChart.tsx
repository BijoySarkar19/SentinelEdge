"use client";

import { ResponsiveContainer, PieChart, Pie, Cell, Tooltip } from "recharts";

const data = [
  { name: "Critical", value: 14, color: "#EF4444" },
  { name: "High", value: 28, color: "#F97316" },
  { name: "Medium", value: 45, color: "#F59E0B" },
  { name: "Low", value: 32, color: "#10B981" },
  { name: "Informational", value: 19, color: "#3B82F6" },
];

export function SeverityChart() {
  return (
    <div className="glass-card flex flex-col justify-between p-5">
      <div>
        <h3 className="text-sm font-semibold tracking-wide text-text-primary uppercase">Severity Composition</h3>
        <p className="text-xs text-text-secondary">Distribution of detected incidents</p>
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
