# ╔══════════════════════════════════════════════════════════════════╗
# ║  sealsim — tests.test_corollaries                                ║
# ║  « the law in Sauter form, under a horizon and in time »         ║
# ╚══════════════════════════════════════════════════════════════════╝

from __future__ import annotations

import numpy as np
import pytest

from sealsim import corollaries as co
from sealsim.figures import critical_ratio


@pytest.fixture
def rng():
    return np.random.default_rng(0)


def test_uniform_sample_matches_closed_form(rng):
    d = co.uniform_diameters(0.5e-3, 2e-3, 400_000, rng)
    reach = co.effective_reach(d, 0.27)
    ratio = co.critical_rate_from_reaches(1.5, reach) * reach.max() / 1.5
    assert ratio == pytest.approx(critical_ratio(0.5e-3, 2e-3), rel=2e-3)
    assert co.critical_ratio_uniform(0.25) == pytest.approx(critical_ratio(0.5e-3, 2e-3))


def test_sauter_form_is_the_acuity_law_for_any_distribution(rng):
    for d in (co.lognormal_diameters(180e-6, 1.8, 50_000, rng),
              co.junge_diameters(20e-6, 2e-3, 4.0, 50_000, rng)):
        direct = co.critical_rate(1.5, d, 0.27)
        sauter = co.critical_rate_sauter(1.5, co.sauter_mean_diameter(d), 0.27)
        assert direct == pytest.approx(sauter, rel=1e-9)


def test_junge_sample_stays_inside_the_cutoffs(rng):
    d = co.junge_diameters(20e-6, 2e-3, 4.0, 10_000, rng)
    assert d.min() >= 20e-6 and d.max() <= 2e-3
    assert np.median(d) < 100e-6          # steep spectrum: most grains are small
    with pytest.raises(ValueError):
        co.junge_diameters(1e-6, 1e-3, 1.0, 10, rng)


def test_horizon_only_raises_the_critical_rate(rng):
    d = co.uniform_diameters(0.5e-3, 2e-3, 100_000, rng)
    free = co.critical_rate(1.5, d, 0.27)
    assert co.critical_rate(1.5, d, 0.27, horizon_m=5.0) == pytest.approx(free)
    cut = co.critical_rate(1.5, d, 0.27, horizon_m=0.1)
    assert cut > free
    assert cut == pytest.approx(1.5 * 1.5 / 0.1, rel=1e-9)   # every grain cut: 3v/(2R)


def test_horizon_helpers_invert_each_other():
    c = co.attenuation_for_horizon(1.0)
    assert co.contrast_horizon(c) == pytest.approx(1.0)
    assert co.horizon_at_turn_rate(1.5, np.deg2rad(124)) == pytest.approx(1.04, abs=0.01)


def test_time_form_and_speed_estimator(rng):
    assert co.turn_per_crossing_deg(2.0) == pytest.approx(114.59, abs=0.01)
    assert co.crossing_time_s(0.42, 1.5) == pytest.approx(0.28)
    d = co.uniform_diameters(0.5e-3, 2e-3, 20_000, rng)
    n = 500
    sizes = rng.choice(d, n)
    cos_phi = rng.uniform(-1, 1, n)
    distance = rng.uniform(0.05, 0.4, n)
    flow = 2.0 * np.sqrt(1 - cos_phi**2) / distance
    estimate = co.speed_from_flow(flow, sizes / distance, float(np.mean(1 / d)))
    assert estimate == pytest.approx(2.0, rel=0.1)
    assert co.speed_estimate_cv(d, 100, rng) < co.speed_estimate_cv(d, 10, rng)
