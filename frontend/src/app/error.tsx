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
