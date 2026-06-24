# DineAI — AI-Powered Restaurant Recommender

Zomato-inspired restaurant recommendation service for Bangalore. Users set preferences; the API filters real restaurant data and uses **Groq LLM** to rank options with explanations.

## Stack

| Layer | Technology |
|-------|------------|
| Backend | Python 3.11, FastAPI, pandas, Groq |
| Frontend | React 18, Vite, TypeScript, Tailwind |
| Data | [Hugging Face Zomato dataset](https://huggingface.co/datasets/ManikaSaini/zomato-restaurant-recommendation) |

## Local development

### Backend

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # add your GROQ_API_KEY
uvicorn app.main:app --reload
```

API: http://localhost:8000 · Docs: http://localhost:8000/docs

### Frontend

```bash
cd frontend
npm install
npm run dev
```

UI: http://localhost:5173

### Bake dataset (optional)

```bash
python scripts/bake_dataset.py
```

## Deployment

**Backend → Railway** · **Frontend → Vercel**

See **[deployment-plan.md](deployment-plan.md)** for step-by-step instructions.

Quick checklist:

1. Push to GitHub
2. Deploy backend on Railway (uses `railway.toml` + `Procfile`)
3. Set `GROQ_API_KEY` and `CORS_ORIGINS` on Railway
4. Deploy `frontend/` on Vercel with `VITE_API_URL=<railway-url>`

## Project structure

```
app/           # FastAPI backend
frontend/      # React SPA
scripts/       # Data validation & build helpers
tests/         # Backend tests
data/processed/  # Cached parquet (gitignored; baked on Railway build)
```

## Documentation

- [context.md](context.md) — requirements
- [architecture.md](architecture.md) — system design
- [implementation-plan.md](implementation-plan.md) — build phases
- [deployment-plan.md](deployment-plan.md) — Railway + Vercel deploy guide
