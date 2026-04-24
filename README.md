# Garraf Property Monitor

FastAPI dashboard + Playwright scraping + OpenAI-compatible or Ollama LLM extraction. Stores deduplicated listings in SQLite, exports each run as CSV under `DATA_DIR/runs/`, and supports a URL blacklist.

## Universal LLM behaviour

Before each scrape, the app **resolves** the OpenAI-compatible endpoint URL on its own:

1. It picks the “primary” URL in this order: environment variable `GPM_LLM_BASE_URL` (optional) → value stored in **Config** → default `https://api.openai.com/v1`.
2. For a **remote HTTPS** API (OpenAI, Groq, etc.), it **only** tries that URL.
3. For **local / Ollama** (localhost, `127.0.0.1`, `host.docker.internal`, typical port 11434, etc.), it **tries several variants in sequence** (e.g. from Docker: `127.0.0.1` → `host.docker.internal` → `172.17.0.1`) until `GET /v1/models` succeeds.
4. The result is **cached** for a few minutes; saving **Config** invalidates the cache.

You do not need to guess the right URL up front for bare metal, Docker, SSH tunnel, or LAN Ollama. If something does not respond, open **`/api/llm-check`** in the browser to see the attempt report.

## Run locally

```bash
cd /path/to/GlueProject
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pip install -r requirements-dev.txt  # tests only
python -m playwright install chromium
export GPM_DATA_DIR=./data
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Open http://localhost:8000 — configure LLM base URL, model, and API key under **Config**, then trigger **Ejecutar ahora** from **Ejecuciones** or the home page (UI labels are in Spanish).

## Docker (bridge network, recommended)

```bash
docker compose up --build
```

Compose adds `extra_hosts: host.docker.internal:host-gateway` for Linux. Data is stored in the `gpm_data` volume.

### If the tunnel or Ollama only listens on the host’s 127.0.0.1

From Docker’s **bridge** network, reaching the host is **not** the same as the host process’s “localhost”: you may need the service bound to **`0.0.0.0:11434`** (tunnel `ssh -N -L 0.0.0.0:11434:…` or `OLLAMA_HOST=0.0.0.0:11434` for Ollama). Automatic resolution tries `host.docker.internal` and the Docker gateway; if nothing responds, use **`/api/llm-check`** for details.

### Alternative: host network (Linux)

```bash
docker compose -f docker-compose.host.yml up --build
```

The app is at `http://127.0.0.1:8000` on the host (no `-p`). That file sets `GPM_LLM_BASE_URL=http://127.0.0.1:11434`.

## Environment

| Variable | Meaning |
|----------|---------|
| `GPM_DATA_DIR` | Directory for `app.db`, `runs/*.csv`, and `pw_profile/` (Playwright persistence). |
| `GPM_LLM_BASE_URL` | Optional. If set, it becomes the **primary** URL before automatic fallbacks (still useful in Kubernetes or CI). |
| `GPM_CRAWL4AI_PAGE_TIMEOUT_MS` | Optional. Page timeout for the **Crawl4AI** listing strategy (default `90000`). |
| `GPM_LISTING_AGENT_MAX_STEPS` | Reserved for a future browser-agent mode (default `0`, unused). |

## Listing strategies (global, under Config)

Under **Settings** (`/config`), **Listing strategy** applies to every portal:

- **static** (default): the app’s persistent **Playwright** profile runs fixed JS/CSS-style extraction (e.g. Idealista `/inmueble/` links).
- **crawl4ai**: a **second** headless Chromium is started by [Crawl4AI](https://docs.crawl4ai.com/) for each portal URL; listing URLs are discovered with regex. Heavier on RAM/CPU.
- **agent_experimental**: **not implemented** in the default image; see `requirements-agent.txt` and [`app/scraper/agent_listing.py`](app/scraper/agent_listing.py).

**Portals** (`/portals`) store only **name**, **search URL**, and **enabled**. Each run processes **enabled** portals **in ID order** (one URL after another). Listing strategy and the **LLM extraction prompt** live in **Config**.

The **LLM** still receives snippets from the chosen strategy; it does **not** browse by itself (same pattern as [llm-web-scrapper](https://huggingface.co/spaces/frkhan/llm-web-scrapper): scrape first, then LLM).

## Models (Ollama / local) and expectations

- No open-weight model “is Perplexity”: **live browsing** needs an **agent loop** (observe page → model proposes actions → Playwright executes) or an API like Firecrawl/Crawl4AI to fetch content first.
- For **structured JSON** after the page text is available, smaller instruct models often work better when prompts are explicit; many teams use **Qwen 2.5 / 3**, **Llama 3.x**, or similar sizes that fit your GPU/RAM. Check [ollama.com/library](https://ollama.com/library) and model cards on **Hugging Face** for licenses and context limits.
- If a model **refuses** (“I cannot browse”), it is usually answering the wrong mental model: remind it (system prompt) that **snippets are already in the user message**—the app does that in seed defaults for new DBs.

## Legal / ToS

Automated access may conflict with a site’s terms or `robots.txt`. **Crawl4AI** and any future agent mode increase traffic and fingerprint surface; use only where you have permission and acceptable rate limits.

## API

- `POST /api/run` — optional JSON `{"portal_id": 1}` (long-running).
- `GET /api/llm-check` — same automatic URL resolution as the scraper; JSON report of candidates tried.

## Notes

- Idealista HTML changes often; the extractor targets `a[href*="/inmueble/"]`. Adjust Playwright selectors if the layout shifts.
- Automated scraping may conflict with site terms; use responsibly.
