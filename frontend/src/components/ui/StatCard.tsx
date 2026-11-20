import React from "react";

interface StatCardProps {
  title: string;
  value: string | number;
  subtitle?: string;
  icon?: React.ReactNode;
  trend?: string;
  highlight?: boolean;
}

export function StatCard({ title, value, subtitle, icon, trend, highlight }: StatCardProps) {
  return (
    <div className={`glass-card p-5 transition hover:border-brand-cyan/30 ${highlight ? "border-brand-cyan/40 glow-cyan" : ""}`}>
      <div className="flex items-center justify-between">
        <span className="text-xs font-semibold tracking-wider text-text-secondary uppercase">{title}</span>
        {icon && <div className="text-brand-cyan">{icon}</div>}
      </div>
      <div className="mt-3 flex items-baseline gap-2">
        <span className="text-3xl font-extrabold tracking-tight text-text-primary">{value}</span>
        {trend && <span className="text-xs font-medium text-sentinel-success">{trend}</span>}
      </div>
      {subtitle && <p className="mt-1 text-xs text-text-secondary">{subtitle}</p>}
    </div>
  );
}
