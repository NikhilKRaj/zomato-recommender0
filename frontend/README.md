# DineAI Frontend

React + Vite + TypeScript UI for the AI-powered restaurant recommendation service.

## Setup

```bash
cd frontend
npm install
```

## Development

Start the FastAPI backend first (from project root):

```bash
uvicorn app.main:app --reload
```

Then start the frontend dev server:

```bash
npm run dev
```

The Vite dev server proxies `/api` to `http://localhost:8000`.

## Environment

| Variable | Default | Description |
|----------|---------|-------------|
| `VITE_API_URL` | `/api` | API base URL (use full URL in production) |

Copy `.env.example` to `.env` if you need a custom API URL.

## Build

```bash
npm run build
npm run preview
```

## Stack

- React 18 + TypeScript + Vite
- Tailwind CSS (DineAI / Stitch design tokens)
- TanStack Query — API data fetching
- React Hook Form + Zod — form validation
- Material Symbols — icons (matches Stitch design)

## Design

UI follows the Stitch design in `stitch_dineai_restaurant_discovery/`:
- Zomato-inspired red accent (`#E23744`)
- Sticky preference form on desktop
- Recommendation cards **without food images**
- Location and cuisine as **dropdown selects** (populated from API metadata)
