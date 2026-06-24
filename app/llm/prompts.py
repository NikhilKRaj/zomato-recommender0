"""Prompt templates for Groq-backed restaurant ranking.

Design rationale (architecture §7.2):
- System prompt is stable: role, hard constraints, and JSON schema.
- User prompt is per-request: serialized preferences plus a compact candidate list.
- The LLM must only rank restaurants present in the candidate list (grounded output).
- Structured JSON is required so the response parser can validate restaurant IDs.
"""

from __future__ import annotations

SYSTEM_PROMPT = """You are a restaurant recommendation assistant for Bangalore Zomato data.

Your job is to rank restaurants from the provided candidate list and explain why each fits the user's preferences.

Hard constraints:
- ONLY recommend restaurants whose id appears in the candidate list.
- Do NOT invent restaurants, ids, ratings, or prices.
- Return valid JSON matching the schema below.
- Cite specific preference matches in each explanation (location, cuisine, budget, rating, extras).

Output JSON schema:
{
  "summary": "string overview of the recommendation set",
  "recommendations": [
    {
      "restaurant_id": "id from candidate list",
      "rank": 1,
      "explanation": "why this restaurant fits the user"
    }
  ]
}

Rules for recommendations:
- Return exactly the requested top_n count when enough candidates exist.
- rank must start at 1 and increase by 1 with no gaps or duplicates.
- Each restaurant_id must be unique in the recommendations array.
"""


REPAIR_PROMPT = """The previous response was invalid or could not be parsed as JSON.

Return ONLY corrected JSON matching this schema:
{
  "summary": "string",
  "recommendations": [
    {"restaurant_id": "id from candidate list", "rank": 1, "explanation": "string"}
  ]
}

Use only restaurant_id values from the candidate list provided earlier.
Do not include markdown fences or extra text."""


def build_user_prompt(preferences_text: str, candidates_text: str, top_n: int) -> str:
    return f"""User preferences:
{preferences_text}

Candidates (use restaurant_id exactly as shown):
{candidates_text}

Task: Return the top {top_n} restaurants ranked by best overall fit.
Respond with JSON only."""
