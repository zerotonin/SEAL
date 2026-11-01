# ╔══════════════════════════════════════════════════════════════════╗
# ║  sealsim — agent                                                 ║
# ║  « the seal: a pose and a body-frame velocity »                  ║
# ╠══════════════════════════════════════════════════════════════════╣
# ║  Position is world-frame, orientation is (yaw, pitch, roll) per  ║
# ║  geometry.py. A step translates along the body velocity rotated  ║
# ║  into world axes and composes the rotation increment properly,   ║
# ║  so the agent and the particle cloud always agree on the frame.  ║
# ╚══════════════════════════════════════════════════════════════════╝

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from scipy.spatial.transform import Rotation

from sealsim.constants import DEFAULT_SEAL_DEPTH_M, FloatArray
from sealsim.geometry import body_to_world, integrate_orientation


@dataclass(frozen=True)
class SealState:
    position: FloatArray
    euler: FloatArray

    @classmethod
    def at(cls, position=(0.0, 0.0, DEFAULT_SEAL_DEPTH_M), euler=(0.0, 0.0, 0.0)) -> SealState:
        return cls(np.asarray(position, dtype=float), np.asarray(euler, dtype=float))

    def rotation(self) -> Rotation:
        return body_to_world(self.euler)


def translation_part(velocity: FloatArray) -> FloatArray:
    v = np.zeros(6)
    v[:3] = np.asarray(velocity, dtype=float)[:3]
    return v


def rotation_part(velocity: FloatArray) -> FloatArray:
    v = np.zeros(6)
    v[3:] = np.asarray(velocity, dtype=float)[3:]
    return v


def world_velocity(state: SealState, velocity: FloatArray) -> FloatArray:
    """Translational velocity (thrust, slip, lift) expressed in world axes."""
    return state.rotation().apply(np.asarray(velocity, dtype=float)[:3])


def advance(state: SealState, velocity: FloatArray, dt: float) -> SealState:
    """One explicit step: translate along the current heading, then rotate."""
    velocity = np.asarray(velocity, dtype=float)
    position = state.position + world_velocity(state, velocity) * dt
    euler = integrate_orientation(state.euler, velocity[3:], dt)
    return SealState(position, euler)
