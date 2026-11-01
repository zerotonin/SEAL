# ╔══════════════════════════════════════════════════════════════════╗
# ║  sealsim — cloud                                                 ║
# ║  « particles as arrays, uniform in volume, each with its own reach » ║
# ╠══════════════════════════════════════════════════════════════════╣
# ║  The cloud is a ball of radius R = d_max around the seal, where  ║
# ║  d_i = a_i / tan(acuity) is the distance at which a grain of     ║
# ║  diameter a_i still subtends the acuity angle. Positions are     ║
# ║  offsets from the seal in world axes, shape (N, 3). A particle   ║
# ║  that leaves the ball re-enters at the point reflection of its   ║
# ║  pre-step position, which maps the exit lens onto the entry      ║
# ║  lens exactly and keeps the density uniform.                     ║
# ╚══════════════════════════════════════════════════════════════════╝

from __future__ import annotations

from dataclasses import dataclass, replace

import numpy as np

from sealsim.constants import (
    ACUITY_SINGLE_TARGET,
    GRAIN_DENSITY,
    PARTICLE_DIAMETER_RANGE_M,
    BoolArray,
    FloatArray,
)


# ┌────────────────────────────────────────────────────────────┐
# │ Specification  « what defines a cloud before sampling »    │
# └────────────────────────────────────────────────────────────┘
@dataclass(frozen=True)
class CloudSpec:
    """Acuity and grain sizes fix the radius; count or density fixes N."""

    acuity_deg: float = ACUITY_SINGLE_TARGET.value
    diameter_range_m: tuple[float, float] = PARTICLE_DIAMETER_RANGE_M
    n_particles: int | None = None
    number_density_per_m3: float | None = None

    @property
    def radius_m(self) -> float:
        return float(visibility_distance(self.diameter_range_m[1], self.acuity_deg))

    @property
    def volume_m3(self) -> float:
        return 4.0 / 3.0 * np.pi * self.radius_m**3

    def count(self) -> int:
        if self.n_particles is not None:
            return int(self.n_particles)
        if self.number_density_per_m3 is not None:
            return max(1, int(round(self.number_density_per_m3 * self.volume_m3)))
        raise ValueError("CloudSpec needs n_particles or number_density_per_m3")

    def with_count(self, n_particles: int) -> CloudSpec:
        return replace(self, n_particles=n_particles, number_density_per_m3=None)


def visibility_distance(diameter_m: FloatArray | float, acuity_deg: float) -> FloatArray | float:
    """Distance at which a grain subtends the acuity angle: d = a / tan(alpha)."""
    return np.asarray(diameter_m, dtype=float) / np.tan(np.deg2rad(acuity_deg))


def number_density_from_spm(
    mass_concentration_g_per_m3: float,
    diameter_m: float,
    grain_density_kg_per_m3: float = GRAIN_DENSITY.value,
) -> float:
    """Particles per cubic metre for spheres of one diameter carrying all the mass."""
    grain_mass_kg = grain_density_kg_per_m3 * np.pi / 6.0 * diameter_m**3
    return mass_concentration_g_per_m3 / 1000.0 / grain_mass_kg


# ┌────────────────────────────────────────────────────────────┐
# │ State  « the sampled cloud and its kinematics »            │
# └────────────────────────────────────────────────────────────┘
@dataclass
class ParticleCloud:
    position: FloatArray
    diameter: FloatArray
    visibility_distance: FloatArray
    radius: float

    @property
    def n(self) -> int:
        return int(self.position.shape[0])

    def copy(self) -> ParticleCloud:
        return ParticleCloud(
            self.position.copy(), self.diameter.copy(),
            self.visibility_distance.copy(), self.radius,
        )


@dataclass
class CloudStep:
    """Positions before and after one displacement, and who left the ball."""

    pre: FloatArray
    post: FloatArray
    exited: BoolArray


def sample_uniform_ball(n: int, radius: float, rng: np.random.Generator) -> FloatArray:
    """Uniform points in a ball: isotropic directions, radius ~ R * U^(1/3)."""
    direction = rng.normal(size=(n, 3))
    direction /= np.linalg.norm(direction, axis=1, keepdims=True)
    r = radius * np.cbrt(rng.uniform(size=(n, 1)))
    return direction * r


def build_cloud(spec: CloudSpec, rng: np.random.Generator) -> ParticleCloud:
    n = spec.count()
    diameter = rng.uniform(*spec.diameter_range_m, size=n)
    return ParticleCloud(
        position=sample_uniform_ball(n, spec.radius_m, rng),
        diameter=diameter,
        visibility_distance=np.asarray(visibility_distance(diameter, spec.acuity_deg)),
        radius=spec.radius_m,
    )


def advect_cloud(cloud: ParticleCloud, displacement: FloatArray) -> CloudStep:
    """Shift all particles, respawn those that left, update the cloud in place."""
    pre = cloud.position.copy()
    post = pre + np.asarray(displacement, dtype=float)
    exited = np.linalg.norm(post, axis=1) > cloud.radius
    cloud.position = post.copy()
    cloud.position[exited] = -pre[exited]
    return CloudStep(pre=pre, post=post, exited=exited)


def visible_at(cloud: ParticleCloud, positions: FloatArray) -> BoolArray:
    """Within each particle's own visibility distance."""
    return np.linalg.norm(positions, axis=1) <= cloud.visibility_distance
