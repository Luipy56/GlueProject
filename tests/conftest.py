"""Set data dir before importing the application (engine URL is resolved at import)."""

from __future__ import annotations

import os
import uuid
from pathlib import Path

import pytest

_root = Path(__file__).resolve().parents[1]
_gpm = _root / "data" / f"pytest_{uuid.uuid4().hex}"
_gpm.mkdir(parents=True, exist_ok=True)
os.environ["GPM_DATA_DIR"] = str(_gpm)


@pytest.fixture(scope="session")
def anyio_backend() -> str:
    return "asyncio"
