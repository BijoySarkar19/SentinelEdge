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
  X,
  ShieldCheck,
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

interface SidebarProps {
  isOpen?: boolean;
  onClose?: () => void;
  tvMode?: boolean;
}

export function Sidebar({ isOpen = false, onClose, tvMode = false }: SidebarProps) {
  const pathname = usePathname();

  // If in TV mode and not manually forced open, hide sidebar for full-screen NOC display
  if (tvMode && !isOpen) {
    return null;
  }

  return (
    <>
      {/* Mobile Backdrop Overlay */}
      {isOpen && (
        <div
          onClick={onClose}
          className="fixed inset-0 z-40 bg-black/70 backdrop-blur-sm lg:hidden transition-opacity duration-300 animate-in fade-in"
        />
      )}

      {/* Main Sidebar Navigation Panel */}
      <aside
        className={`fixed inset-y-0 left-0 z-50 flex w-64 2xl:w-72 flex-col bg-[#091426] border-r border-white/5 transition-transform duration-300 ease-in-out lg:translate-x-0 ${
          isOpen ? "translate-x-0 shadow-2xl" : "-translate-x-full"
        }`}
      >
        {/* Brand Header */}
        <div className="flex h-16 items-center justify-between px-5 sm:px-6 border-b border-white/5">
          <Link href="/dashboard" onClick={onClose} className="flex items-center gap-3">
            <div className="flex h-9 w-9 items-center justify-center rounded-xl bg-brand-cyan/10 border border-brand-cyan/30 text-brand-cyan glow-cyan">
              <svg className="h-5 w-5" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
              </svg>
            </div>
            <div>
              <span className="text-base font-extrabold tracking-tight text-text-primary">SentinelEdge</span>
              <span className="block text-[10px] font-semibold tracking-wider text-brand-cyan uppercase">Edge AI Platform</span>
            </div>
          </Link>

          {/* Close button for Mobile / Tablet */}
          <button
            onClick={onClose}
            className="p-1.5 rounded-lg text-text-secondary hover:text-text-primary hover:bg-white/5 lg:hidden"
            title="Close menu"
          >
            <X className="h-5 w-5" />
          </button>
        </div>

        {/* Nav Items List */}
        <nav className="flex-1 space-y-1 px-3 py-4 overflow-y-auto">
          {NAVIGATION.map((item) => {
            const isActive =
              pathname === item.href ||
              (item.href !== "/dashboard" && pathname.startsWith(item.href));
            const Icon = item.icon;
            return (
              <Link
                key={item.name}
                href={item.href}
                onClick={onClose}
                className={`flex items-center gap-3 rounded-xl px-3.5 py-2.5 text-sm font-medium transition duration-150 ${
                  isActive
                    ? "bg-brand-cyan/15 text-brand-cyan border border-brand-cyan/30 font-semibold shadow-sm shadow-cyan-950/30"
                    : "text-text-secondary hover:bg-white/5 hover:text-text-primary"
                }`}
              >
                <Icon className={`h-4 w-4 shrink-0 ${isActive ? "text-brand-cyan" : "text-text-secondary"}`} />
                <span className="truncate">{item.name}</span>
              </Link>
            );
          })}
        </nav>

        {/* Privacy & Compliance Guarantee Badge */}
        <div className="p-4 border-t border-white/5">
          <div className="rounded-xl bg-[#071322] p-3 border border-white/5 text-[11px] text-text-secondary">
            <div className="flex items-center gap-1.5 font-bold text-sentinel-success mb-1">
              <span className="h-1.5 w-1.5 rounded-full bg-sentinel-success animate-pulse" />
              Privacy Guard: Active
            </div>
            <p className="text-[10px] text-text-secondary/80 leading-relaxed">
              Zero raw video WAN transmission. Faces &amp; plates blurred at edge RAM.
            </p>
          </div>
        </div>
      </aside>
    </>
  );
}
