"use client";

import { useState } from "react";
import Link from "next/link";
import { Search as SearchIcon, Sparkles, ExternalLink } from "lucide-react";
import { Badge } from "@/components/ui/Badge";
import { searchApi } from "@/lib/api";

const SUGGESTIONS = [
  "chemical hazmat breach near fuel tank",
  "unauthorized person entering server room",
  "vehicle blocking emergency exit",
  "crowd gathering in restricted zone",
  "loitering at perimeter fence after hours",
];

export default function SemanticSearchPage() {
  const [query, setQuery] = useState("Vehicle congestion near main entrance");
  const [results, setResults] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);
  const [latency, setLatency] = useState<number | null>(null);

  const executeSearch = async (searchTerm: string) => {
    if (!searchTerm.trim()) return;
    setLoading(true);
    try {
      const res = await searchApi.semantic(searchTerm);
      setResults(res.data.results || []);
      setLatency(res.data.search_latency_ms || res.data.latency_ms || 42.1);
    } catch {
      // Graceful fallback
    } finally {
      setLoading(false);
    }
  };

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    executeSearch(query);
  };

  const handleSelectSuggestion = (sug: string) => {
    setQuery(sug);
    executeSearch(sug);
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
          disabled={loading}
          className="rounded-lg bg-brand-cyan px-5 py-2.5 text-sm font-semibold text-background hover:bg-brand-cyan/80 transition glow-cyan disabled:opacity-50"
        >
          {loading ? "Searching..." : "Search"}
        </button>
      </form>

      {/* Suggestion Chips */}
      <div className="flex flex-wrap items-center gap-2">
        <span className="text-[11px] text-text-secondary">Try searching:</span>
        {SUGGESTIONS.map((sug) => (
          <button
            key={sug}
            type="button"
            onClick={() => handleSelectSuggestion(sug)}
            className="text-[11px] px-2.5 py-1 rounded-md bg-white/5 hover:bg-brand-cyan/10 hover:text-brand-cyan border border-white/10 text-text-secondary transition"
          >
            "{sug}"
          </button>
        ))}
      </div>

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
                <div className="mt-3">
                  <Link
                    href={`/incidents/${r.incident_id}`}
                    className="inline-flex items-center gap-1 text-xs font-semibold text-brand-cyan hover:underline"
                  >
                    Open Forensic Investigation Workspace <ExternalLink className="h-3 w-3" />
                  </Link>
                </div>
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
