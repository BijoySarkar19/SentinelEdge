"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  LayoutDashboard,
  Radio,
  Camera,
  AlertTriangle,
  MapPin,
  BarChart3,
  Search,
  Sliders,
  Activity,
  Settings,
} from "lucide-react";

const NAVIGATION = [
  { name: "Dashboard", href: "/dashboard", icon: LayoutDashboard },
  { name: "Live Monitor", href: "/live-monitor", icon: Radio },
  { name: "Cameras", href: "/cameras", icon: Camera },
  { name: "Incidents", href: "/incidents", icon: AlertTriangle },
  { name: "GIS Map", href: "/map", icon: MapPin },
  { name: "Analytics", href: "/analytics", icon: BarChart3 },
  { name: "Smart Search", href: "/search", icon: Search },
  { name: "Rules Engine", href: "/rules", icon: Sliders },
  { name: "System Health", href: "/system", icon: Activity },
  { name: "Settings", href: "/settings", icon: Settings },
];

export function Sidebar() {
  const pathname = usePathname();

  return (
    <aside className="fixed inset-y-0 left-0 z-30 flex w-64 flex-col bg-background-secondary border-r border-white/5">
      {/* Brand logo */}
      <div className="flex h-16 items-center gap-3 px-6 border-b border-white/5">
        <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-brand-cyan/10 border border-brand-cyan/30 text-brand-cyan glow-cyan">
          <svg className="h-5 w-5" viewBox="0 0 24 24" fill="none" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
          </svg>
        </div>
        <div>
          <span className="text-base font-bold tracking-tight text-text-primary">SentinelEdge</span>
          <span className="block text-[10px] font-medium tracking-wider text-brand-cyan uppercase">Edge AI Platform</span>
        </div>
      </div>

      {/* Nav items */}
      <nav className="flex-1 space-y-1 px-3 py-4 overflow-y-auto">
        {NAVIGATION.map((item) => {
          const isActive = pathname === item.href || (item.href !== "/dashboard" && pathname.startsWith(item.href));
          const Icon = item.icon;
          return (
            <Link
              key={item.name}
              href={item.href}
              className={`flex items-center gap-3 rounded-lg px-3.5 py-2.5 text-sm font-medium transition ${
                isActive
                  ? "bg-brand-cyan/10 text-brand-cyan border border-brand-cyan/20"
                  : "text-text-secondary hover:bg-white/5 hover:text-text-primary"
              }`}
            >
              <Icon className={`h-4 w-4 ${isActive ? "text-brand-cyan" : "text-text-secondary"}`} />
              {item.name}
            </Link>
          );
        })}
      </nav>

      {/* Privacy guarantee badge */}
      <div className="p-4 border-t border-white/5">
        <div className="rounded-lg bg-background-card/50 p-3 border border-white/5 text-[11px] text-text-secondary">
          <div className="flex items-center gap-1.5 font-semibold text-brand-cyan mb-1">
            <span className="h-1.5 w-1.5 rounded-full bg-brand-cyan animate-pulse" />
            Privacy Mode: Active
          </div>
          Raw video is strictly retained on edge. Zero PII transmitted.
        </div>
      </div>
    </aside>
  );
}
