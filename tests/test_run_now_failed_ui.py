from types import SimpleNamespace
from unittest.mock import AsyncMock, patch

from starlette.testclient import TestClient


def test_run_now_redirects_failed_run_query() -> None:
    from app.main import app

    failed = SimpleNamespace(id=42, status="failed", error_message="httpx.ConnectError: boom")

    with patch(
        "app.routers.web.execute_scrape",
        new=AsyncMock(return_value=failed),
    ):
        with TestClient(app) as client:
            r = client.post("/run-now", data={}, follow_redirects=False)
    assert r.status_code == 303
    assert "failed_run=42" in r.headers["location"]


def test_run_now_redirects_done_run_on_success() -> None:
    from app.main import app

    ok = SimpleNamespace(id=7, status="success")

    with patch(
        "app.routers.web.execute_scrape",
        new=AsyncMock(return_value=ok),
    ):
        with TestClient(app) as client:
            r = client.post("/run-now", data={}, follow_redirects=False)
    assert r.status_code == 303
    assert "done_run=7" in r.headers["location"]
