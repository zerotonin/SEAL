# ╔══════════════════════════════════════════════════════════════════╗
# ║  sealsim — tests.conftest                                        ║
# ║  « shared fixtures and a headless matplotlib »                   ║
# ╠══════════════════════════════════════════════════════════════════╣
# ║  LEGACY_DIR points at the frozen 2019-2022 scripts for regression. ║
# ╚══════════════════════════════════════════════════════════════════╝

from __future__ import annotations

import os
import sys
from pathlib import Path

import pytest

os.environ.setdefault("MPLBACKEND", "Agg")

REPO_ROOT = Path(__file__).resolve().parents[1]
LEGACY_DIR = REPO_ROOT / "_legacy"
FIXTURE_DIR = Path(__file__).resolve().parent / "fixtures"


@pytest.fixture(scope="session")
def legacy_sim():
    """Import the legacy SEAL_SIM module, or skip when its deps are absent."""
    pytest.importorskip("ai.cs", reason="legacy code needs the ai.cs package")
    if str(LEGACY_DIR) not in sys.path:
        sys.path.insert(0, str(LEGACY_DIR))
    import SEAL_SIM  # noqa: E402  (legacy flat module)

    return SEAL_SIM
