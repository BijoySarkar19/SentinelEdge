"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { authApi } from "@/lib/api";
import {
  Bell,
  LogOut,
  Menu,
  Tv,
  Minimize2,
  Maximize2,
  Radio,
  User,
} from "lucide-react";

interface HeaderProps {
  onToggleMobileMenu?: () => void;
  tvMode?: boolean;
  onToggleTvMode?: () => void;
}

export function Header({ onToggleMobileMenu, tvMode = false, onToggleTvMode }: HeaderProps) {
  const router = useRouter();

  const handleLogout = async () => {
    try {
      await authApi.logout();
      router.push("/login");
    } catch {
      router.push("/login");
    }
  };

  const toggleBrowserFullscreen = () => {
    if (!document.fullscreenElement) {
      document.documentElement.requestFullscreen().catch(() => {});
    } else {
      if (document.exitFullscreen) {
        document.exitFullscreen().catch(() => {});
      }
    }
    if (onToggleTvMode) onToggleTvMode();
  };

  return (
    <header className="sticky top-0 z-20 flex h-16 w-full items-center justify-between bg-[#091426]/90 backdrop-blur-md px-4 sm:px-6 lg:px-8 border-b border-white/5">
      {/* Left Area: Mobile Hamburger + Telemetry Pill */}
      <div className="flex items-center gap-2.5 sm:gap-4">
        {/* Hamburger Menu Toggle (Mobile & Tablet) */}
        <button
          onClick={onToggleMobileMenu}
          className="p-2 -ml-2 rounded-xl text-text-secondary hover:text-text-primary hover:bg-white/5 lg:hidden transition"
          aria-label="Toggle navigation drawer"
        >
          <Menu className="h-5 w-5" />
        </button>

        {/* Live WebSocket Telemetry Pill */}
        <div className="flex items-center gap-2 rounded-full border border-sentinel-success/20 bg-sentinel-success/10 px-2.5 sm:px-3.5 py-1 text-[11px] sm:text-xs font-semibold text-sentinel-success shadow-sm">
          <span className="relative flex h-2 w-2">
            <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-sentinel-success opacity-75" />
            <span className="relative inline-flex rounded-full h-2 w-2 bg-sentinel-success" />
          </span>
          <span className="hidden sm:inline">Edge Stream:</span>
          <span>Live WebSocket</span>
        </div>
      </div>

      {/* Right Area: TV Fullscreen Mode + Alerts + Profile + Logout */}
      <div className="flex items-center gap-2 sm:gap-3.5">
        {/* TV / NOC Wall Fullscreen Mode Button */}
        <button
          onClick={toggleBrowserFullscreen}
          className={`flex items-center gap-1.5 p-2 sm:px-3 sm:py-1.5 rounded-xl border text-xs font-semibold transition ${
            tvMode
              ? "bg-brand-cyan text-background border-brand-cyan glow-cyan"
              : "border-white/10 text-text-secondary hover:text-text-primary hover:bg-white/5"
          }`}
          title={tvMode ? "Exit TV / Wall Display Mode" : "Enter TV / NOC Wall Display Mode"}
        >
          <Tv className="h-4 w-4 shrink-0" />
          <span className="hidden md:inline">{tvMode ? "TV Wall Mode Active" : "TV / NOC Mode"}</span>
        </button>

        {/* Incident Alerts Bell */}
        <Link
          href="/incidents"
          className="relative rounded-xl p-2 text-text-secondary hover:bg-white/5 hover:text-text-primary transition"
          title="Inspect Active Incidents"
        >
          <Bell className="h-5 w-5" />
          <span className="absolute top-1.5 right-1.5 h-2 w-2 rounded-full bg-sentinel-critical animate-pulse" />
        </Link>

        <div className="h-5 w-[1px] bg-white/10 hidden sm:block" />

        {/* Operator Profile Pill */}
        <div className="flex items-center gap-2 sm:gap-2.5">
          <div className="flex h-8 w-8 items-center justify-center rounded-xl bg-brand-cyan/20 border border-brand-cyan/30 text-xs font-bold text-brand-cyan shadow-sm">
            OP
          </div>
          <div className="text-left text-xs hidden sm:block">
            <span className="block font-semibold text-text-primary leading-tight">Operator</span>
            <span className="text-[10px] text-text-secondary">SecOps Level 2</span>
          </div>
        </div>

        {/* Sign Out Button */}
        <button
          onClick={handleLogout}
          className="rounded-xl p-2 text-text-secondary hover:bg-red-500/10 hover:text-red-400 transition ml-1"
          title="Sign Out"
        >
          <LogOut className="h-5 w-5" />
        </button>
      </div>
    </header>
  );
}
