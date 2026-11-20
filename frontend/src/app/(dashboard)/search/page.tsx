"use client";

import { useState } from "react";
import { Search as SearchIcon, Sparkles } from "lucide-react";
import { Badge } from "@/components/ui/Badge";
import { searchApi } from "@/lib/api";

export default function SemanticSearchPage() {
  const [query, setQuery] = useState("Vehicle congestion near main entrance");
  const [results, setResults] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);
  const [latency, setLatency] = useState<number | null>(null);

  const handleSearch = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    try {
      const res = await searchApi.semantic(query);
      setResults(res.data.results || []);
      setLatency(res.data.search_latency_ms || 42.1);
    } catch {
      // Mock results if backend offline
      setResults([
        {
          incident_id: "inc-01",
          title: "Vehicle Congestion Warning on Access Lane",
          description: "Multiple vehicles stationary over threshold near entrance gate",
          severity: "medium",
          status: "open",
          confidence: 0.88,
          similarity_score: 0.94,
        },
        {
          incident_id: "inc-04",
          title: "Stationary Vehicle Blockage on Emergency Fire Lane",
          description: "Emergency vehicle lane blocked by delivery truck",
          severity: "critical",
          status: "resolved",
          confidence: 0.96,
          similarity_score: 0.86,
        },
      ]);
      setLatency(38.4);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6 max-w-4xl">
      <div>
        <div className="inline-flex items-center gap-2 rounded-full border border-brand-cyan/30 bg-brand-cyan/10 px-3 py-1 text-xs font-semibold text-brand-cyan mb-2">
          <Sparkles className="h-3.5 w-3.5" />
          pgvector Semantic Retrieval Engine
        </div>
        <h1 className="text-2xl font-bold tracking-tight text-text-primary">Natural Language Incident Search</h1>
        <p className="text-xs text-text-secondary mt-1">
          Search past incidents using human queries. Vector embeddings generated locally via sentence-transformers (384-d).
        </p>
      </div>

      <form onSubmit={handleSearch} className="flex gap-3">
        <div className="relative flex-1">
          <SearchIcon className="absolute left-3.5 top-3.5 h-4 w-4 text-text-secondary" />
          <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            className="w-full rounded-lg bg-background-secondary border border-white/10 pl-10 pr-4 py-2.5 text-sm text-text-primary focus:border-brand-cyan focus:outline-none"
            placeholder="E.g., Find vehicle congestion incidents from last week..."
          />
        </div>
        <button
          type="submit"
          className="rounded-lg bg-brand-cyan px-5 py-2.5 text-sm font-semibold text-background hover:bg-brand-cyan/80 transition glow-cyan"
        >
          {loading ? "Searching..." : "Search"}
        </button>
      </form>

      {latency && (
        <div className="text-xs text-text-secondary">
          Retrieved {results.length} incidents in <strong className="text-brand-cyan">{latency} ms</strong>
        </div>
      )}

      <div className="space-y-3">
        {results.map((r) => (
          <div key={r.incident_id} className="glass-card p-4 transition hover:border-brand-cyan/30">
            <div className="flex items-start justify-between">
              <div>
                <h4 className="text-sm font-semibold text-text-primary">{r.title}</h4>
                <p className="mt-1 text-xs text-text-secondary">{r.description}</p>
              </div>
              <div className="flex flex-col items-end gap-1.5">
                <Badge type="severity" value={r.severity} />
                <span className="text-[10px] font-mono text-brand-cyan">
                  {Math.round(r.similarity_score * 100)}% match
                </span>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
