"""Release notes shown on /documentation (user-facing). Keep in sync with meaningful releases."""

from __future__ import annotations

from typing import TypedDict


class ChangelogEntry(TypedDict):
    version: str
    date: str
    items: dict[str, list[str]]


CHANGELOG: list[ChangelogEntry] = [
    {
        "version": "0.0.18",
        "date": "2026-04-24",
        "items": {
            "es": [
                "Documentación: el registro de cambios va en un bloque desplegable (<details>) para no alargar la página.",
            ],
            "en": [
                "Documentation: changelog is inside a collapsible <details> block so the page stays short.",
            ],
            "de": [
                "Dokumentation: Änderungsprotokoll in einem einklappbaren <details>-Block, damit die Seite kurz bleibt.",
            ],
        },
    },
    {
        "version": "0.0.17",
        "date": "2026-04-24",
        "items": {
            "es": [
                "Corrección: la plantilla de documentación usaba la clave «items» del changelog; en Jinja eso colisionaba con dict.items() y devolvía error 500.",
            ],
            "en": [
                "Fix: documentation template used changelog key «items»; in Jinja that collided with dict.items() and caused a 500 error.",
            ],
            "de": [
                "Fix: Dokumentationsvorlage nutzte den Changelog-Schlüssel «items»; in Jinja kollidierte das mit dict.items() und verursachte HTTP 500.",
            ],
        },
    },
    {
        "version": "0.0.16",
        "date": "2026-04-24",
        "items": {
            "es": [
                "Nueva página «Documentación» en la propia aplicación (guía de uso, configuración, portales/LLM, API, entorno y registro de cambios).",
                "Regla del proyecto: actualizar esta documentación cuando cambie la funcionalidad o la interfaz de forma relevante.",
            ],
            "en": [
                "New in-app «Documentation» page (usage, settings, portals/LLM, API, environment, and changelog).",
                "Project rule: keep this documentation updated when functionality or the UI changes in a meaningful way.",
            ],
            "de": [
                "Neue «Dokumentation»-Seite in der App (Nutzung, Einstellungen, Portale/LLM, API, Umgebung und Änderungsprotokoll).",
                "Projektregel: Diese Dokumentation bei relevanten Funktions- oder UI-Änderungen aktualisieren.",
            ],
        },
    },
    {
        "version": "0.0.15",
        "date": "2026-04",
        "items": {
            "es": [
                "Iteración de despliegue y UI (favicon, compose dev/prod, textos y flujos de configuración).",
            ],
            "en": [
                "Deployment/UI iteration (favicon, dev/prod compose, copy and configuration flows).",
            ],
            "de": [
                "Deployment-/UI-Iteration (Favicon, Compose dev/prod, Texte und Konfigurationsabläufe).",
            ],
        },
    },
    {
        "version": "0.0.8",
        "date": "2025",
        "items": {
            "es": [
                "Tema claro/oscuro, cabecera renovada y tokens de diseño.",
                "Interfaz en varios idiomas (es / en / de).",
            ],
            "en": [
                "Light/dark theme, refreshed header and design tokens.",
                "UI locales (es / en / de).",
            ],
            "de": [
                "Hell-/Dunkelmodus, überarbeitete Kopfzeile und Design-Tokens.",
                "Oberfläche mehrsprachig (es / en / de).",
            ],
        },
    },
    {
        "version": "0.0.1",
        "date": "2025",
        "items": {
            "es": [
                "Versión inicial: FastAPI, Playwright, extracción vía LLM compatible con OpenAI/Ollama, SQLite y scheduler.",
                "Resolución automática de URL del LLM y diagnóstico (`/api/llm-check`).",
            ],
            "en": [
                "Initial release: FastAPI, Playwright, OpenAI/Ollama-compatible LLM extraction, SQLite, and scheduler.",
                "Automatic LLM base URL resolution and diagnostics (`/api/llm-check`).",
            ],
            "de": [
                "Erstversion: FastAPI, Playwright, OpenAI/Ollama-kompatible LLM-Extraktion, SQLite und Scheduler.",
                "Automatische LLM-Basis-URL-Auflösung und Diagnose (`/api/llm-check`).",
            ],
        },
    },
]
