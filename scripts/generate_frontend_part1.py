import os

ROOT = r"c:\Users\bijoy\Desktop\SENTINEL-EDGE\SentinelEdge"

def write(rel_path, content):
    full_path = os.path.join(ROOT, rel_path)
    os.makedirs(os.path.dirname(full_path), exist_ok=True)
    with open(full_path, "w", encoding="utf-8") as f:
        f.write(content.strip() + "\n")
    print(f"Wrote {rel_path}")

# ==================== PUBLIC ASSETS ====================

write("frontend/public/manifest.json", '''
{
  "name": "SentinelEdge Incident Intelligence",
  "short_name": "SentinelEdge",
  "description": "Privacy-First Edge-to-Cloud Real-Time Video & Incident Intelligence Platform",
  "start_url": "/dashboard",
  "display": "standalone",
  "background_color": "#050B16",
  "theme_color": "#22D3EE",
  "icons": [
    {
      "src": "/icons/icon-192.svg",
      "sizes": "192x192",
      "type": "image/svg+xml"
    },
    {
      "src": "/icons/icon-512.svg",
      "sizes": "512x512",
      "type": "image/svg+xml"
    }
  ]
}
''')

write("frontend/public/icons/icon-192.svg", '''
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 192 192" width="192" height="192">
  <rect width="192" height="192" rx="36" fill="#050B16"/>
  <path d="M96 28 L152 52 V96 C152 132 128 160 96 172 C64 160 40 132 40 96 V52 Z" fill="#091426" stroke="#22D3EE" stroke-width="6"/>
  <circle cx="96" cy="100" r="26" fill="none" stroke="#22D3EE" stroke-width="5"/>
  <circle cx="96" cy="100" r="10" fill="#22D3EE"/>
</svg>
''')

write("frontend/public/icons/icon-512.svg", '''
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512" width="512" height="512">
  <rect width="512" height="512" rx="96" fill="#050B16"/>
  <path d="M256 72 L408 136 V256 C408 352 344 428 256 460 C168 428 104 352 104 256 V136 Z" fill="#091426" stroke="#22D3EE" stroke-width="14"/>
  <circle cx="256" cy="268" r="70" fill="none" stroke="#22D3EE" stroke-width="12"/>
  <circle cx="256" cy="268" r="28" fill="#22D3EE"/>
</svg>
''')

# ==================== APP LAYOUT & ERROR ====================

write("frontend/src/app/layout.tsx", '''
import type { Metadata, Viewport } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "SentinelEdge — Incident Intelligence",
  description: "Privacy-First Edge-to-Cloud Real-Time Video & Incident Intelligence Platform",
  manifest: "/manifest.json",
};

export const viewport: Viewport = {
  themeColor: "#050B16",
  width: "device-width",
  initialScale: 1,
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className="dark">
      <body className="min-h-screen bg-background text-text-primary antialiased selection:bg-brand-cyan/20 selection:text-brand-cyan">
        {children}
      </body>
    </html>
  );
}
''')

write("frontend/src/app/loading.tsx", '''
export default function Loading() {
  return (
    <div className="flex h-screen w-screen items-center justify-center bg-background">
      <div className="flex flex-col items-center gap-4">
        <div className="h-12 w-12 animate-spin rounded-full border-4 border-brand-cyan border-t-transparent glow-cyan" />
        <p className="text-sm tracking-wider text-text-secondary uppercase">Initializing SentinelEdge Feed...</p>
      </div>
    </div>
  );
}
''')

write("frontend/src/app/error.tsx", '''
"use client";

import { useEffect } from "react";

export default function Error({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  useEffect(() => {
    console.error("Dashboard error:", error);
  }, [error]);

  return (
    <div className="flex h-screen w-full flex-col items-center justify-center gap-6 bg-background px-4">
      <div className="glass-card flex max-w-md flex-col items-center p-8 text-center">
        <div className="mb-4 flex h-14 w-14 items-center justify-center rounded-full bg-red-500/10 text-sentinel-critical">
          <svg className="h-8 w-8" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
          </svg>
        </div>
        <h2 className="text-xl font-bold text-text-primary">System Telemetry Interrupted</h2>
        <p className="mt-2 text-sm text-text-secondary">{error.message || "An unexpected error occurred in the monitoring runtime."}</p>
        <button
          onClick={() => reset()}
          className="mt-6 rounded-lg bg-brand-cyan px-5 py-2.5 text-sm font-semibold text-background transition hover:bg-brand-cyan/80 glow-cyan"
        >
          Re-establish Connection
        </button>
      </div>
    </div>
  );
}
''')

