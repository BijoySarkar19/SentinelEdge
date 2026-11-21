"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { authApi } from "@/lib/api";
import {
  ShieldCheck,
  Lock,
  User,
  Eye,
  EyeOff,
  ArrowRight,
  Sparkles,
  AlertCircle,
  Radio,
  CheckCircle2,
} from "lucide-react";

export default function LoginPage() {
  const router = useRouter();
  const [username, setUsername] = useState("admin");
  const [password, setPassword] = useState("Admin@Sentinel2026!");
  const [showPassword, setShowPassword] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [quickFillActive, setQuickFillActive] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      await authApi.login(username, password || "Admin@Sentinel2026!");
      router.push("/dashboard");
    } catch (err: any) {
      setError(
        err?.response?.data?.detail ||
          "Authentication failed. Please verify credentials or backend cluster connectivity."
      );
    } finally {
      setLoading(false);
    }
  };

  const handleQuickFill = () => {
    setUsername("admin");
    setPassword("Admin@Sentinel2026!");
    setQuickFillActive(true);
    setTimeout(() => setQuickFillActive(false), 2000);
  };

  return (
    <div className="relative min-h-screen w-full flex flex-col items-center justify-center p-4 bg-[#050B16] overflow-hidden select-none">
      {/* Background Cyber Ambient Glow Orbs */}
      <div className="absolute -top-40 -left-40 h-96 w-96 rounded-full bg-brand-cyan/15 blur-[120px] pointer-events-none" />
      <div className="absolute -bottom-40 -right-40 h-96 w-96 rounded-full bg-brand-blue/15 blur-[120px] pointer-events-none" />
      <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 h-[500px] w-[500px] rounded-full bg-brand-purple/5 blur-[160px] pointer-events-none" />

      {/* Cybernetic Dot Grid Background */}
      <div className="absolute inset-0 bg-[radial-gradient(#22d3ee_1px,transparent_1px)] [background-size:32px_32px] opacity-[0.07] pointer-events-none" />

      {/* Floating System Status Pill */}
      <div className="mb-6 z-10 animate-in fade-in slide-in-from-top-4 duration-500">
        <div className="inline-flex items-center gap-2 rounded-full border border-brand-cyan/20 bg-brand-cyan/10 px-4 py-1.5 text-[11px] font-semibold text-brand-cyan backdrop-blur-md shadow-lg shadow-cyan-950/20">
          <span className="relative flex h-2 w-2">
            <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-brand-cyan opacity-75" />
            <span className="relative inline-flex rounded-full h-2 w-2 bg-brand-cyan" />
          </span>
          <span className="tracking-wider uppercase">SentinelEdge Cluster v1.0 • Node Fleet Secure</span>
        </div>
      </div>

      {/* Main Glassmorphic Login Card */}
      <div className="relative z-10 w-full max-w-[440px] rounded-2xl border border-white/10 bg-[#0B192D]/80 backdrop-blur-xl p-8 sm:p-10 shadow-2xl glow-cyan animate-in fade-in zoom-in-95 duration-300">
        {/* Corner Cyber Accent Crosshairs */}
        <div className="absolute top-3 left-3 h-2 w-2 border-t-2 border-l-2 border-brand-cyan/50" />
        <div className="absolute top-3 right-3 h-2 w-2 border-t-2 border-r-2 border-brand-cyan/50" />
        <div className="absolute bottom-3 left-3 h-2 w-2 border-b-2 border-l-2 border-brand-cyan/50" />
        <div className="absolute bottom-3 right-3 h-2 w-2 border-b-2 border-r-2 border-brand-cyan/50" />

        {/* Brand Shield & Title Header */}
        <div className="flex flex-col items-center text-center">
          <div className="relative flex h-14 w-14 items-center justify-center rounded-2xl bg-gradient-to-tr from-brand-cyan/20 to-brand-blue/20 border border-brand-cyan/40 text-brand-cyan shadow-inner">
            <ShieldCheck className="h-7 w-7" />
            <div className="absolute -inset-1 rounded-2xl border border-brand-cyan/20 animate-pulse pointer-events-none" />
          </div>

          <h1 className="mt-4 text-2xl sm:text-3xl font-extrabold tracking-tight bg-gradient-to-r from-white via-slate-100 to-brand-cyan bg-clip-text text-transparent">
            SentinelEdge
          </h1>
          <p className="mt-1.5 text-xs text-text-secondary leading-relaxed">
            Privacy-First Video &amp; Incident Intelligence Console
          </p>
        </div>

        {/* Quick Fill Demo Credentials Action */}
        <div className="mt-5 rounded-xl bg-white/[0.03] border border-white/5 p-2.5 flex items-center justify-between">
          <div className="text-[11px] text-text-secondary">
            <span className="text-text-primary font-medium">Demo Access:</span>{" "}
            <code className="text-brand-cyan font-mono">admin</code>
          </div>
          <button
            type="button"
            onClick={handleQuickFill}
            className={`text-[11px] font-semibold px-2.5 py-1 rounded-md transition flex items-center gap-1.5 ${
              quickFillActive
                ? "bg-sentinel-success/20 text-sentinel-success border border-sentinel-success/30"
                : "bg-brand-cyan/10 hover:bg-brand-cyan/20 text-brand-cyan border border-brand-cyan/30"
            }`}
          >
            {quickFillActive ? (
              <>
                <CheckCircle2 className="h-3 w-3" /> Loaded!
              </>
            ) : (
              <>
                <Sparkles className="h-3 w-3" /> Auto-Fill
              </>
            )}
          </button>
        </div>

        {/* Error Alert Box */}
        {error && (
          <div className="mt-4 rounded-lg bg-sentinel-critical/15 border border-sentinel-critical/30 p-3 text-xs text-sentinel-critical flex items-start gap-2 animate-in fade-in">
            <AlertCircle className="h-4 w-4 shrink-0 mt-0.5" />
            <span>{error}</span>
          </div>
        )}

        {/* Credentials Form */}
        <form onSubmit={handleSubmit} className="mt-6 space-y-4">
          <div>
            <label className="block text-[11px] font-semibold uppercase tracking-wider text-text-secondary mb-1.5">
              Operator Identification
            </label>
            <div className="relative">
              <User className="absolute left-3.5 top-3 h-4 w-4 text-text-secondary/60" />
              <input
                type="text"
                required
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                placeholder="Enter operator username"
                className="w-full rounded-xl bg-[#071322] border border-white/10 pl-10 pr-3.5 py-2.5 text-sm text-text-primary placeholder:text-text-secondary/40 focus:border-brand-cyan focus:outline-none focus:ring-1 focus:ring-brand-cyan transition"
              />
            </div>
          </div>

          <div>
            <label className="block text-[11px] font-semibold uppercase tracking-wider text-text-secondary mb-1.5">
              Security Token / Password
            </label>
            <div className="relative">
              <Lock className="absolute left-3.5 top-3 h-4 w-4 text-text-secondary/60" />
              <input
                type={showPassword ? "text" : "password"}
                required
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="Enter operator password"
                className="w-full rounded-xl bg-[#071322] border border-white/10 pl-10 pr-10 py-2.5 text-sm text-text-primary placeholder:text-text-secondary/40 focus:border-brand-cyan focus:outline-none focus:ring-1 focus:ring-brand-cyan transition"
              />
              <button
                type="button"
                onClick={() => setShowPassword(!showPassword)}
                className="absolute right-3.5 top-3 text-text-secondary/60 hover:text-text-primary transition"
                title={showPassword ? "Hide password" : "Show password"}
              >
                {showPassword ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
              </button>
            </div>
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full mt-2 rounded-xl bg-gradient-to-r from-brand-cyan to-brand-blue py-3 text-sm font-bold text-background transition hover:opacity-90 disabled:opacity-50 glow-cyan flex items-center justify-center gap-2 group shadow-lg shadow-cyan-950/40"
          >
            {loading ? (
              <>
                <div className="h-4 w-4 animate-spin rounded-full border-2 border-background border-t-transparent" />
                <span>Authorizing Clearance...</span>
              </>
            ) : (
              <>
                <span>Sign In to Platform</span>
                <ArrowRight className="h-4 w-4 transition group-hover:translate-x-1" />
              </>
            )}
          </button>
        </form>

        {/* Security & Compliance Footer */}
        <div className="mt-6 pt-5 border-t border-white/5 flex flex-col items-center gap-2 text-center text-[11px] text-text-secondary">
          <div className="flex items-center gap-1.5 text-sentinel-success font-medium">
            <Radio className="h-3 w-3 animate-pulse" />
            <span>256-bit AES Token Auth • Zero Raw Video WAN Transmission</span>
          </div>
          <div className="flex items-center gap-3 text-text-secondary/60 mt-1">
            <a
              href="https://github.com/BijoySarkar19/SentinelEdge/blob/main/docs/legal/PRIVACY_POLICY.md"
              target="_blank"
              rel="noreferrer"
              className="hover:text-brand-cyan transition underline underline-offset-2"
            >
              Privacy Architecture
            </a>
            <span>•</span>
            <a
              href="https://github.com/BijoySarkar19/SentinelEdge/blob/main/docs/legal/TERMS_OF_SERVICE.md"
              target="_blank"
              rel="noreferrer"
              className="hover:text-brand-cyan transition underline underline-offset-2"
            >
              Terms of Service
            </a>
            <span>•</span>
            <a
              href="https://github.com/BijoySarkar19/SentinelEdge/blob/main/docs/legal/GDPR_COMPLIANCE_GUIDE.md"
              target="_blank"
              rel="noreferrer"
              className="hover:text-brand-cyan transition underline underline-offset-2"
            >
              GDPR Compliance
            </a>
          </div>
        </div>
      </div>

      {/* Subtle Copyright Subtext */}
      <p className="mt-6 text-[11px] text-text-secondary/40 font-mono z-10">
        SentinelEdge © 2026 • Edge AI Computer Vision Platform
      </p>
    </div>
  );
}
