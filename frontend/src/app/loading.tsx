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