write("frontend/src/app/not-found.tsx", '''
"use client";

import { useState, useEffect, useCallback } from "react";
import Link from "next/link";

const GRID_SIZE = 18;
type Point = [number, number];

export default function NotFound() {
  const [snake, setSnake] = useState<Point[]>([[8, 8], [8, 9]]);
  const [food, setFood] = useState<Point>([4, 4]);
  const [dir, setDir] = useState<Point>([0, -1]);
  const [score, setScore] = useState(0);
  const [gameOver, setGameOver] = useState(false);
  const [isPlaying, setIsPlaying] = useState(false);

  const resetGame = () => {
    setSnake([[8, 8], [8, 9]]);
    setFood([4, 4]);
    setDir([0, -1]);
    setScore(0);
    setGameOver(false);
    setIsPlaying(true);
  };

  const moveSnake = useCallback(() => {
    if (gameOver || !isPlaying) return;

    setSnake((prev) => {
      const head = prev[0];
      const newHead: Point = [
        (head[0] + dir[0] + GRID_SIZE) % GRID_SIZE,
        (head[1] + dir[1] + GRID_SIZE) % GRID_SIZE,
      ];

      // Self collision
      if (prev.some(([x, y]) => x === newHead[0] && y === newHead[1])) {
        setGameOver(true);
        return prev;
      }

      const nextSnake = [newHead, ...prev];
      if (newHead[0] === food[0] && newHead[1] === food[1]) {
        setScore((s) => s + 10);
        setFood([
          Math.floor(Math.random() * GRID_SIZE),
          Math.floor(Math.random() * GRID_SIZE),
        ]);
      } else {
        nextSnake.pop();
      }
      return nextSnake;
    });
  }, [dir, food, gameOver, isPlaying]);

  useEffect(() => {
    const handleKey = (e: KeyboardEvent) => {
      if (e.key === "ArrowUp" && dir[1] !== 1) setDir([0, -1]);
      if (e.key === "ArrowDown" && dir[1] !== -1) setDir([0, 1]);
      if (e.key === "ArrowLeft" && dir[0] !== 1) setDir([-1, 0]);
      if (e.key === "ArrowRight" && dir[0] !== -1) setDir([1, 0]);
    };
    window.addEventListener("keydown", handleKey);
    return () => window.removeEventListener("keydown", handleKey);
  }, [dir]);

  useEffect(() => {
    if (!isPlaying) return;
    const interval = setInterval(moveSnake, 130);
    return () => clearInterval(interval);
  }, [moveSnake, isPlaying]);

  return (
    <div className="flex min-h-screen flex-col items-center justify-center bg-background px-4 text-center">
      <div className="mb-4 inline-flex items-center gap-2 rounded-full border border-brand-cyan/30 bg-brand-cyan/10 px-4 py-1.5 text-xs font-semibold tracking-wider text-brand-cyan uppercase">
        <span className="h-2 w-2 rounded-full bg-brand-cyan animate-pulse" />
        Signal Lost • Error 404
      </div>
      <h1 className="text-4xl font-extrabold text-text-primary md:text-5xl">Feed Not Found</h1>
      <p className="mt-2 max-w-md text-sm text-text-secondary">
        The requested camera sector or incident report does not exist. Play the Sentinel Drone Patrol mini-game while reconnecting.
      </p>

      {/* Snake Game Terminal */}
      <div className="glass-card mt-6 p-4">
        <div className="mb-3 flex items-center justify-between text-xs text-text-secondary">
          <span>Score: <strong className="text-brand-cyan">{score}</strong></span>
          <span>Use Arrow Keys</span>
        </div>
        <div
          className="relative grid bg-background-secondary rounded-lg border border-white/5"
          style={{
            gridTemplateColumns: `repeat(${GRID_SIZE}, 18px)`,
            gridTemplateRows: `repeat(${GRID_SIZE}, 18px)`,
          }}
        >
          {Array.from({ length: GRID_SIZE * GRID_SIZE }).map((_, i) => {
            const x = i % GRID_SIZE;
            const y = Math.floor(i / GRID_SIZE);
            const isSnake = snake.some(([sx, sy]) => sx === x && sy === y);
            const isHead = snake[0][0] === x && snake[0][1] === y;
            const isFood = food[0] === x && food[1] === y;

            return (
              <div
                key={i}
                className={`h-[18px] w-[18px] rounded-xs transition-colors ${
                  isHead
                    ? "bg-brand-cyan glow-cyan"
                    : isSnake
                    ? "bg-brand-blue/70"
                    : isFood
                    ? "bg-sentinel-critical animate-ping"
                    : ""
                }`}
              />
            );
          })}
        </div>
        <div className="mt-4 flex justify-center gap-3">
          {!isPlaying ? (
            <button
              onClick={resetGame}
              className="rounded-lg bg-brand-cyan px-4 py-2 text-xs font-semibold text-background hover:bg-brand-cyan/80 glow-cyan"
            >
              Start Patrol Game
            </button>
          ) : gameOver ? (
            <button
              onClick={resetGame}
              className="rounded-lg bg-sentinel-critical px-4 py-2 text-xs font-semibold text-white"
            >
              Crashed! Play Again
            </button>
          ) : null}
        </div>
      </div>

      <Link
        href="/dashboard"
        className="mt-8 text-sm font-medium text-brand-cyan hover:underline"
      >
        ← Return to Incident Dashboard
      </Link>
    </div>
  );
}
''')

