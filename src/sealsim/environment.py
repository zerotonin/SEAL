# ╔══════════════════════════════════════════════════════════════════╗
# ║  sealsim — environment                                           ║
# ║  « the water column and what moves in it »                       ║
# ╠══════════════════════════════════════════════════════════════════╣
# ║  Surface and floor are planes; particles outside the column are  ║
# ║  invisible. Currents are world-frame velocity fields evaluated   ║
# ║  at absolute particle positions, either uniform or interpolated  ║
# ║  between the eight corners of the simulated box (legacy mode).   ║
# ╚══════════════════════════════════════════════════════════════════╝

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Protocol

import numpy as np
from scipy.interpolate import RegularGridInterpolator

from sealsim.constants import OCEAN_FLOOR_Z_M, OCEAN_SURFACE_Z_M, BoolArray, FloatArray, Vec3


# ┌────────────────────────────────────────────────────────────┐
# │ Currents  « velocity fields in world axes »                │
# └────────────────────────────────────────────────────────────┘
class CurrentField(Protocol):
    def __call__(self, position: FloatArray) -> FloatArray: ...


@dataclass(frozen=True)
class UniformCurrent:
    velocity: Vec3 = (0.0, 0.0, 0.0)

    def __call__(self, position: FloatArray) -> FloatArray:
        position = np.asarray(position, dtype=float)
        return np.broadcast_to(np.asarray(self.velocity, dtype=float), position.shape).copy()

    @property
    def speed(self) -> float:
        return float(np.linalg.norm(self.velocity))


@dataclass(frozen=True, eq=False)
class CornerCurrent:
    """Trilinear interpolation between velocities given at the box corners.

    corners has shape (2, 2, 2, 3), indexed by (x, y, z) corner and component;
    index 0 is the lower bound of each axis.
    """

    corners: FloatArray
    xy_limits: tuple[float, float] = (-70.0, 70.0)
    z_limits: tuple[float, float] = (OCEAN_FLOOR_Z_M.value, OCEAN_SURFACE_Z_M)

    def __post_init__(self) -> None:
        grid = (np.array(self.xy_limits), np.array(self.xy_limits), np.array(self.z_limits))
        interp = RegularGridInterpolator(
            grid, np.asarray(self.corners, dtype=float), bounds_error=False, fill_value=None
        )
        object.__setattr__(self, "_interp", interp)

    def __call__(self, position: FloatArray) -> FloatArray:
        return self._interp(np.atleast_2d(np.asarray(position, dtype=float)))


# ┌────────────────────────────────────────────────────────────┐
# │ Column  « surface, floor and the field between them »      │
# └────────────────────────────────────────────────────────────┘
@dataclass(frozen=True)
class Environment:
    surface_z: float = OCEAN_SURFACE_Z_M
    floor_z: float = OCEAN_FLOOR_Z_M.value
    current: CurrentField = field(default_factory=UniformCurrent)

    def in_water(self, z: FloatArray) -> BoolArray:
        z = np.asarray(z, dtype=float)
        return (z < self.surface_z) & (z > self.floor_z)

    def current_at(self, position: FloatArray) -> FloatArray:
        return self.current(position)
