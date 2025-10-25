/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  async rewrites() {
    return [
      // Proxy all /api/* calls to FastAPI backend in docker-compose network
      {
        source: '/api/:path*',
        destination: 'http://backend:8080/:path*',
      },
    ];
  },
};

export default nextConfig;
