# Edge Cases: AI-Powered Restaurant Recommendation System

This document catalogs **corner scenarios** for the Zomato-inspired restaurant recommendation service defined in [context.md](context.md) and [architecture.md](architecture.md). Each entry describes the scenario, the affected component, and the **expected system behavior**.

Use this as a test-design checklist during [implementation-plan.md](implementation-plan.md) Phases 1–6.

---

## Table of Contents

1. [Data Ingestion & Preprocessing](#1-data-ingestion--preprocessing)
2. [User Input & Validation](#2-user-input--validation)
3. [Preference Filtering](#3-preference-filtering)
4. [LLM Integration (Groq)](#4-llm-integration-groq)
5. [Recommendation Service & Orchestration](#5-recommendation-service--orchestration)
6. [API Layer](#6-api-layer)
7. [Fallback & Graceful Degradation](#7-fallback--graceful-degradation)
8. [User Interface](#8-user-interface)
9. [Security & Privacy](#9-security--privacy)
10. [Performance, Concurrency & Limits](#10-performance-concurrency--limits)
11. [Deployment & Operations](#11-deployment--operations)
12. [Cross-Cutting / End-to-End Scenarios](#12-cross-cutting--end-to-end-scenarios)

---

## Legend

| Field | Meaning |
|-------|---------|
| **ID** | Stable reference for tests and issues |
| **Severity** | `Critical` — wrong/missing results; `High` — degraded UX; `Medium` — recoverable; `Low` — cosmetic or rare |

---

## 1. Data Ingestion & Preprocessing

| ID | Scenario | Severity | Expected Behavior |
|----|----------|----------|-------------------|
| D-01 | Hugging Face download fails (network timeout, 503) | Critical | Fail startup with clear error; do not serve partial data. Document manual download fallback. |
| D-02 | Hugging Face dataset schema changes (column renamed/removed) | Critical | Preprocessor fails loudly with schema mismatch message; log missing columns. |
| D-03 | First run with no local cache | Medium | Download dataset, preprocess, write `data/processed/restaurants.parquet`, then load store. |
| D-04 | Corrupt or partial parquet cache | High | Detect read/validation failure; re-download or re-preprocess on next startup (or `force_refresh=True`). |
| D-05 | Empty dataset returned from Hugging Face | Critical | Abort startup; health check reports unhealthy data state. |
| D-06 | Duplicate rows (same name + address) | Medium | Deduplicate; keep row with higher votes or first occurrence; log count dropped. |
| D-07 | Duplicate restaurant names at different addresses | Low | Treat as distinct records; stable `restaurant_id` must differ (hash name+address). |
| D-08 | `rate` missing or empty string | Medium | Set `rating` to `null` or `0.0`; exclude from results when `min_rating > 0`. |
| D-09 | `rate` malformed (e.g. `"NEW"`, `"-"`, `"4.1"`, `"4.1 / 5"`) | High | Parse tolerant where possible; flag unparseable rows; log sample of failures. |
| D-10 | `rate` out of range (e.g. `"6.0/5"`, negative) | Medium | Clamp to 0–5 or drop row; log anomaly. |
| D-11 | `approx_cost(for two people)` missing | Medium | Set `cost_for_two` to `null`; exclude from budget filter or treat as unknown band. |
| D-12 | Cost as range string (e.g. `"300-400"`, `"300,400"`) | High | Parse to midpoint or lower bound consistently; document chosen rule. |
| D-13 | Cost with currency symbols or commas (`"₹1,200"`, `"1,200"`) | High | Strip non-numeric chars before parsing. |
| D-14 | Cost at exact band boundary (₹300, ₹600) | Medium | Apply documented rules: low ≤ 300, medium 301–600, high > 600. |
| D-15 | `cuisines` empty or whitespace only | Medium | Set `cuisines` to empty list; row won't match cuisine filter. |
| D-16 | `cuisines` with inconsistent casing/spacing (`"North Indian, Chinese "`) | Medium | Lowercase, trim, split on comma; normalize for matching. |
| D-17 | Multi-cuisine string with typos or aliases (`"Itallian"`) | Low | No fuzzy match at filter layer unless explicitly implemented; user sees no match. |
| D-18 | `online_order` / `book_table` not exactly `"Yes"` / `"No"` | Medium | Map known values; treat unknown as `false` or `null`; log unmapped values. |
| D-19 | Very long `reviews_list` or `dish_liked` fields | Low | Store full text in store; truncate only when building LLM prompt (≤ 100 chars). |
| D-20 | `listed_in(city)` vs `location` mismatch (city in one, neighbourhood in other) | High | Location filter checks **both** fields case-insensitively. |
| D-21 | User searches city name not in dataset (e.g. `"Delhi"`) | High | Filter returns empty; API 404 with suggestion to use metadata locations. |
| D-22 | Bangalore-only dataset vs examples mentioning other cities | Medium | Metadata and UI clarify available geography; no silent wrong results. |
| D-23 | `url` or `phone` missing | Low | Return `null` in API; UI hides link or shows "N/A". |
| D-24 | `votes` missing or zero | Low | Use `0` for fallback ranking; many ties possible at same rating. |
| D-25 | `force_refresh=True` while app is running | Medium | Reload store atomically or require restart; avoid serving half-updated data. |
| D-26 | Disk full when writing parquet cache | Critical | Fail with IO error; do not mark cache as valid. |
| D-27 | Row count drops below 90% after preprocessing | High | Log warning; continue if above minimum threshold; investigate in logs. |

---

## 2. User Input & Validation

| ID | Scenario | Severity | Expected Behavior |
|----|----------|----------|-------------------|
| U-01 | Missing required field (`location`, `budget`, or `cuisine`) | High | HTTP 400 with field-level validation errors (Pydantic). |
| U-02 | Invalid `budget` value (e.g. `"cheap"`, `"MEDIUM"`) | High | HTTP 400; accept only `low`, `medium`, `high` (normalize case if configured). |
| U-03 | `min_rating` below 0 or above 5 | High | HTTP 400; clamp or reject per schema (prefer reject with message). |
| U-04 | `min_rating` = 0 (explicit "any rating") | Low | Do not filter on rating; include restaurants with missing ratings if policy allows. |
| U-05 | `min_rating` = 5.0 | Medium | Very restrictive; may return empty set → 404 with broadening suggestion. |
| U-06 | `top_n` = 0 or negative | High | HTTP 400. |
| U-07 | `top_n` > 10 (schema max) | High | HTTP 400 or clamp to 10 per architecture. |
| U-08 | `top_n` greater than candidate count | Medium | Return all available candidates (≤ `top_n`); no padding with fake entries. |
| U-09 | Empty string for `location` or `cuisine` | High | HTTP 400 (treat as missing). |
| U-10 | Whitespace-only `location` / `cuisine` | High | Trim and reject if empty after trim. |
| U-11 | Location with special characters (`"Koramangala 5th Block"`) | Medium | Case-insensitive substring match against stored values. |
| U-12 | Cuisine partial match (`"Ital"`) | Medium | Substring match in normalized cuisine list (if that is the defined rule). |
| U-13 | Cuisine multi-select not in MVP (single string only) | Low | Only first cuisine used unless API extended; document limitation. |
| U-14 | `additional_preferences` empty string | Low | Omit from prompt or pass as none; no error. |
| U-15 | `additional_preferences` exceeds 500 characters | High | HTTP 400 from API; UI enforces max length client-side. |
| U-16 | `additional_preferences` with prompt injection attempt | High | Sanitize/limit length; system prompt instructs LLM to ignore override instructions; no tool execution. |
| U-17 | `additional_preferences` in non-English | Low | Pass through to LLM; ranking still grounded in candidate list. |
| U-18 | Conflicting preferences ("cheap" in text but `budget: high`) | Medium | Structured filters win for hard constraints; LLM may note conflict in explanation. |
| U-19 | Unicode / emoji in free text | Low | Accept if within length limit; UTF-8 throughout stack. |
| U-20 | SQL/script injection in text fields | High | No raw SQL from user input; pandas filtering only; escape in logs. |

---

## 3. Preference Filtering

| ID | Scenario | Severity | Expected Behavior |
|----|----------|----------|-------------------|
| F-01 | No restaurants match all filters | High | Empty candidate list → `NoCandidatesError` → HTTP 404 with message to relax filters. |
| F-02 | Only one restaurant matches | Medium | Pass single candidate to LLM; return 1 recommendation (not error). |
| F-03 | Thousands match (e.g. location only + low min_rating) | High | Pre-rank by `(rating, votes)`; cap at `MAX_CANDIDATES` (30) before LLM. |
| F-04 | All capped candidates have identical rating and votes | Medium | Stable tie-break (e.g. original index or name sort) for reproducibility. |
| F-05 | Location matches `city` but not `location` column | Medium | Still included (OR logic across fields). |
| F-06 | Location matches neighbourhood but user typed city name | Medium | Included if city field matches; document UX to use metadata dropdown. |
| F-07 | Cuisine filter on multi-tag restaurant (`"Italian, Pizza"`) | Low | Match if any tag contains cuisine substring. |
| F-08 | Budget filter excludes all high-rated options | Medium | Valid empty result; suggest raising budget or lowering min_rating. |
| F-09 | `min_rating` excludes rows with null rating | High | Rows with invalid/missing rating excluded when min_rating > 0. |
| F-10 | Optional filter: delivery requested but no `online_order` | Medium | Further narrows set; may cause empty result. |
| F-11 | Optional filter: table booking required | Medium | Same as F-10 for `book_table`. |
| F-12 | Keyword match on `rest_type` / `meal_type` ("family-friendly") | Medium | Case-insensitive keyword in additional preference parsing or filter extension. |
| F-13 | Keyword match false positive ("quick" matches "quick bites" and unrelated) | Low | Document matching rules; prefer explicit meal_type when possible. |
| F-14 | Filter order dependency | Low | Filters commutative for AND logic; order should not change result set. |
| F-15 | Case variation in location/cuisine (`"koramangala"`, `"ITALIAN"`) | Low | Case-insensitive matching throughout. |

---

## 4. LLM Integration (Groq)

| ID | Scenario | Severity | Expected Behavior |
|----|----------|----------|-------------------|
| L-01 | `GROQ_API_KEY` missing or empty | Critical | Clear error at LLM call time; fall back to rule-based ranker if configured. |
| L-02 | Invalid / revoked API key | High | Groq 401; catch and trigger fallback; log without exposing key. |
| L-03 | Groq rate limit (429) | High | Exponential backoff (limited retries); then fallback ranker. |
| L-04 | Groq timeout (`GROQ_TIMEOUT_SECONDS`) | High | Abort request; fallback ranker; `meta.source = "fallback"`. |
| L-05 | Groq 503 / service unavailable | High | Same as L-04. |
| L-06 | Response not valid JSON | High | Retry once with repair prompt; then fallback. |
| L-07 | JSON valid but wrong schema (missing `recommendations`) | High | Retry once; then fallback. |
| L-08 | LLM returns fewer than `top_n` items | Medium | Return what was validated; pad from fallback ranker for remaining slots **only from candidate set**. |
| L-09 | LLM returns duplicate `restaurant_id` in list | High | Deduplicate; keep highest rank; log warning. |
| L-10 | LLM hallucinates `restaurant_id` not in candidates | Critical | Reject invalid IDs; do not surface hallucinated restaurants. |
| L-11 | LLM returns valid IDs but wrong ranks (gaps, duplicates) | Medium | Re-normalize ranks 1..N after validation. |
| L-12 | LLM recommends restaurant that violates hard filter | Critical | Post-validation ensures ID ∈ candidates (already filter-compliant). |
| L-13 | LLM explanation contradicts data ("budget-friendly" for high-cost row) | Medium | Display explanation but data fields come from structured record, not LLM. |
| L-14 | Empty or generic explanations | Low | Still return recommendation; optional minimum length check for quality. |
| L-15 | `summary` field missing or null | Low | Return `summary: null` or omit; UI handles absence. |
| L-16 | Prompt exceeds model context / max tokens | High | Cap candidates at 30; truncate long fields; reduce prompt size; retry with smaller set if needed. |
| L-17 | `response_format: json_object` not supported by chosen model | High | Document compatible models; fail fast in config validation. |
| L-18 | Model returns markdown-wrapped JSON (` ```json `) | High | Strip fences before parse; retry if still invalid. |
| L-19 | Temperature too high → unstable rankings | Low | Default temperature 0.3 for reproducibility. |
| L-20 | Single candidate — LLM still asked to rank top 5 | Medium | Prompt and parser handle N < top_n; return 1 item. |
| L-21 | Repair prompt retry also fails | High | Fallback ranker; never return unvalidated LLM output. |
| L-22 | Groq returns truncated JSON (max tokens hit) | High | Treat as parse failure; retry or fallback. |
| L-23 | Network interruption mid-stream | High | Timeout + fallback. |

---

## 5. Recommendation Service & Orchestration

| ID | Scenario | Severity | Expected Behavior |
|----|----------|----------|-------------------|
| R-01 | Filter returns empty | High | Short-circuit; no LLM call; raise `NoCandidatesError`. |
| R-02 | LLM succeeds but all IDs fail validation | High | Full fallback ranker for top N from candidates. |
| R-03 | Partial LLM validation success (3 of 5 valid) | Medium | Return 3 LLM-ranked + fill remainder via fallback from remaining candidates. |
| R-04 | Merge LLM output with full restaurant record | Medium | API response uses store data for name, rating, cost — not LLM-invented values. |
| R-05 | Concurrent requests share same store | Medium | Read-only store after load; thread-safe or single-worker for MVP. |
| R-06 | Store not loaded yet (startup race) | Critical | `/recommend` returns 503 until lifespan startup completes. |
| R-07 | `meta.candidates_considered` accuracy | Low | Reflect pre-cap count or post-filter count consistently (document which). |
| R-08 | `meta.source` values | Low | `"llm"` or `"fallback"` always set correctly. |
| R-09 | `meta.model` when on fallback | Low | Null or last attempted model; document convention. |
| R-10 | Idempotent identical requests | Low | Same filters may yield slightly different LLM order; acceptable unless temperature=0. |

---

## 6. API Layer

| ID | Scenario | Severity | Expected Behavior |
|----|----------|----------|-------------------|
| A-01 | Malformed JSON body | High | HTTP 422/400 with parse error detail. |
| A-02 | Wrong Content-Type | Medium | Reject or attempt JSON parse with clear error. |
| A-03 | GET `/metadata/locations` before data load | High | 503 or empty list with warning — prefer 503 until ready. |
| A-04 | Metadata endpoints with huge lists (~hundreds cuisines) | Low | Return full list; consider pagination in future; UI may use search. |
| A-05 | `/health` when Groq key missing but data loaded | Low | Health OK for data path; LLM path degraded (document in response body optional). |
| A-06 | `/health` when dataset failed to load | Critical | Return unhealthy status (503). |
| A-07 | Oversized request body | Medium | Reject at size limit before processing. |
| A-08 | HTTP method not allowed | Low | 405 from FastAPI. |
| A-09 | Unknown route | Low | 404. |
| A-10 | Internal unhandled exception | High | HTTP 500; generic message to client; stack trace in logs only. |
| A-11 | OpenAPI `/docs` exposed in production | Low | Disable via config in production if required. |

---

## 7. Fallback & Graceful Degradation

| ID | Scenario | Severity | Expected Behavior |
|----|----------|----------|-------------------|
| G-01 | Fallback disabled and LLM fails | High | HTTP 503 per architecture (if fallback explicitly disabled). |
| G-02 | Fallback enabled (default) | High | Return rule-based ranking by `(rating, votes)` with generic or templated explanations. |
| G-03 | Fallback with tied ratings | Medium | Secondary sort by votes, then stable id. |
| G-04 | Fallback explanations quality | Low | Template: "Rated X/5 with Y votes; matches your filters." — not LLM prose. |
| G-05 | User notification on fallback | Medium | UI/API indicates `meta.source: "fallback"` so user knows AI reasoning unavailable. |
| G-06 | Intermittent Groq failures | High | Per-request fallback; do not crash process. |

---

## 8. User Interface

| ID | Scenario | Severity | Expected Behavior |
|----|----------|----------|-------------------|
| I-01 | Metadata API unreachable on page load | High | Show error banner; disable submit or use cached defaults with warning. |
| I-02 | Empty locations/cuisines metadata | High | Show "data unavailable"; link to troubleshooting. |
| I-03 | Submit while previous request in flight | Medium | Disable button / show spinner; ignore or cancel duplicate submit. |
| I-04 | API returns 404 (no matches) | High | Empty state: suggest relaxing location, cuisine, budget, or rating. |
| I-05 | API returns 400 validation error | High | Display field errors near form inputs. |
| I-06 | API returns 500 / network error | High | Friendly error message; retry option. |
| I-07 | Long AI explanation overflows card | Low | Scroll or truncate with "read more". |
| I-08 | Missing Zomato URL | Low | Hide external link button. |
| I-09 | Rating display for null rating | Low | Show "N/A" or "Unrated". |
| I-10 | Cost display for null cost | Low | Show "Price not available". |
| I-11 | Very long restaurant name or address | Low | Wrap text; no layout break. |
| I-12 | Fallback mode indicator | Medium | Badge or note when `meta.source === "fallback"`. |
| I-13 | User selects location not in dropdown (free text UI) | Medium | May 404; autocomplete from metadata preferred. |
| I-14 | Streamlit session refresh mid-request | Low | Lose in-flight state; user resubmits. |

---

## 9. Security & Privacy

| ID | Scenario | Severity | Expected Behavior |
|----|----------|----------|-------------------|
| S-01 | `GROQ_API_KEY` in logs or error traces | Critical | Never log secrets; redact in exception handlers. |
| S-02 | `.env` committed to git | Critical | Block via `.gitignore`; document in README. |
| S-03 | Raw `reviews_list` exposed in API | High | Omit by default (PII risk); only truncated snippets to LLM if needed. |
| S-04 | Phone numbers in public API | Medium | Omit or mask unless explicitly required. |
| S-05 | Prompt injection via `additional_preferences` | High | Length limit + system prompt hardening; no execution of embedded instructions. |
| S-06 | Abuse: high volume `/recommend` calls | Medium | Rate limit per IP in production; 429 response. |
| S-07 | CORS misconfiguration (if React SPA) | Medium | Restrict allowed origins in production. |

---

## 10. Performance, Concurrency & Limits

| ID | Scenario | Severity | Expected Behavior |
|----|----------|----------|-------------------|
| P-01 | Cold start: first HF download (~574 MB) | High | Document delay; show loading state; cache for subsequent runs. |
| P-02 | Memory pressure with full DataFrame (~51k rows) | Medium | Acceptable for MVP; monitor RSS; optional column pruning. |
| P-03 | 10+ concurrent `/recommend` requests | Medium | Target architecture NFR; queue or limit Groq concurrency if needed. |
| P-04 | Filter-only path latency | Low | < 200 ms for typical query on in-memory store. |
| P-05 | End-to-end p95 latency with Groq | Medium | Target < 5 s; log slow requests. |
| P-06 | Repeated identical metadata requests | Low | Cache locations/cuisines in memory; optional HTTP cache headers. |
| P-07 | LLM prompt token growth with max candidates | High | Stay within `GROQ_MAX_TOKENS`; enforce caps. |

---

## 11. Deployment & Operations

| ID | Scenario | Severity | Expected Behavior |
|----|----------|----------|-------------------|
| O-01 | Container start without baked parquet | High | Run preprocess at build time or first boot; avoid HF download every replica start. |
| O-02 | Missing `GROQ_API_KEY` in production | High | Service starts; recommendations use fallback only; alert ops. |
| O-03 | Docker health check before data ready | High | `/health` reflects readiness; orchestrator waits. |
| O-04 | Rolling deploy with in-memory store | Medium | Each instance loads dataset; no shared state required. |
| O-05 | Clock skew / timezone in logs | Low | Use UTC in structured logs. |
| O-06 | Dataset refresh in production | Medium | Rebuild image or run migration job; version parquet file. |
| O-07 | Groq model deprecation | Medium | Configurable `GROQ_MODEL`; document upgrade path. |

---

## 12. Cross-Cutting / End-to-End Scenarios

| ID | Scenario | Severity | Expected Behavior |
|----|----------|----------|-------------------|
| E-01 | **Happy path**: Koramangala + Italian + medium + rating ≥ 4 | — | Filter → LLM → 5 ranked cards with explanations and summary. |
| E-02 | **Over-constrained**: rare cuisine + high rating + low budget + niche location | High | 404 with helpful broadening hints, not LLM hallucination. |
| E-03 | **Under-constrained**: popular location only, min_rating 0 | Medium | Large match set capped to 30; LLM still ranks top 5. |
| E-04 | **Groq down, fallback on**: full user journey | High | User still gets 5 restaurants sorted by rating/votes; fallback flagged. |
| E-05 | **Delhi in problem statement examples, Bangalore in data** | Medium | No Delhi results unless in dataset; metadata drives UI options. |
| E-06 | **Same restaurant recommended twice** after dedup + validation | Critical | Must not happen in final API response. |
| E-07 | **Reproducibility test**: same input twice with temperature 0.3 | Low | Rankings may vary slightly; document as LLM non-determinism. |
| E-08 | **Full pipeline smoke test** without network (cached data, mock Groq) | — | CI runs with fixtures; no live API key required for unit tests. |
| E-09 | **Partial filter relaxation** (future): "expand search" | Low | Out of MVP scope; document as extension. |
| E-10 | **Accessibility**: screen reader on recommendation cards | Low | Semantic HTML; labels for rating and cost. |

---

## Test Priority Matrix

Use this order when building tests in Phase 6:

| Priority | IDs | Rationale |
|----------|-----|-----------|
| P0 | L-10, L-12, R-02, E-06, D-01, S-01 | Data integrity and no hallucinated restaurants |
| P1 | F-01, F-03, L-01–L-07, G-02, U-01–U-02, A-01 | Core request paths and failure modes |
| P2 | D-08–D-14, F-05–F-09, I-04–I-06, P-01 | Data quality and UX on errors |
| P3 | Remaining IDs | Polish, edge polish, operational |

---

## Mapping to Implementation Phases

| Phase | Primary edge-case sections |
|-------|----------------------------|
| Phase 1 | §1 Data Ingestion |
| Phase 2 | §3 Preference Filtering, parts of §2 |
| Phase 3 | §4 LLM Integration |
| Phase 4 | §5, §6, §7 |
| Phase 5 | §8 |
| Phase 6 | All sections — full test matrix |
| Phase 7 | §11 Deployment |

---

## Related Documents

- [context.md](context.md) — requirements and workflow
- [architecture.md](architecture.md) — component design and API contracts
- [implementation-plan.md](implementation-plan.md) — phase tasks and risk register

---

*Update this document when new components, filters, or LLM behaviors are added.*
