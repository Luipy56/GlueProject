# Garraf Property Monitor

FastAPI dashboard + Playwright scraping + OpenAI-compatible or Ollama LLM extraction. Stores deduplicated listings in SQLite, exports each run as CSV under `DATA_DIR/runs/`, and supports a URL blacklist.

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

Open http://localhost:8000 — configure LLM base URL, model, and API key under **Config**, then trigger **Ejecutar ahora** from **Ejecuciones** or the home page.

## Docker

```bash
docker compose up --build
```

Data (SQLite, Chromium profile, CSVs) persists in the `gpm_data` volume.

Compose sets `extra_hosts: host.docker.internal:host-gateway` and **`GPM_LLM_BASE_URL=http://host.docker.internal:11434`** so the app reaches Ollama (or your SSH tunnel) on the host. That variable **overrides** the Base URL stored in the UI database for LLM calls only. Change the port in `docker-compose.yml` if your tunnel listens elsewhere.

`http://127.0.0.1:11434` inside the container is not your laptop; use `host.docker.internal` or publish Ollama in the same compose stack.

## Environment

| Variable | Meaning |
|----------|---------|
| `GPM_DATA_DIR` | Directory for `app.db`, `runs/*.csv`, and `pw_profile/` (Playwright persistence). |
| `GPM_LLM_BASE_URL` | Optional. If set, overrides stored `llm_base_url` for OpenAI-compatible requests (e.g. Ollama on the host from Docker). |

## API

`POST /api/run` with optional JSON `{"portal_id": 1}` to run a scrape asynchronously within the request (can be long-running).

## Notes

- Idealista HTML changes often; the extractor targets `a[href*="/inmueble/"]`. Adjust Playwright selectors if the layout shifts.
- Automated scraping may conflict with site terms; use responsibly.
