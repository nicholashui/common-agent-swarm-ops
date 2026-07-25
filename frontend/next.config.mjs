const backendApiOrigin = process.env.BACKEND_API_ORIGIN;

function backendApiDestination(path) {
  if (backendApiOrigin === undefined || backendApiOrigin.length === 0) return null;
  const origin = new URL(backendApiOrigin);
  if (origin.protocol !== "http:" && origin.protocol !== "https:") throw new Error("BACKEND_API_ORIGIN must use HTTP or HTTPS.");
  if (origin.pathname !== "/" || origin.search || origin.hash) throw new Error("BACKEND_API_ORIGIN must be an origin without a path, query, or fragment.");
  return `${origin.origin}${path}`;
}

const SECURITY_HEADERS = [
  ["Content-Security-Policy", "default-src 'self'; base-uri 'self'; connect-src 'self'; frame-ancestors 'none'; frame-src 'none'; object-src 'none'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'; img-src 'self' data:; font-src 'self'; form-action 'self'; upgrade-insecure-requests"],
  ["Referrer-Policy", "no-referrer"],
  ["Strict-Transport-Security", "max-age=63072000; includeSubDomains; preload"],
  ["X-Content-Type-Options", "nosniff"],
];

/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  async headers() {
    return [
      { source: "/:path*", headers: SECURITY_HEADERS.map(([key, value]) => ({ key, value })) },
      { source: "/api/v1/:path*", headers: [{ key: "Cache-Control", value: "no-store" }] },
    ];
  },
  async rewrites() {
    const destination = backendApiDestination("/api/v1/:path*");
    return destination === null ? [] : [{ source: "/api/v1/:path*", destination }];
  },
};

export default nextConfig;
