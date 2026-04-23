# Garraf Property Monitor

FastAPI dashboard + Playwright scraping + OpenAI-compatible or Ollama LLM extraction. Stores deduplicated listings in SQLite, exports each run as CSV under `DATA_DIR/runs/`, and supports a URL blacklist.

## Comportamiento “universal” del LLM

Antes de cada scrape, la app **resuelve sola** la URL del endpoint OpenAI-compatible:

1. Toma la URL “principal” en este orden: variable de entorno `GPM_LLM_BASE_URL` (opcional) → valor guardado en **Config** → por defecto `https://api.openai.com/v1`.
2. Si es una API **HTTPS remota** (OpenAI, Groq, etc.), **solo** prueba esa URL.
3. Si es un caso **local / Ollama** (localhost, `127.0.0.1`, `host.docker.internal`, puerto típico 11434, etc.), **prueba varias variantes en secuencia** (p. ej. desde Docker: `127.0.0.1` → `host.docker.internal` → `172.17.0.1`) hasta que `GET /v1/models` responda bien.
4. El resultado se **cachea** unos minutos; al guardar **Config** se invalida la caché.

Así no hace falta acertar a la primera con la URL según si corres en bare metal, Docker, túnel SSH u Ollama en LAN. Si algo no responde, abre **`/api/llm-check`** en el navegador para ver el informe de intentos.

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

## Docker (red bridge, recomendado)

```bash
docker compose up --build
```

Compose incluye `extra_hosts: host.docker.internal:host-gateway` para Linux. Los datos van al volumen `gpm_data`.

### Si el túnel u Ollama solo escuchan en 127.0.0.1 del host

Desde la **red bridge** de Docker, una conexión al host **no es la misma** que “localhost” del proceso en el host: a veces hace falta enlazar el servicio en **`0.0.0.0:11434`** (túnel `ssh -N -L 0.0.0.0:11434:…` u `OLLAMA_HOST=0.0.0.0:11434` en Ollama). La resolución automática prueba `host.docker.internal` y el gateway Docker; si nada responde, usa **`/api/llm-check`** para ver el detalle.

### Alternativa: red del anfitrión (Linux)

```bash
docker compose -f docker-compose.host.yml up --build
```

La app queda en `http://127.0.0.1:8000` del host (sin `-p`). Ese fichero fija `GPM_LLM_BASE_URL=http://127.0.0.1:11434`.

## Environment

| Variable | Meaning |
|----------|---------|
| `GPM_DATA_DIR` | Directory for `app.db`, `runs/*.csv`, and `pw_profile/` (Playwright persistence). |
| `GPM_LLM_BASE_URL` | Optional. If set, it becomes the **primary** URL before automatic fallbacks (still useful in Kubernetes or CI). |

## API

- `POST /api/run` — optional JSON `{"portal_id": 1}` (long-running).
- `GET /api/llm-check` — same automatic URL resolution as the scraper; JSON report of candidates tried.

## Notes

- Idealista HTML changes often; the extractor targets `a[href*="/inmueble/"]`. Adjust Playwright selectors if the layout shifts.
- Automated scraping may conflict with site terms; use responsibly.
