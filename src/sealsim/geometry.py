# ╔══════════════════════════════════════════════════════════════════╗
# ║  sealsim — geometry                                              ║
# ║  « one rotation convention, flow measured on the sphere »        ║
# ╠══════════════════════════════════════════════════════════════════╣
# ║  Body frame: x forward (thrust), y left (slip), z up (lift).     ║
# ║  World frame: right-handed, z up, depth negative. Euler angles   ║
# ║  (yaw, pitch, roll): yaw positive to the right, pitch positive   ║
# ║  nose-up, roll positive right-side-down, applied in that order   ║
# ║  (intrinsic Z, Y', X''). This keeps every sign in the data       ║
# ║  tables and the thesis; in z-up axes it is Rz(-yaw) Ry(-pitch)   ║
# ║  Rx(roll). Retinal coordinates: azimuth = atan2(y, x), positive  ║
# ║  to the left; elevation = asin(z / r), positive up. Sphere       ║
# ║  functions run on numpy or cupy arrays alike.                    ║
# ╚══════════════════════════════════════════════════════════════════╝

from __future__ import annotations

import numpy as np
from scipy.spatial.transform import Rotation

from sealsim.backend import array_module_of
from sealsim.constants import FloatArray

EULER_SIGNS = np.array([-1.0, -1.0, 1.0])


# ┌────────────────────────────────────────────────────────────┐
# │ Orientation  « Euler angles, rotations and their rates (CPU) » │
# └────────────────────────────────────────────────────────────┘
def body_to_world(euler: FloatArray) -> Rotation:
    """Rotation taking body-frame vectors to world axes; batched for (N, 3) input."""
    return Rotation.from_euler("ZYX", np.asarray(euler, dtype=float) * EULER_SIGNS)


def euler_from_rotation(rot: Rotation) -> FloatArray:
    return rot.as_euler("ZYX") * EULER_SIGNS


def body_angular_velocity(rates: FloatArray) -> FloatArray:
    """(yaw, pitch, roll) rates to the angular velocity vector in body axes."""
    rates = np.asarray(rates, dtype=float)
    return np.stack([rates[..., 2], -rates[..., 1], -rates[..., 0]], axis=-1)


def rates_from_angular_velocity(omega: FloatArray) -> FloatArray:
    omega = np.asarray(omega, dtype=float)
    return np.stack([-omega[..., 2], -omega[..., 1], omega[..., 0]], axis=-1)


def integrate_orientation(euler: FloatArray, rates: FloatArray, dt: float) -> FloatArray:
    """Compose a body-frame rotation increment onto the current orientation."""
    delta = Rotation.from_rotvec(body_angular_velocity(rates) * dt)
    return euler_from_rotation(body_to_world(euler) * delta)


def rates_between(euler0: FloatArray, euler1: FloatArray, dt: float) -> FloatArray:
    """Mean (yaw, pitch, roll) rates that carry euler0 into euler1 within dt."""
    delta = body_to_world(euler0).inv() * body_to_world(euler1)
    return rates_from_angular_velocity(delta.as_rotvec() / dt)


# ┌────────────────────────────────────────────────────────────┐
# │ Sphere  « directions on the retina (numpy or cupy) »       │
# └────────────────────────────────────────────────────────────┘
def unit_vectors(xyz: FloatArray) -> FloatArray:
    xp = array_module_of(xyz)
    xyz = xp.asarray(xyz, dtype=float)
    norm = xp.linalg.norm(xyz, axis=-1, keepdims=True)
    with np.errstate(invalid="ignore", divide="ignore"):
        return xp.where(norm > 0, xyz / norm, 0.0)


def to_spherical(xyz: FloatArray) -> tuple[FloatArray, FloatArray, FloatArray]:
    """Cartesian to (distance, azimuth, elevation) in metres and radians."""
    xp = array_module_of(xyz)
    xyz = xp.asarray(xyz, dtype=float)
    r = xp.linalg.norm(xyz, axis=-1)
    az = xp.arctan2(xyz[..., 1], xyz[..., 0])
    with np.errstate(invalid="ignore", divide="ignore"):
        el = xp.arcsin(xp.clip(xp.where(r > 0, xyz[..., 2] / r, 0.0), -1.0, 1.0))
    return r, az, el


def spherical_to_unit(az: FloatArray, el: FloatArray) -> FloatArray:
    xp = array_module_of(az, el)
    az, el = xp.asarray(az, dtype=float), xp.asarray(el, dtype=float)
    return xp.stack([xp.cos(el) * xp.cos(az), xp.cos(el) * xp.sin(az), xp.sin(el)], axis=-1)


def tangent_basis(az: FloatArray, el: FloatArray) -> tuple[FloatArray, FloatArray]:
    """Local east (increasing azimuth) and north (increasing elevation) unit vectors."""
    xp = array_module_of(az, el)
    az, el = xp.asarray(az, dtype=float), xp.asarray(el, dtype=float)
    zeros = xp.zeros_like(az)
    e_az = xp.stack([-xp.sin(az), xp.cos(az), zeros], axis=-1)
    e_el = xp.stack([-xp.sin(el) * xp.cos(az), -xp.sin(el) * xp.sin(az), xp.cos(el)], axis=-1)
    return e_az, e_el


def angle_between(a: FloatArray, b: FloatArray) -> FloatArray:
    """Great-circle angle between direction vectors, stable near 0 and pi."""
    xp = array_module_of(a, b)
    ua, ub = unit_vectors(a), unit_vectors(b)
    cross = xp.linalg.norm(xp.cross(ua, ub), axis=-1)
    dot = xp.einsum("...i,...i->...", ua, ub)
    return xp.arctan2(cross, dot)


def great_circle_flow(
    u0: FloatArray, u1: FloatArray
) -> tuple[FloatArray, FloatArray, FloatArray]:
    """Displacement on the sphere from direction u0 to u1.

    Returns:
        magnitude: great-circle angle [rad], shape (N,).
        tangent:   unit tangent at u0 pointing towards u1, shape (N, 3).
        flow:      magnitude times tangent in the (azimuth, elevation) basis at u0, (N, 2).
    """
    xp = array_module_of(u0, u1)
    u0, u1 = unit_vectors(u0), unit_vectors(u1)
    magnitude = angle_between(u0, u1)
    along = xp.einsum("...i,...i->...", u0, u1)[..., None]
    tangent = unit_vectors(u1 - along * u0)
    _, az, el = to_spherical(u0)
    e_az, e_el = tangent_basis(az, el)
    flow = magnitude[..., None] * xp.stack(
        [xp.einsum("...i,...i->...", tangent, e_az),
         xp.einsum("...i,...i->...", tangent, e_el)],
        axis=-1,
    )
    return magnitude, tangent, flow
