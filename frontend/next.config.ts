import type { NextConfig } from 'next';

const nextConfig: NextConfig = {
  output: 'standalone',
  images: {
    remotePatterns: [
      { protocol: 'https', hostname: 'tile.openstreetmap.org' },
      { protocol: 'https', hostname: '*.tile.openstreetmap.org' },
    ],
  },
  typescript: { ignoreBuildErrors: false },
  eslint: { ignoreDuringBuilds: false },
  async redirects() {
    return [
      {
        source: '/',
        destination: '/dashboard',
        permanent: false,
      },
    ];
  },
  async headers() {
    return [
      {
        source: '/(.*)',
        headers: [
          { key: 'X-Frame-Options', value: 'SAMEORIGIN' },
          { key: 'X-Content-Type-Options', value: 'nosniff' },
          { key: 'Referrer-Policy', value: 'strict-origin-when-cross-origin' },
          { key: 'Permissions-Policy', value: 'camera=(), microphone=(), geolocation=()' },
        ],
      },
    ];
  },
  webpack(config) {
    return config;
  },
};

export default nextConfig;
