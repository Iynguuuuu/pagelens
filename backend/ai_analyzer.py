import os
import json
from groq import Groq


def get_client():
    return Groq(api_key=os.environ.get("GROQ_API_KEY"))


SYSTEM_PROMPT = """You are an expert web analyst specializing in SEO, conversion rate optimization, and UX for marketing websites.

You will receive:
1. Factual metrics scraped from a webpage (word count, headings, links, images, CTAs, meta tags)
2. The visible page text (truncated to ~3000 words)

Your job is to produce a structured JSON audit covering insights and prioritized recommendations.

RULES:
- Every insight MUST reference specific numbers from the metrics provided
- Be direct and specific — no vague or generic statements
- Insights must be grounded in the data, not assumptions
- Recommendations must be actionable and ranked by impact (1 = highest)

OUTPUT FORMAT — respond ONLY with valid JSON, no markdown fences, no explanation outside the JSON:

{
  "insights": {
    "seo_structure": {
      "score": "<Good | Needs Work | Poor>",
      "summary": "<2-3 sentence analysis referencing specific metrics>"
    },
    "messaging_clarity": {
      "score": "<Good | Needs Work | Poor>",
      "summary": "<2-3 sentence analysis>"
    },
    "cta_usage": {
      "score": "<Good | Needs Work | Poor>",
      "summary": "<2-3 sentence analysis>"
    },
    "content_depth": {
      "score": "<Good | Needs Work | Poor>",
      "summary": "<2-3 sentence analysis>"
    },
    "ux_concerns": {
      "score": "<Good | Needs Work | Poor>",
      "summary": "<2-3 sentence analysis>"
    }
  },
  "recommendations": [
    {
      "priority": 1,
      "title": "<Short title>",
      "reasoning": "<Why this matters, tied to specific metrics>",
      "action": "<Specific action to take>"
    }
  ]
}"""


def build_user_prompt(url: str, metrics: dict, page_text: str) -> str:
    return f"""Audit the following webpage: {url}

--- FACTUAL METRICS ---
{json.dumps(metrics, indent=2)}

--- PAGE CONTENT (first ~3000 words of visible text) ---
{page_text}

Produce the structured JSON audit now."""


def analyze_with_claude(url: str, metrics: dict, page_text: str) -> tuple[dict, dict]:
    client = get_client()
    user_prompt = build_user_prompt(url, metrics, page_text)

    completion = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        max_tokens=2048,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt}
        ]
    )

    raw_output = completion.choices[0].message.content.strip()

    
    if raw_output.startswith("```"):
        raw_output = raw_output.split("```")[1]
        if raw_output.startswith("json"):
            raw_output = raw_output[4:]
        raw_output = raw_output.strip()

    try:
        parsed = json.loads(raw_output)
    except json.JSONDecodeError:
        parsed = {
            "insights": {},
            "recommendations": [],
            "parse_error": "Model returned non-JSON output",
            "raw": raw_output
        }

    prompt_log = {
        "system_prompt": SYSTEM_PROMPT,
        "user_prompt": user_prompt,
        "model": "llama-3.3-70b-versatile",
        "max_tokens": 2048,
        "input_tokens": completion.usage.prompt_tokens,
        "output_tokens": completion.usage.completion_tokens,
        "raw_model_output": raw_output,
        "stop_reason": completion.choices[0].finish_reason
    }

    return parsed, prompt_log
