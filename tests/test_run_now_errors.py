from unittest.mock import AsyncMock, patch

from starlette.testclient import TestClient


def test_run_now_redirects_with_error_on_failure() -> None:
    from app.main import app

    with patch(
        "app.routers.web.execute_scrape",
        new=AsyncMock(side_effect=RuntimeError("MissingGreenlet: simulated")),
    ):
        with TestClient(app) as client:
            r = client.post("/run-now", data={}, follow_redirects=False)
    assert r.status_code == 303
    assert r.headers["location"].startswith("/runs?error=")
    assert "MissingGreenlet" in r.headers["location"]
