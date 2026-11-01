# ╔══════════════════════════════════════════════════════════════════╗
# ║  sealsim — tests.test_opticflow                                  ║
# ║  « analytic flow fields the simulation must reproduce »          ║
# ╠══════════════════════════════════════════════════════════════════╣
# ║  Pure translation puts the focus of expansion at the heading,    ║
# ║  pure yaw gives uniform flow of omega dt, an object abeam at d   ║
# ║  moves at v/d, a current adds a uniform field, and nothing       ║
# ║  above the surface is seen.                                      ║
# ╚══════════════════════════════════════════════════════════════════╝

from __future__ import annotations

import numpy as np
import pytest

from sealsim import opticflow as of
from sealsim.agent import SealState
from sealsim.cloud import CloudSpec, ParticleCloud, build_cloud
from sealsim.environment import Environment, UniformCurrent
from sealsim.geometry import body_to_world
from sealsim.simulate import StepConfig, advance_cloud, run_step

SMALL_CLOUD = CloudSpec(n_particles=3000)


def _flow_for(velocity, dt=0.01, euler=(0.0, 0.0, 0.0), current=(0.0, 0.0, 0.0), seed=0):
    cloud = build_cloud(SMALL_CLOUD, np.random.default_rng(seed))
    env = Environment(current=UniformCurrent(current))
    field, after = advance_cloud(cloud, env, SealState.at(euler=euler), np.asarray(velocity), dt)
    return field, after


def test_pure_translation_focus_of_expansion_is_the_heading():
    field, _ = _flow_for([1.5, 0, 0, 0, 0, 0])
    foe = of.estimate_foe(field)
    assert of.foe_heading_error(foe, [1.5, 0, 0]) < np.deg2rad(0.5)


def test_pure_sideways_translation_focus_is_to_the_left():
    field, _ = _flow_for([0, 1.0, 0, 0, 0, 0])
    foe = of.estimate_foe(field, mask=field.valid)
    np.testing.assert_allclose(foe, [0.0, 1.0, 0.0], atol=0.02)


def test_pure_yaw_gives_uniform_flow_of_omega_dt_on_the_equator():
    omega, dt = 2.0, 0.01
    field, _ = _flow_for([0, 0, 0, omega, 0, 0], dt=dt)
    equator = field.valid & (np.abs(field.elevation) < np.deg2rad(5))
    np.testing.assert_allclose(field.magnitude[equator], omega * dt, rtol=5e-3)
    assert np.all(field.flow[equator, 0] > 0)


def test_object_abeam_moves_at_v_over_d():
    v, d, dt = 1.5, 0.3, 1e-3
    cloud = ParticleCloud(
        position=np.array([[0.0, d, 0.0]]), diameter=np.array([2e-3]),
        visibility_distance=np.array([1.0]), radius=1.0,
    )
    field, _ = advance_cloud(cloud, Environment(), SealState.at(),
                             np.array([v, 0, 0, 0, 0, 0]), dt)
    assert field.magnitude[0] / dt == pytest.approx(v / d, rel=1e-3)
    assert field.flow[0, 0] > 0  # on the left side, rearward drift is increasing azimuth


def test_critical_rotation_balances_translation_abeam():
    v, d = 1.5, 0.3
    cloud = ParticleCloud(
        position=np.array([[0.0, d, 0.0]]), diameter=np.array([2e-3]),
        visibility_distance=np.array([1.0]), radius=1.0,
    )
    trans, _ = advance_cloud(cloud.copy(), Environment(), SealState.at(),
                             np.array([v, 0, 0, 0, 0, 0]), 1e-3)
    rot, _ = advance_cloud(cloud.copy(), Environment(), SealState.at(),
                           np.array([0, 0, 0, v / d, 0, 0]), 1e-3)
    assert trans.magnitude[0] == pytest.approx(rot.magnitude[0], rel=1e-3)


def test_current_equals_opposite_self_motion():
    field_current, _ = _flow_for([0, 0, 0, 0, 0, 0], current=(-1.0, 0.0, 0.0))
    field_swim, _ = _flow_for([1.0, 0, 0, 0, 0, 0])
    np.testing.assert_allclose(field_current.magnitude, field_swim.magnitude, atol=1e-12)


def test_particles_above_the_surface_are_invisible():
    cloud = build_cloud(SMALL_CLOUD, np.random.default_rng(0))
    env = Environment()
    state = SealState.at(position=(0.0, 0.0, 0.0))
    field, _ = advance_cloud(cloud, env, state, np.array([1.0, 0, 0, 0, 0, 0]), 0.01)
    assert field.valid.any()
    assert not np.any(field.valid & (cloud.position[:, 2] > 0.1))


def test_flow_is_frame_invariant_under_initial_orientation():
    a, _ = _flow_for([1.0, 0.2, -0.1, 0.5, 0.2, 0.0])
    b, _ = _flow_for([1.0, 0.2, -0.1, 0.5, 0.2, 0.0], euler=(0.7, -0.3, 0.2))
    assert of.estimate_foe(a) == pytest.approx(of.estimate_foe(b), abs=0.05)


def test_fov_mask_uses_the_published_limits():
    az = np.deg2rad([0.0, 103.0, 105.0, -103.0])
    el = np.deg2rad([0.0, -11.0, 0.0, 70.0])
    np.testing.assert_array_equal(of.fov_mask(az, el), [True, True, False, False])


def test_spearman_rho_is_high_for_pure_translation_and_low_for_pure_yaw():
    trans, _ = _flow_for([1.5, 0, 0, 0, 0, 0])
    yaw, _ = _flow_for([0, 0, 0, 2.0, 0, 0])
    assert of.distance_rank_correlation(trans) > 0.5
    assert abs(of.distance_rank_correlation(yaw)) < 0.2


def test_translation_rotation_index_bounds():
    assert of.translation_rotation_index(1.0, 0.0) == 1.0
    assert of.translation_rotation_index(0.0, 1.0) == -1.0
    assert np.isnan(of.translation_rotation_index(0.0, 0.0))


def test_run_step_decomposes_and_reports_all_metrics():
    result = run_step(StepConfig(velocity=(1.8, 0.0, 0.0, 2.2, 0.0, 0.0), seed=1,
                                 cloud=CloudSpec(n_particles=2000)))
    m = result.metrics
    assert set(result.components) == {"translation", "rotation"}
    assert m.n_in_fov > 0
    assert -1.0 <= m.trans_rot_index <= 1.0
    assert np.isfinite(m.foe_error_rad) and np.isfinite(m.spearman_rho)
    rotation_only = body_to_world(result.after.euler)
    assert rotation_only.magnitude() == pytest.approx(2.2 * result.dt, rel=1e-9)
