import type { VercelRequest, VercelResponse } from "@vercel/node";

function getBackendBaseUrl(): string | undefined {
  const base = process.env.RAILWAY_API_URL ?? process.env.VITE_API_URL;
  return base?.replace(/\/$/, "");
}

function buildTargetUrl(req: VercelRequest): string | null {
  const base = getBackendBaseUrl();
  if (!base) {
    return null;
  }

  const { path, ...query } = req.query;
  const pathSegments = Array.isArray(path) ? path : path ? [path] : [];
  const pathString = pathSegments.join("/");

  const params = new URLSearchParams();
  for (const [key, value] of Object.entries(query)) {
    if (value === undefined) {
      continue;
    }
    if (Array.isArray(value)) {
      for (const item of value) {
        params.append(key, item);
      }
      continue;
    }
    params.append(key, value);
  }

  const queryString = params.toString();
  return `${base}/${pathString}${queryString ? `?${queryString}` : ""}`;
}

export default async function handler(req: VercelRequest, res: VercelResponse) {
  const targetUrl = buildTargetUrl(req);
  if (!targetUrl) {
    res.status(502).json({
      detail:
        "Backend API URL is not configured. Set RAILWAY_API_URL in Vercel environment variables.",
    });
    return;
  }

  const headers: Record<string, string> = {
    "Content-Type": "application/json",
  };

  const init: RequestInit = {
    method: req.method,
    headers,
  };

  if (req.method && !["GET", "HEAD"].includes(req.method)) {
    init.body = req.body ? JSON.stringify(req.body) : undefined;
  }

  try {
    const upstream = await fetch(targetUrl, init);
    const contentType = upstream.headers.get("content-type") ?? "application/json";
    const body = await upstream.text();
    res.status(upstream.status).setHeader("Content-Type", contentType).send(body);
  } catch (error) {
    res.status(502).json({
      detail: `Failed to reach backend API: ${error instanceof Error ? error.message : String(error)}`,
    });
  }
}
