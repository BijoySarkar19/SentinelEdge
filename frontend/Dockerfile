# =============================================================================
# SentinelEdge — Next.js Frontend Dockerfile
# Three-stage build: deps → builder → runner (distroless-style, non-root)
# Requires Next.js output: 'standalone' in next.config.ts/js
# =============================================================================

# ---------------------------------------------------------------------------
# Stage 1 — deps: install Node dependencies with caching
# ---------------------------------------------------------------------------
FROM node:24-alpine AS deps

# Install libc compatibility for native modules on Alpine
RUN apk add --no-cache libc6-compat

WORKDIR /app

# Copy lockfile(s) first for optimal Docker layer caching
COPY package.json package-lock.json* ./
# Uncomment the relevant line if using Yarn or pnpm instead:
# COPY yarn.lock ./
# COPY pnpm-lock.yaml ./

# Install exact dependencies from lockfile
RUN npm ci --omit=dev --ignore-scripts

# ---------------------------------------------------------------------------
# Stage 2 — builder: compile Next.js application
# ---------------------------------------------------------------------------
FROM node:24-alpine AS builder

RUN apk add --no-cache libc6-compat

WORKDIR /app

# Bring in production node_modules from deps stage
COPY --from=deps /app/node_modules ./node_modules

# Copy full source
COPY . .

# Disable Next.js telemetry during build
ENV NEXT_TELEMETRY_DISABLED=1

# Build the application (outputs standalone + static bundles)
RUN npm run build

# ---------------------------------------------------------------------------
# Stage 3 — runner: minimal production image
# ---------------------------------------------------------------------------
FROM node:24-alpine AS runner

LABEL maintainer="SentinelEdge Team"
LABEL org.opencontainers.image.title="SentinelEdge Frontend"
LABEL org.opencontainers.image.description="Next.js privacy-first video intelligence dashboard"
LABEL org.opencontainers.image.version="0.1.0"

WORKDIR /app

ENV NODE_ENV=production
ENV NEXT_TELEMETRY_DISABLED=1
ENV PORT=3000
ENV HOSTNAME=0.0.0.0

# Create a non-root system user/group for security
RUN addgroup --system --gid 1001 nodejs \
 && adduser  --system --uid 1001 nextjs

# Copy public assets
COPY --from=builder /app/public ./public

# Copy the standalone server output (self-contained Node.js server)
COPY --from=builder --chown=nextjs:nodejs /app/.next/standalone ./

# Copy static assets into the expected location inside standalone output
COPY --from=builder --chown=nextjs:nodejs /app/.next/static ./.next/static

USER nextjs

EXPOSE 3000

# Health check — hits the Next.js health/readiness route
HEALTHCHECK --interval=30s --timeout=10s --retries=5 --start-period=30s \
  CMD wget -qO- http://localhost:3000/ > /dev/null 2>&1 || exit 1

# Start the standalone Next.js server
CMD ["node", "server.js"]