# ==================== AUTH PAGES ====================

write("frontend/src/app/(auth)/layout.tsx", '''
export default function AuthLayout({ children }: { children: React.ReactNode }) {
  return (
    <div className="flex min-h-screen items-center justify-center bg-background p-4">
      <div className="absolute inset-0 bg-grid-pattern opacity-40 pointer-events-none" />
      <div className="relative z-10 w-full max-w-md">{children}</div>
    </div>
  );
}
''')

write("frontend/src/app/login/page.tsx", '''
"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { authApi } from "@/lib/api";

export default function LoginPage() {
  const router = useRouter();
  const [username, setUsername] = useState("admin");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      await authApi.login(username, password || "Admin@Sentinel2026!");
      router.push("/dashboard");
    } catch (err: any) {
      setError(err?.response?.data?.detail || "Authentication failed. Please verify credentials.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="glass-card p-8 glow-cyan">
      <div className="flex flex-col items-center text-center">
        <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-brand-cyan/10 border border-brand-cyan/30 text-brand-cyan">
          <svg className="h-6 w-6" viewBox="0 0 24 24" fill="none" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
          </svg>
        </div>
        <h1 className="mt-4 text-2xl font-bold tracking-tight text-text-primary">SentinelEdge</h1>
        <p className="mt-1 text-xs text-text-secondary">Incident Intelligence & Operator Console</p>
      </div>

      {error && (
        <div className="mt-4 rounded-lg bg-red-500/10 border border-red-500/20 p-3 text-xs text-red-400">
          {error}
        </div>
      )}

      <form onSubmit={handleSubmit} className="mt-6 space-y-4">
        <div>
          <label className="block text-xs font-semibold uppercase tracking-wider text-text-secondary">
            Username
          </label>
          <input
            type="text"
            required
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            className="mt-1.5 w-full rounded-lg bg-background-secondary border border-white/10 px-3.5 py-2.5 text-sm text-text-primary placeholder:text-text-secondary/40 focus:border-brand-cyan focus:outline-none focus:ring-1 focus:ring-brand-cyan"
            placeholder="admin"
          />
        </div>

        <div>
          <label className="block text-xs font-semibold uppercase tracking-wider text-text-secondary">
            Password
          </label>
          <input
            type="password"
            required
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            className="mt-1.5 w-full rounded-lg bg-background-secondary border border-white/10 px-3.5 py-2.5 text-sm text-text-primary placeholder:text-text-secondary/40 focus:border-brand-cyan focus:outline-none focus:ring-1 focus:ring-brand-cyan"
            placeholder="••••••••••••"
          />
        </div>

        <button
          type="submit"
          disabled={loading}
          className="w-full rounded-lg bg-brand-cyan py-2.5 text-sm font-semibold text-background transition hover:bg-brand-cyan/80 disabled:opacity-50 glow-cyan"
        >
          {loading ? "Authenticating..." : "Sign In to Platform"}
        </button>
      </form>

      <div className="mt-6 text-center text-xs text-text-secondary">
        <p>Default Operator Credential: <code className="text-brand-cyan">admin</code></p>
      </div>
    </div>
  );
}
''')

# ==================== UI COMPONENTS ====================

write("frontend/src/components/ui/Badge.tsx", '''
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
''')

write("frontend/src/components/ui/StatCard.tsx", '''
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
''')

write("frontend/src/components/layout/Sidebar.tsx", '''
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
''')

write("frontend/src/components/layout/Header.tsx", '''
"use client";

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
        <button
          className="relative rounded-lg p-2 text-text-secondary hover:bg-white/5 hover:text-text-primary transition"
          title="Incident Alerts"
        >
          <Bell className="h-5 w-5" />
          <span className="absolute top-1.5 right-1.5 h-2 w-2 rounded-full bg-sentinel-critical" />
        </button>

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
''')

write("frontend/src/app/(dashboard)/layout.tsx", '''
import { Sidebar } from "@/components/layout/Sidebar";
import { Header } from "@/components/layout/Header";

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <div className="min-h-screen bg-background">
      <Sidebar />
      <div className="pl-64 flex flex-col min-h-screen">
        <Header />
        <main className="flex-1 p-8 overflow-y-auto">
          {children}
        </main>
      </div>
    </div>
  );
}
''')

print("Frontend Part 1 complete.")
