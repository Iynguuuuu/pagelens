# PageLens — AI-Powered Website Audit Tool

> Built for Eight25Media's AI-Native Software Engineer assessment.

**Live Demo:** `https://pagelens.vercel.app` *(update after deploy)*  
**Backend API:** `https://pagelens-api.onrender.com` *(update after deploy)*

---

## What It Does

Paste a URL → get a two-layer audit in seconds:

1. **Factual Metrics** — scraped deterministically (no AI): word count, headings, CTAs, links, images, alt text %, meta tags
2. **AI Insights** — Claude analyzes the metrics + page text and returns structured JSON covering SEO, messaging, CTAs, content depth, and UX
3. **Prioritized Recommendations** — 3–5 ranked, actionable items tied to actual numbers

---

## Architecture

```
[React Frontend]
      │  POST /audit { url }
      ▼
[Flask Backend]
  ├── scraper.py        → BeautifulSoup extracts metrics + visible text
  ├── ai_analyzer.py    → Builds prompts, calls Claude API, parses JSON output
  ├── logger.py         → Saves full prompt log (system prompt, user prompt, raw output)
  └── app.py            → Orchestrates scrape → analyze → respond
      │
      ▼
[Anthropic Claude API]  (claude-opus-4-5, structured JSON output)
```

**Key design decision: clean separation.**  
`scraper.py` is pure Python/BeautifulSoup — zero AI.  
`ai_analyzer.py` is pure AI — zero scraping.  
They communicate via a typed metrics dict. This makes each layer independently testable and replaceable.

---

## AI Design Decisions

### Structured Output via System Prompt
Rather than asking Claude to produce freeform text, the system prompt specifies an exact JSON schema. Claude is instructed to return **only** valid JSON — no markdown fences, no preamble. This avoids fragile regex parsing and makes the output directly usable by the frontend.

### Metrics-Grounded Insights
The user prompt embeds the full metrics JSON alongside the page text. The system prompt explicitly requires every insight to **reference specific numbers**. This prevents generic AI output like "your content could be improved" — instead Claude says "with only 1 H1 and 312 words, the page lacks the depth expected for competitive SERPs."

### Token Efficiency
Page text is capped at ~3,000 words before being sent to the model. This keeps input tokens predictable and cost-efficient while giving Claude enough content to assess messaging clarity and content depth meaningfully.

### Prompt Logging
Every API call is logged to `prompt_logs.json` with: system prompt, constructed user prompt, raw model output (pre-parse), token counts, and stop reason. The `/logs` endpoint exposes these. This gives full visibility into the AI layer.

---

## Trade-offs

| Decision | Trade-off |
|---|---|
| BeautifulSoup scraper | Fast and simple, but JS-rendered pages (SPAs) won't be fully scraped. Playwright would handle these but adds complexity. |
| Claude structured JSON output | Reliable schema, but occasionally the model adds markdown fences — handled with a strip step. |
| 3000-word page text cap | Keeps tokens/cost low, but very long pages lose tail content. Chunking + summarization would be the next step. |
| Flask + Render | Simple deployment, but cold starts on Render's free tier can add ~30s to first request. |
| Single-page audit only | Matches the spec and keeps the tool focused. Multi-page crawling would need a queue system. |

---

## What I'd Improve With More Time

1. **Playwright integration** — render JS-heavy SPAs before scraping
2. **Scoring dashboard** — an overall 0–100 score aggregated from all insight categories
3. **Historical comparisons** — re-audit the same URL and diff the results over time
4. **PDF export** — one-click audit report download
5. **Streaming AI responses** — show insights as they arrive rather than waiting for full completion
6. **Rate limiting + caching** — avoid re-scraping the same URL within a short window

---

## Local Setup

### Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt

cp .env.example .env
# Add your ANTHROPIC_API_KEY to .env

python app.py
# → Running on http://localhost:5000
```

### Frontend

```bash
cd frontend
npm install

cp .env.example .env
# VITE_API_URL=http://localhost:5000

npm run dev
# → http://localhost:5173
```

---

## Deployment

### Backend → Render

1. Create a new **Web Service** on [render.com](https://render.com)
2. Connect your GitHub repo, set root directory to `backend/`
3. Build command: `pip install -r requirements.txt`
4. Start command: `gunicorn app:app --bind 0.0.0.0:$PORT --workers 2 --timeout 60`
5. Add environment variable: `ANTHROPIC_API_KEY=sk-ant-...`

### Frontend → Vercel

1. Import repo on [vercel.com](https://vercel.com)
2. Set root directory to `frontend/`
3. Add environment variable: `VITE_API_URL=https://your-render-url.onrender.com`
4. Deploy

---

## API Reference

### `POST /audit`
```json
{ "url": "https://example.com" }
```
Returns metrics, AI insights, recommendations, and a log ID.

### `GET /logs`
Returns all prompt logs (system prompts, user prompts, raw model outputs).

### `GET /logs/:log_id`
Returns a single prompt log by ID.

---

## Prompt Logs

All prompt logs are stored in `backend/prompt_logs.json` and exposed via the `/logs` endpoint.

Each log contains:
- `system_prompt` — the full system prompt sent to Claude
- `user_prompt` — the constructed user prompt including metrics JSON and page text
- `raw_model_output` — Claude's response before JSON parsing
- `input_tokens` / `output_tokens` — token usage
- `stop_reason` — why the model stopped generating

See `prompt_logs_sample.json` in the repo root for an example.