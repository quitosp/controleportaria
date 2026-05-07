/** @type {import('next').NextConfig} */

const isProd = process.env.NODE_ENV === "production";
const apiUrl = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:5270";
const apiOrigin = (() => { try { return new URL(apiUrl).origin; } catch { return apiUrl; } })();
const apiWs = apiOrigin.replace(/^http/, "ws");

const securityHeaders = [
  { key: "Strict-Transport-Security", value: "max-age=63072000; includeSubDomains; preload" },
  { key: "X-Content-Type-Options", value: "nosniff" },
  { key: "X-Frame-Options", value: "DENY" },
  { key: "Referrer-Policy", value: "strict-origin-when-cross-origin" },
  { key: "Permissions-Policy", value: "camera=(), microphone=(), geolocation=()" },
  {
    key: "Content-Security-Policy",
    value: [
      "default-src 'self'",
      "img-src 'self' data: blob: https:",
      // Em dev o Next/Turbopack/React precisam de unsafe-eval para HMR
      `script-src 'self' 'unsafe-inline'${isProd ? "" : " 'unsafe-eval'"}`,
      "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com",
      // Next.js inlining de fontes usa data: URIs
      "font-src 'self' data: https://fonts.gstatic.com",
      // API + SignalR (ws) — origem da NEXT_PUBLIC_API_URL
      `connect-src 'self' ${apiOrigin} ${apiWs}${isProd ? "" : " ws://localhost:* http://localhost:*"}`,
      "frame-ancestors 'none'",
    ].join("; "),
  },
];

const nextConfig = {
  reactStrictMode: true,
  poweredByHeader: false,
  async headers() {
    return [
      {
        source: "/:path*",
        headers: securityHeaders,
      },
    ];
  },
};

export default nextConfig;
