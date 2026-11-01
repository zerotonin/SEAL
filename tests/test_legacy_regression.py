# ╔══════════════════════════════════════════════════════════════════╗
# ║  sealsim — tests.test_legacy_regression                          ║
# ║  « the old code must keep doing what it did »                    ║
# ╠══════════════════════════════════════════════════════════════════╣
# ║  Guards the frozen scripts in _legacy/ against silent drift so the ║
# ║  rewrite can be compared against them in Sprint 2.               ║
# ╚══════════════════════════════════════════════════════════════════╝

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pytest

FIXTURE_DIR = Path(__file__).resolve().parent / "fixtures"
sys.path.insert(0, str(FIXTURE_DIR))
from make_legacy_fixture import run_legacy_step  # noqa: E402

FIXTURE = FIXTURE_DIR / "legacy_step_R0p1_seed0.npz"


@pytest.fixture(scope="module")
def pinned():
    return dict(np.load(FIXTURE))


@pytest.fixture(scope="module")
def fresh(legacy_sim):
    return run_legacy_step()


def test_particle_positions_reproduce(pinned, fresh):
    np.testing.assert_allclose(fresh["start"], pinned["start"], rtol=0, atol=1e-12)
    np.testing.assert_allclose(fresh["end"], pinned["end"], rtol=0, atol=1e-12)


def test_flow_magnitudes_reproduce(pinned, fresh):
    np.testing.assert_allclose(fresh["flow_mag"], pinned["flow_mag"], rtol=1e-10, atol=0)


def test_seal_moves_forward_by_one_sample(pinned, fresh):
    expected = pinned["position"] + np.array([3.0 / 100, 0.0, 0.0])
    np.testing.assert_allclose(fresh["seal_end"], expected, atol=1e-12)


def test_particles_shift_opposite_to_seal(fresh):
    shift = (fresh["end"] - fresh["start"])[fresh["visible"]]
    np.testing.assert_allclose(shift.mean(axis=0), [-0.03, 0.0, 0.0], atol=1e-6)
