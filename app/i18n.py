"""UI translations (es / en / de). No runtime gettext dependency."""

from __future__ import annotations

from typing import Any, Protocol


class RequestLike(Protocol):
    """Minimal request shape for locale detection (Starlette/FastAPI Request)."""

    query_params: Any
    cookies: Any
    headers: Any
    url: Any


LOCALES = frozenset({"es", "en", "de"})
DEFAULT_LOCALE = "es"

MESSAGES: dict[str, dict[str, str]] = {
    "es": {
        "nav.listings": "Listados",
        "nav.runs": "Ejecuciones",
        "nav.portals": "Portales",
        "nav.config": "Config",
        "nav.blacklist": "Blacklist",
        "nav.lang.es": "Castellano",
        "nav.lang.en": "English",
        "nav.lang.de": "Deutsch",
        "nav.version_title": "Versión desplegada",
        "nav.version_label": "Versión",
        "nav.theme_aria_dark": "Cambiar a tema oscuro",
        "nav.theme_aria_light": "Cambiar a tema claro",
        "js.submitting": "Ejecutando… (varios minutos)",
        "index.title": "Listados · Garraf Monitor",
        "index.h1": "Listados",
        "index.interval": "Intervalo configurado",
        "index.model": "Modelo",
        "index.last_ok": "Último scraping OK",
        "index.no_ok_runs": "Aún no hay ejecuciones correctas.",
        "index.filter": "Filtro",
        "index.view_all": "Ver todos",
        "index.only_last_ok": "Solo última ejecución OK",
        "index.run_now": "Ejecutar ahora",
        "th.portal": "Portal",
        "th.title": "Título",
        "th.price": "Precio",
        "th.m2": "m²",
        "th.phone": "Teléfono",
        "th.seller": "Vendedor",
        "th.url": "URL",
        "common.open": "abrir",
        "common.blacklist": "Blacklist",
        "index.blacklist_title": "Ocultar",
        "index.empty": "Sin datos todavía. Ejecuta un scraping desde «Ejecuciones».",
        "config.title": "Config · Garraf Monitor",
        "config.h1": "Configuración",
        "config.intro": (
            "La app elige sola una URL alineada al entorno (Docker, túnel, LAN, cloud): "
            "prueba varias direcciones en orden hasta que Ollama/API responda en `/v1/models`. "
            "Opcional: `GPM_LLM_BASE_URL` en el entorno tiene prioridad sobre el campo de abajo."
        ),
        "config.llm_env_title": "LLM vía variable de entorno",
        "config.llm_env_body": (
            "`GPM_LLM_BASE_URL` está definida y tiene prioridad sobre el valor guardado en la base de datos. "
            "Valor efectivo mostrado:"
        ),
        "config.scheduler_interval": "Intervalo scheduler (horas)",
        "config.llm_provider": "Proveedor LLM",
        "config.opt_openai": "OpenAI-compatible (remoto)",
        "config.opt_ollama": "Ollama (local, API /v1)",
        "config.base_url": "Base URL API",
        "config.base_url_help_effective": "Valor efectivo ahora para el LLM:",
        "config.base_url_suffix": "(se añade `/v1` automáticamente si falta).",
        "config.base_url_local_hint": (
            "En local con Ollama: `http://127.0.0.1:11434`. En Docker sin variable de entorno, usa "
            "`http://host.docker.internal:11434`."
        ),
        "config.test_link": "Probar conexión (/api/llm-check)",
        "config.api_key": "API key (vacío para Ollama local)",
        "config.model": "Modelo",
        "config.temperature": "Temperature",
        "config.system_prompt": "System prompt (extracción JSON)",
        "config.save": "Guardar",
        "runs.title": "Ejecuciones · Garraf Monitor",
        "runs.h1": "Historial de scrapings",
        "runs.banner_ok_title": "Listo",
        "runs.error_title": "Error",
        "runs.error_hint": "Motivo guardado para esta ejecución (revisa también la columna «Detalle» en la tabla).",
        "runs.manual_hint": (
            "Disparo manual (misma lógica que el scheduler). Solo una ejecución a la vez: "
            "el botón se desactiva al enviar."
        ),
        "runs.portal_optional": "Portal (opcional)",
        "runs.portal_placeholder": "ID numérico o vacío = todos",
        "th.id": "ID",
        "th.start": "Inicio",
        "th.end": "Fin",
        "th.status": "Estado",
        "th.new": "Nuevos",
        "th.updated": "Actualizados",
        "th.csv": "CSV",
        "th.detail": "Detalle / error",
        "runs.download": "descargar",
        "runs.no_message": "(sin mensaje)",
        "runs.empty": "Sin ejecuciones.",
        "portals.title": "Portales · Garraf Monitor",
        "portals.h1": "Portales",
        "portals.add_title": "Añadir portal",
        "label.name": "Nombre",
        "label.search_url": "URL de búsqueda",
        "label.prompt_template": "Plantilla de instrucciones (portal)",
        "portals.fetch_phone": "Abrir detalle para teléfono (Idealista)",
        "portals.create": "Crear",
        "portals.disabled": "(desactivado)",
        "label.url": "URL",
        "label.instructions": "Instrucciones",
        "portals.detail_phone": "Detalle teléfono",
        "portals.active": "Activo",
        "portals.delete_confirm": "¿Borrar portal y sus listados asociados?",
        "portals.delete": "Eliminar",
        "portals.none": "No hay portales.",
        "blacklist.title": "Blacklist · Garraf Monitor",
        "blacklist.h1": "Blacklist",
        "blacklist.intro": (
            "Patrón: URL canónica exacta o prefijo. Oculta en el listado y omite en futuros merges."
        ),
        "label.pattern": "Patrón",
        "label.note_optional": "Nota (opcional)",
        "blacklist.add": "Añadir",
        "th.note": "Nota",
        "th.created": "Creado",
        "blacklist.remove": "Quitar",
        "blacklist.empty": "Vacío.",
        "runs.not_found": "No se encontró la ejecución #{id}.",
        "runs.failed_no_message": (
            "La ejecución terminó en estado «failed» pero no hay mensaje de error guardado."
        ),
        "runs.success_done": (
            "Ejecución #{id} correcta: {new} anuncios nuevos, {updated} actualizados."
        ),
        "run_now.busy": (
            "Ya hay una ejecución en curso. Espera a que termine o revisa la tabla de ejecuciones."
        ),
        "base.default_title": "Garraf Monitor",
    },
    "en": {
        "nav.listings": "Listings",
        "nav.runs": "Runs",
        "nav.portals": "Portals",
        "nav.config": "Settings",
        "nav.blacklist": "Blacklist",
        "nav.lang.es": "Spanish",
        "nav.lang.en": "English",
        "nav.lang.de": "German",
        "nav.version_title": "Deployed version",
        "nav.version_label": "Version",
        "nav.theme_aria_dark": "Switch to dark theme",
        "nav.theme_aria_light": "Switch to light theme",
        "js.submitting": "Running… (several minutes)",
        "index.title": "Listings · Garraf Monitor",
        "index.h1": "Listings",
        "index.interval": "Scheduled interval",
        "index.model": "Model",
        "index.last_ok": "Last successful scrape",
        "index.no_ok_runs": "No successful runs yet.",
        "index.filter": "Filter",
        "index.view_all": "Show all",
        "index.only_last_ok": "Last successful run only",
        "index.run_now": "Run now",
        "th.portal": "Portal",
        "th.title": "Title",
        "th.price": "Price",
        "th.m2": "m²",
        "th.phone": "Phone",
        "th.seller": "Seller",
        "th.url": "URL",
        "common.open": "open",
        "common.blacklist": "Blacklist",
        "index.blacklist_title": "Hide",
        "index.empty": "No data yet. Run a scrape from “Runs”.",
        "config.title": "Settings · Garraf Monitor",
        "config.h1": "Settings",
        "config.intro": (
            "The app automatically picks a URL suited to the environment (Docker, tunnel, LAN, cloud): "
            "it tries several addresses in order until Ollama/the API responds at `/v1/models`. "
            "Optional: `GPM_LLM_BASE_URL` in the environment overrides the field below."
        ),
        "config.llm_env_title": "LLM via environment variable",
        "config.llm_env_body": (
            "`GPM_LLM_BASE_URL` is set and overrides the value stored in the database. "
            "Effective value shown:"
        ),
        "config.scheduler_interval": "Scheduler interval (hours)",
        "config.llm_provider": "LLM provider",
        "config.opt_openai": "OpenAI-compatible (remote)",
        "config.opt_ollama": "Ollama (local, /v1 API)",
        "config.base_url": "API base URL",
        "config.base_url_help_effective": "Effective value for the LLM right now:",
        "config.base_url_suffix": "(`/v1` is added automatically if missing).",
        "config.base_url_local_hint": (
            "Local Ollama: `http://127.0.0.1:11434`. In Docker without the env var, use "
            "`http://host.docker.internal:11434`."
        ),
        "config.test_link": "Test connection (/api/llm-check)",
        "config.api_key": "API key (empty for local Ollama)",
        "config.model": "Model",
        "config.temperature": "Temperature",
        "config.system_prompt": "System prompt (JSON extraction)",
        "config.save": "Save",
        "runs.title": "Runs · Garraf Monitor",
        "runs.h1": "Scrape history",
        "runs.banner_ok_title": "Done",
        "runs.error_title": "Error",
        "runs.error_hint": "Stored reason for this run (also check the “Detail” column in the table).",
        "runs.manual_hint": (
            "Manual trigger (same logic as the scheduler). Only one run at a time: "
            "the button disables on submit."
        ),
        "runs.portal_optional": "Portal (optional)",
        "runs.portal_placeholder": "Numeric ID or empty = all",
        "th.id": "ID",
        "th.start": "Start",
        "th.end": "End",
        "th.status": "Status",
        "th.new": "New",
        "th.updated": "Updated",
        "th.csv": "CSV",
        "th.detail": "Detail / error",
        "runs.download": "download",
        "runs.no_message": "(no message)",
        "runs.empty": "No runs.",
        "portals.title": "Portals · Garraf Monitor",
        "portals.h1": "Portals",
        "portals.add_title": "Add portal",
        "label.name": "Name",
        "label.search_url": "Search URL",
        "label.prompt_template": "Portal instruction template",
        "portals.fetch_phone": "Open detail for phone (Idealista)",
        "portals.create": "Create",
        "portals.disabled": "(disabled)",
        "label.url": "URL",
        "label.instructions": "Instructions",
        "portals.detail_phone": "Phone detail",
        "portals.active": "Enabled",
        "portals.delete_confirm": "Delete this portal and its associated listings?",
        "portals.delete": "Delete",
        "portals.none": "No portals.",
        "blacklist.title": "Blacklist · Garraf Monitor",
        "blacklist.h1": "Blacklist",
        "blacklist.intro": (
            "Pattern: exact canonical URL or prefix. Hides in listings and skips in future merges."
        ),
        "label.pattern": "Pattern",
        "label.note_optional": "Note (optional)",
        "blacklist.add": "Add",
        "th.note": "Note",
        "th.created": "Created",
        "blacklist.remove": "Remove",
        "blacklist.empty": "Empty.",
        "runs.not_found": "Run #{id} was not found.",
        "runs.failed_no_message": "The run ended as “failed” but no error message was stored.",
        "runs.success_done": "Run #{id} succeeded: {new} new listings, {updated} updated.",
        "run_now.busy": "A scrape is already running. Wait for it to finish or check the runs table.",
        "base.default_title": "Garraf Monitor",
    },
    "de": {
        "nav.listings": "Inserate",
        "nav.runs": "Läufe",
        "nav.portals": "Portale",
        "nav.config": "Einstellungen",
        "nav.blacklist": "Blacklist",
        "nav.lang.es": "Spanisch",
        "nav.lang.en": "Englisch",
        "nav.lang.de": "Deutsch",
        "nav.version_title": "Bereitgestellte Version",
        "nav.version_label": "Version",
        "nav.theme_aria_dark": "Zum dunklen Design wechseln",
        "nav.theme_aria_light": "Zum hellen Design wechseln",
        "js.submitting": "Läuft… (einige Minuten)",
        "index.title": "Inserate · Garraf Monitor",
        "index.h1": "Inserate",
        "index.interval": "Geplantes Intervall",
        "index.model": "Modell",
        "index.last_ok": "Letzter erfolgreicher Scrape",
        "index.no_ok_runs": "Noch keine erfolgreichen Läufe.",
        "index.filter": "Filter",
        "index.view_all": "Alle anzeigen",
        "index.only_last_ok": "Nur letzter erfolgreicher Lauf",
        "index.run_now": "Jetzt ausführen",
        "th.portal": "Portal",
        "th.title": "Titel",
        "th.price": "Preis",
        "th.m2": "m²",
        "th.phone": "Telefon",
        "th.seller": "Anbieter",
        "th.url": "URL",
        "common.open": "öffnen",
        "common.blacklist": "Blacklist",
        "index.blacklist_title": "Ausblenden",
        "index.empty": "Noch keine Daten. Starte einen Scrape unter «Läufe».",
        "config.title": "Einstellungen · Garraf Monitor",
        "config.h1": "Einstellungen",
        "config.intro": (
            "Die App wählt automatisch eine zur Umgebung passende URL (Docker, Tunnel, LAN, Cloud): "
            "Sie probiert mehrere Adressen nacheinander, bis Ollama/die API unter `/v1/models` antwortet. "
            "Optional: `GPM_LLM_BASE_URL` in der Umgebung hat Vorrang vor dem Feld unten."
        ),
        "config.llm_env_title": "LLM über Umgebungsvariable",
        "config.llm_env_body": (
            "`GPM_LLM_BASE_URL` ist gesetzt und hat Vorrang vor dem in der Datenbank gespeicherten Wert. "
            "Angezeigter effektiver Wert:"
        ),
        "config.scheduler_interval": "Scheduler-Intervall (Stunden)",
        "config.llm_provider": "LLM-Anbieter",
        "config.opt_openai": "OpenAI-kompatibel (remote)",
        "config.opt_ollama": "Ollama (lokal, /v1-API)",
        "config.base_url": "API-Basis-URL",
        "config.base_url_help_effective": "Aktueller effektiver Wert für das LLM:",
        "config.base_url_suffix": "(`/v1` wird bei Bedarf automatisch ergänzt).",
        "config.base_url_local_hint": (
            "Lokal mit Ollama: `http://127.0.0.1:11434`. In Docker ohne Umgebungsvariable: "
            "`http://host.docker.internal:11434`."
        ),
        "config.test_link": "Verbindung testen (/api/llm-check)",
        "config.api_key": "API-Schlüssel (leer für lokales Ollama)",
        "config.model": "Modell",
        "config.temperature": "Temperature",
        "config.system_prompt": "System-Prompt (JSON-Extraktion)",
        "config.save": "Speichern",
        "runs.title": "Läufe · Garraf Monitor",
        "runs.h1": "Scrape-Verlauf",
        "runs.banner_ok_title": "Fertig",
        "runs.error_title": "Fehler",
        "runs.error_hint": (
            "Gespeicherter Grund für diesen Lauf (siehe auch Spalte «Detail» in der Tabelle)."
        ),
        "runs.manual_hint": (
            "Manueller Start (gleiche Logik wie der Scheduler). Nur ein Lauf gleichzeitig: "
            "Der Button wird beim Absenden deaktiviert."
        ),
        "runs.portal_optional": "Portal (optional)",
        "runs.portal_placeholder": "Numerische ID oder leer = alle",
        "th.id": "ID",
        "th.start": "Start",
        "th.end": "Ende",
        "th.status": "Status",
        "th.new": "Neu",
        "th.updated": "Aktualisiert",
        "th.csv": "CSV",
        "th.detail": "Detail / Fehler",
        "runs.download": "herunterladen",
        "runs.no_message": "(keine Meldung)",
        "runs.empty": "Keine Läufe.",
        "portals.title": "Portale · Garraf Monitor",
        "portals.h1": "Portale",
        "portals.add_title": "Portal hinzufügen",
        "label.name": "Name",
        "label.search_url": "Such-URL",
        "label.prompt_template": "Instruktionsvorlage (Portal)",
        "portals.fetch_phone": "Detail für Telefon öffnen (Idealista)",
        "portals.create": "Anlegen",
        "portals.disabled": "(deaktiviert)",
        "label.url": "URL",
        "label.instructions": "Anweisungen",
        "portals.detail_phone": "Telefon-Detail",
        "portals.active": "Aktiv",
        "portals.delete_confirm": "Dieses Portal und zugehörige Inserate löschen?",
        "portals.delete": "Löschen",
        "portals.none": "Keine Portale.",
        "blacklist.title": "Blacklist · Garraf Monitor",
        "blacklist.h1": "Blacklist",
        "blacklist.intro": (
            "Muster: exakte kanonische URL oder Präfix. Wird in der Liste ausgeblendet und bei "
            "künftigen Merges übersprungen."
        ),
        "label.pattern": "Muster",
        "label.note_optional": "Notiz (optional)",
        "blacklist.add": "Hinzufügen",
        "th.note": "Notiz",
        "th.created": "Erstellt",
        "blacklist.remove": "Entfernen",
        "blacklist.empty": "Leer.",
        "runs.not_found": "Lauf #{id} wurde nicht gefunden.",
        "runs.failed_no_message": (
            "Der Lauf endete mit «failed», aber es wurde keine Fehlermeldung gespeichert."
        ),
        "runs.success_done": (
            "Lauf #{id} erfolgreich: {new} neue Inserate, {updated} aktualisiert."
        ),
        "run_now.busy": (
            "Es läuft bereits ein Scrape. Warte bis zum Ende oder prüfe die Lauf-Tabelle."
        ),
        "base.default_title": "Garraf Monitor",
    },
}


def resolve_locale(request: RequestLike) -> str:
    q = (request.query_params.get("lang") or "").strip().lower()
    if q in LOCALES:
        return q
    cookie = (request.cookies.get("gpm_lang") or "").strip().lower()
    if cookie in LOCALES:
        return cookie
    accept = request.headers.get("accept-language") or ""
    for part in accept.split(","):
        code = part.split(";")[0].strip().lower()
        if not code:
            continue
        primary = code.split("-")[0]
        if primary in LOCALES:
            return primary
    return DEFAULT_LOCALE


def translate(locale: str, key: str, **kwargs: Any) -> str:
    loc = locale if locale in LOCALES else DEFAULT_LOCALE
    table = MESSAGES.get(loc) or MESSAGES[DEFAULT_LOCALE]
    s = table.get(key)
    if s is None:
        s = MESSAGES[DEFAULT_LOCALE].get(key, key)
    if kwargs:
        return s.format(**kwargs)
    return s


def html_lang_attr(locale: str) -> str:
    return locale if locale in LOCALES else DEFAULT_LOCALE
