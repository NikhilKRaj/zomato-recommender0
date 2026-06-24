import { writeFileSync } from "node:fs";
import { resolve } from "node:path";

const apiUrl = (process.env.RAILWAY_API_URL ?? process.env.VITE_API_URL ?? "")
  .trim()
  .replace(/\/$/, "");

const rewrites = [];

if (apiUrl) {
  rewrites.push({
    source: "/api/:path*",
    destination: `${apiUrl}/:path*`,
  });
  console.log(`[vercel] Proxy /api/* -> ${apiUrl}`);
} else {
  console.warn(
    "[vercel] RAILWAY_API_URL is not set; /api proxy rewrite will be omitted.",
  );
}

rewrites.push({
  source: "/((?!api/).*)",
  destination: "/index.html",
});

const config = { rewrites };
const outputPath = resolve(import.meta.dirname, "..", "vercel.json");
writeFileSync(outputPath, `${JSON.stringify(config, null, 2)}\n`);
console.log(`[vercel] Wrote ${outputPath}`);
