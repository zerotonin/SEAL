# ╔══════════════════════════════════════════════════════════════════╗
# ║  sealsim — tests.test_geometry                                   ║
# ║  « the rotation convention, pinned by hand-computed cases »      ║
# ╠══════════════════════════════════════════════════════════════════╣
# ║  Yaw right, pitch up, roll right-side-down; azimuth              ║
# ║  left-positive; great-circle flow exact for finite steps.        ║
# ╚══════════════════════════════════════════════════════════════════╝

from __future__ import annotations

import numpy as np
import pytest

from sealsim import geometry as geo

FORWARD = np.array([1.0, 0.0, 0.0])
LEFT = np.array([0.0, 1.0, 0.0])
UP = np.array([0.0, 0.0, 1.0])


def test_yaw_right_turns_forward_vector_to_minus_y():
    rot = geo.body_to_world([np.pi / 2, 0.0, 0.0])
    np.testing.assert_allclose(rot.apply(FORWARD), [0.0, -1.0, 0.0], atol=1e-12)


def test_pitch_up_raises_the_nose():
    rot = geo.body_to_world([0.0, np.deg2rad(30), 0.0])
    np.testing.assert_allclose(rot.apply(FORWARD), [np.cos(np.pi / 6), 0.0, 0.5], atol=1e-12)


def test_roll_right_lowers_the_right_side():
    rot = geo.body_to_world([0.0, 0.0, np.pi / 2])
    np.testing.assert_allclose(rot.apply(LEFT), UP, atol=1e-12)


def test_euler_round_trip():
    euler = np.array([0.3, -0.4, 0.2])
    np.testing.assert_allclose(geo.euler_from_rotation(geo.body_to_world(euler)), euler)


def test_integrate_orientation_matches_small_angle_addition_from_level():
    rates = np.array([1.0, -0.5, 0.3])
    new = geo.integrate_orientation(np.zeros(3), rates, 1e-3)
    np.testing.assert_allclose(new, rates * 1e-3, atol=1e-6)


def test_yaw_rate_at_pitch_couples_into_roll():
    """Body rates are not Euler rates: yawing while pitched rolls the Euler roll."""
    euler = np.array([0.1, 0.05, 0.0])
    new = geo.integrate_orientation(euler, [1.0, 0.0, 0.0], 1e-3)
    assert new[2] == pytest.approx(1e-3 * np.tan(0.05), rel=1e-4)


def test_rates_between_inverts_integration():
    euler = np.array([0.4, -0.2, 0.1])
    rates = np.array([2.0, 1.0, -0.5])
    new = geo.integrate_orientation(euler, rates, 0.01)
    np.testing.assert_allclose(geo.rates_between(euler, new, 0.01), rates, atol=1e-9)


def test_spherical_azimuth_is_left_positive_and_elevation_up():
    r, az, el = geo.to_spherical(np.array([[1.0, 1.0, 0.0], [0.0, 0.0, 2.0]]))
    np.testing.assert_allclose(r, [np.sqrt(2), 2.0])
    np.testing.assert_allclose(az[0], np.pi / 4)
    np.testing.assert_allclose(el, [0.0, np.pi / 2])


def test_spherical_to_unit_round_trip():
    xyz = np.random.default_rng(1).normal(size=(50, 3))
    _, az, el = geo.to_spherical(xyz)
    np.testing.assert_allclose(geo.spherical_to_unit(az, el), geo.unit_vectors(xyz), atol=1e-12)


def test_great_circle_flow_near_the_zenith_is_small():
    """Legacy elementwise difference reported 3.14 rad here; the true angle is 0.2."""
    u0 = geo.spherical_to_unit(0.0, np.pi / 2 - 0.1)
    u1 = geo.spherical_to_unit(np.pi, np.pi / 2 - 0.1)
    magnitude, _, _ = geo.great_circle_flow(u0[None], u1[None])
    np.testing.assert_allclose(magnitude, [0.2], atol=1e-12)


def test_great_circle_flow_along_the_equator_is_pure_azimuth():
    u0 = geo.spherical_to_unit(0.0, 0.0)
    u1 = geo.spherical_to_unit(0.3, 0.0)
    magnitude, tangent, flow = geo.great_circle_flow(u0[None], u1[None])
    np.testing.assert_allclose(magnitude, [0.3])
    np.testing.assert_allclose(flow, [[0.3, 0.0]], atol=1e-12)
    np.testing.assert_allclose(tangent, [[0.0, 1.0, 0.0]], atol=1e-12)


@pytest.mark.parametrize("angle", [1e-9, 0.5, np.pi - 1e-6])
def test_angle_between_is_stable(angle):
    b = np.array([np.cos(angle), np.sin(angle), 0.0])
    np.testing.assert_allclose(geo.angle_between(FORWARD, b), angle, rtol=1e-6, atol=1e-12)
