# ╔══════════════════════════════════════════════════════════════════╗
# ║  sealsim — tests.test_cloud                                      ║
# ║  « uniform in volume, exact respawn, honest visibility »         ║
# ╠══════════════════════════════════════════════════════════════════╣
# ║  The legacy cloud put 82 % of particles outside its radius;      ║
# ║  these tests make that class of bug impossible to reintroduce.   ║
# ╚══════════════════════════════════════════════════════════════════╝

from __future__ import annotations

import numpy as np
import pytest
from scipy.stats import kstest

from sealsim import cloud as cl


def test_visibility_distance_corrects_the_degree_radian_slip():
    assert cl.visibility_distance(160e-6, 5.5 / 60) == pytest.approx(0.1000, abs=2e-4)
    assert cl.visibility_distance(2e-3, 0.27) == pytest.approx(0.4244, abs=1e-3)


def test_spec_radius_is_the_reach_of_the_largest_grain():
    spec = cl.CloudSpec(acuity_deg=0.27, diameter_range_m=(0.5e-3, 2e-3), n_particles=10)
    assert spec.radius_m == pytest.approx(0.4244, abs=1e-3)


def test_spec_count_from_density():
    spec = cl.CloudSpec(number_density_per_m3=1000.0)
    assert spec.count() == pytest.approx(1000.0 * spec.volume_m3, abs=1)
    with pytest.raises(ValueError):
        cl.CloudSpec().count()


def test_number_density_from_spm_quartz_millimetre_grains():
    assert cl.number_density_from_spm(1.0, 1e-3) == pytest.approx(720.8, rel=1e-3)


def test_uniform_ball_radial_cdf_is_cubic():
    rng = np.random.default_rng(0)
    r = np.linalg.norm(cl.sample_uniform_ball(20000, 2.0, rng), axis=1)
    assert r.max() <= 2.0
    assert kstest(r / 2.0, lambda x: x**3).pvalue > 0.01


def test_uniform_ball_directions_are_isotropic():
    rng = np.random.default_rng(0)
    xyz = cl.sample_uniform_ball(20000, 1.0, rng)
    cos_theta = xyz[:, 2] / np.linalg.norm(xyz, axis=1)
    assert kstest(cos_theta, "uniform", args=(-1, 2)).pvalue > 0.01


def test_build_cloud_is_inside_radius_and_visibility_per_particle():
    spec = cl.CloudSpec(n_particles=500)
    cloud = cl.build_cloud(spec, np.random.default_rng(3))
    assert np.all(np.linalg.norm(cloud.position, axis=1) <= cloud.radius)
    assert np.all(cloud.visibility_distance <= cloud.radius + 1e-12)
    visible = cl.visible_at(cloud, cloud.position)
    assert 0 < visible.sum() < cloud.n


def test_advect_respawns_by_point_reflection_and_keeps_count():
    rng = np.random.default_rng(4)
    cloud = cl.build_cloud(cl.CloudSpec(n_particles=2000), rng)
    radius = cloud.radius
    step = cl.advect_cloud(cloud, np.array([0.3 * radius, 0.0, 0.0]))
    assert step.exited.any()
    assert cloud.n == 2000
    np.testing.assert_allclose(cloud.position[step.exited], -step.pre[step.exited])
    assert np.all(np.linalg.norm(cloud.position, axis=1) <= radius + 1e-12)


def test_density_stays_uniform_after_many_steps():
    rng = np.random.default_rng(5)
    cloud = cl.build_cloud(cl.CloudSpec(n_particles=20000), rng)
    for _ in range(40):
        cl.advect_cloud(cloud, np.array([0.1 * cloud.radius, 0.02 * cloud.radius, 0.0]))
    r = np.linalg.norm(cloud.position, axis=1) / cloud.radius
    assert kstest(r, lambda x: x**3).pvalue > 0.01
