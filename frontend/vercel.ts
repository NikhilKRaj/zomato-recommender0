const railwayApiUrl = (
  process.env.RAILWAY_API_URL ??
  process.env.VITE_API_URL ??
  "https://web-production-0c816.up.railway.app"
).replace(/\/$/, "");

/** @type {import('@vercel/config').VercelConfig} */
const config = {
  rewrites: [
    {
      source: "/api/:path*",
      destination: `${railwayApiUrl}/:path*`,
    },
    {
      source: "/(.*)",
      destination: "/index.html",
    },
  ],
};

export default config;
