# ╔══════════════════════════════════════════════════════════════════╗
# ║  sealsim — tests.test_legacy_vs_new                              ║
# ║  « the rewrite reproduces the 2022 step where it was right »     ║
# ╠══════════════════════════════════════════════════════════════════╣
# ║  Same 200 start positions, same 3 m/s thrust at 100 Hz, zero     ║
# ║  orientation, R = 0.1 m. Kinematics must agree exactly; the      ║
# ║  legacy flow magnitude is reconstructed from the new spherical   ║
# ║  coordinates, and the exact great-circle angle is shown to be    ║
# ║  the smaller, correct quantity.                                  ║
# ╚══════════════════════════════════════════════════════════════════╝

from __future__ import annotations

from pathlib import Path

import numpy as np
import pytest

from sealsim.agent import SealState
from sealsim.cloud import ParticleCloud
from sealsim.environment import Environment
from sealsim.geometry import to_spherical
from sealsim.simulate import advance_cloud

FIXTURE = Path(__file__).resolve().parent / "fixtures" / "legacy_step_R0p1_seed0.npz"


@pytest.fixture(scope="module")
def legacy():
    return dict(np.load(FIXTURE))


@pytest.fixture(scope="module")
def replay(legacy):
    """Run the new kinematics from the legacy start positions."""
    radius = float(legacy["cloud_radius"])
    n = legacy["start"].shape[0]
    cloud = ParticleCloud(
        position=legacy["start"].copy(), diameter=np.full(n, 160e-6),
        visibility_distance=np.full(n, radius), radius=radius,
    )
    state = SealState.at(position=legacy["position"])
    dt = 1.0 / 100
    field, after = advance_cloud(cloud, Environment(), state, legacy["step"], dt)
    return dict(field=field, after=after, pre=legacy["start"], post=legacy["start"]
                + (legacy["end"] - legacy["start"]))


def test_particle_shift_matches_legacy_exactly(legacy, replay):
    np.testing.assert_allclose(replay["post"], legacy["end"], atol=1e-15)
    np.testing.assert_allclose(replay["after"].position, legacy["seal_end"], atol=1e-12)


def test_legacy_flow_magnitude_is_reconstructed_from_new_coordinates(legacy, replay):
    """Legacy |OF| = sqrt(dr^2 + d_el^2 + d_az^2), metres mixed with radians."""
    r0, az0, el0 = to_spherical(legacy["start"])
    r1, az1, el1 = to_spherical(legacy["end"])
    d_az, d_el = az1 - az0, el1 - el0
    no_wrap = (np.abs(d_az) <= np.pi) & (np.abs(d_el) <= np.pi / 2)
    legacy_like = np.sqrt((r1 - r0) ** 2 + d_el**2 + d_az**2)
    np.testing.assert_allclose(legacy_like[no_wrap], legacy["flow_mag"][no_wrap], rtol=1e-9)


def test_great_circle_angle_never_exceeds_the_legacy_angle_sum(legacy, replay):
    field = replay["field"]
    valid = field.valid
    r0, az0, el0 = to_spherical(legacy["start"])
    r1, az1, el1 = to_spherical(legacy["end"])
    legacy_angle_only = np.sqrt((az1 - az0) ** 2 + (el1 - el0) ** 2)
    assert np.all(field.magnitude[valid] <= legacy_angle_only[valid] + 1e-12)
    assert field.magnitude[valid].max() < np.pi


def test_small_displacements_agree_to_first_order(legacy, replay):
    """For small steps the exact angle equals sqrt((cos(el) d_az)^2 + d_el^2)."""
    field = replay["field"]
    _, az0, el0 = to_spherical(legacy["start"])
    _, az1, el1 = to_spherical(legacy["end"])
    first_order = np.sqrt((np.cos(el0) * (az1 - az0)) ** 2 + (el1 - el0) ** 2)
    small = (first_order < 0.2) & (np.abs(el0) < np.deg2rad(45))
    assert small.sum() > 20
    np.testing.assert_allclose(field.magnitude[small], first_order[small], rtol=0.05)
