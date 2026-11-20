"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { authApi } from "@/lib/api";
import { Bell, LogOut, ShieldCheck } from "lucide-react";

export function Header() {
  const router = useRouter();

  const handleLogout = async () => {
    try {
      await authApi.logout();
      router.push("/login");
    } catch {
      router.push("/login");
    }
  };

  return (
    <header className="sticky top-0 z-20 flex h-16 w-full items-center justify-between bg-background-secondary/80 backdrop-blur-md px-8 border-b border-white/5">
      <div className="flex items-center gap-3">
        <div className="flex items-center gap-2 rounded-full border border-sentinel-success/20 bg-sentinel-success/10 px-3 py-1 text-xs font-semibold text-sentinel-success">
          <span className="h-2 w-2 rounded-full bg-sentinel-success animate-pulse" />
          Live WebSocket Telemetry
        </div>
      </div>

      <div className="flex items-center gap-4">
        <Link
          href="/incidents"
          className="relative rounded-lg p-2 text-text-secondary hover:bg-white/5 hover:text-text-primary transition"
          title="Inspect Active Incidents"
        >
          <Bell className="h-5 w-5" />
          <span className="absolute top-1.5 right-1.5 h-2 w-2 rounded-full bg-sentinel-critical animate-pulse" />
        </Link>

        <div className="h-6 w-[1px] bg-white/10" />

        <div className="flex items-center gap-3">
          <div className="flex h-8 w-8 items-center justify-center rounded-full bg-brand-cyan/20 text-xs font-bold text-brand-cyan">
            OP
          </div>
          <div className="text-left text-xs">
            <span className="block font-semibold text-text-primary">Operator</span>
            <span className="text-[10px] text-text-secondary">Level 2 Control</span>
          </div>
        </div>

        <button
          onClick={handleLogout}
          className="rounded-lg p-2 text-text-secondary hover:bg-red-500/10 hover:text-red-400 transition"
          title="Sign Out"
        >
          <LogOut className="h-5 w-5" />
        </button>
      </div>
    </header>
  );
}
