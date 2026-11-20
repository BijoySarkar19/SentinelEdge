import React from "react";
import { getSeverityBadgeClass, getStatusBadgeClass } from "@/lib/utils";

interface BadgeProps {
  type?: "severity" | "status";
  value: string;
  className?: string;
}

export function Badge({ type = "severity", value, className = "" }: BadgeProps) {
  const badgeStyle = type === "severity" 
    ? getSeverityBadgeClass(value as any)
    : getStatusBadgeClass(value as any);

  return (
    <span
      className={`inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-semibold uppercase tracking-wider ${badgeStyle} ${className}`}
    >
      {value.replace("_", " ")}
    </span>
  );
}
