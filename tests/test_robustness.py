# ╔══════════════════════════════════════════════════════════════════╗
# ║  sealsim — tests.test_robustness                                 ║
# ║  « bands, bow flow and the Cramer-Rao bound behave as derived »  ║
# ╚══════════════════════════════════════════════════════════════════╝

from __future__ import annotations

import numpy as np
import pytest

from sealsim import robustness as rb
from sealsim.cloud import CloudSpec
from sealsim.simulate import StepConfig, run_step

SPEC = CloudSpec(acuity_deg=0.27, diameter_range_m=(0.5e-3, 2e-3), n_particles=4000)


def _step(yaw_degps: float, seed: int = 0):
    return run_step(StepConfig(velocity=(1.5, 0, 0, np.deg2rad(yaw_degps), 0, 0),
                               cloud=SPEC, seed=seed))


def test_regional_index_is_one_without_rotation_and_falls_with_it():
    still = rb.regional_index(_step(0.0))
    assert np.allclose(still["index"], 1.0)
    turning = rb.regional_index(_step(300.0))
    assert (turning["index"] < 1.0).all()
    assert turning["n"].sum() > 0


def test_frontal_band_crosses_first_instantaneously():
    frame = rb.instant_regional_index(SPEC, 1.5, 456.0, seed=1).set_index("band")
    assert frame.loc["frontal", "index"] < frame.loc["oblique", "index"]
    assert frame.loc["oblique", "index"] < frame.loc["lateral", "index"]
    rng = np.random.default_rng(0)
    frontal = rb.band_critical_ratio(rb.DEFAULT_BANDS[0], 2.0, rng)
    lateral = rb.band_critical_ratio(rb.DEFAULT_BANDS[2], 2.0, rng)
    assert frontal < 1.4 < 2.0 < lateral


def test_bow_flow_is_small_and_unbiased_for_pure_thrust():
    bias = rb.bow_flow_bias(SPEC, (1.5, 0.0, 0.0), 124.0, body_radius_m=0.09)
    assert 0.9 < bias.translational_gain < 1.0
    assert abs(bias.index_with - bias.index_without) < 0.03
    assert bias.foe_error_deg == pytest.approx(0.0, abs=1e-6)
    assert bias.apparent_rotation_degps == pytest.approx(0.0, abs=1e-6)
    bigger = rb.bow_flow_bias(SPEC, (1.5, 0.0, 0.0), 124.0, body_radius_m=0.16)
    assert bigger.translational_gain < bias.translational_gain


def test_dipole_field_vanishes_far_from_the_body():
    far = np.array([[50.0, 0.0, 0.0]])
    v = np.array([1.5, 0.0, 0.0])
    u = rb.dipole_relative_velocity(far, v, 0.1, np.zeros(3))
    assert np.allclose(u, -v, atol=1e-6)


def test_crb_additive_is_rotation_free_and_weber_is_not():
    noises = {"add": rb.ObserverNoise(0.1, 0.0), "web": rb.ObserverNoise(0.1, 0.3)}
    slow = rb.observer_errors(_step(0.0), noises)
    fast = rb.observer_errors(_step(900.0), noises)
    assert slow["add"] == pytest.approx(fast["add"], rel=1e-6)
    assert fast["web"] > 1.5 * slow["web"]
    assert fast["foe_template"] > slow["foe_template"]
