# ╔══════════════════════════════════════════════════════════════════╗
# ║  sealsim — opticflow                                             ║
# ║  « what the retina sees and what can be read from it »           ║
# ╠══════════════════════════════════════════════════════════════════╣
# ║  Flow is the great-circle displacement of each particle          ║
# ║  direction between two samples, expressed in the body frame of   ║
# ║  each sample. Three odometry readouts are computed on every run  ║
# ║  (lab rule: run everything, decide later): the                   ║
# ║  focus-of-expansion heading error, the Spearman correlation      ║
# ║  between 1/ flow and distance, and the translational/rotational  ║
# ║  flow index.                                                     ║
# ╚══════════════════════════════════════════════════════════════════╝

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from scipy.spatial.transform import Rotation
from scipy.stats import spearmanr

from sealsim.constants import (
    AZIMUTH_LIMIT_DEG,
    ELEVATION_MAX_DEG,
    ELEVATION_MIN_DEG,
    BoolArray,
    FloatArray,
)
from sealsim.geometry import angle_between, great_circle_flow, to_spherical, unit_vectors


# ┌────────────────────────────────────────────────────────────┐
# │ Flow field  « per-particle retinal displacement »          │
# └────────────────────────────────────────────────────────────┘
@dataclass
class FlowField:
    azimuth: FloatArray
    elevation: FloatArray
    flow: FloatArray
    magnitude: FloatArray
    tangent: FloatArray
    direction: FloatArray
    distance: FloatArray
    valid: BoolArray

    @property
    def in_fov(self) -> BoolArray:
        return self.valid & fov_mask(self.azimuth, self.elevation)


def compute_flow(
    pre_world: FloatArray,
    post_world: FloatArray,
    rot0: Rotation,
    rot1: Rotation,
    valid: BoolArray,
) -> FlowField:
    """Retinal flow from world-axis offsets before and after a step."""
    pre_body = rot0.inv().apply(pre_world)
    post_body = rot1.inv().apply(post_world)
    r0, az, el = to_spherical(pre_body)
    r1 = np.linalg.norm(post_body, axis=1)
    magnitude, tangent, flow = great_circle_flow(pre_body, post_body)
    return FlowField(
        azimuth=az, elevation=el, flow=flow, magnitude=magnitude, tangent=tangent,
        direction=unit_vectors(pre_body), distance=0.5 * (r0 + r1),
        valid=np.asarray(valid, dtype=bool) & np.isfinite(magnitude),
    )


def fov_mask(azimuth: FloatArray, elevation: FloatArray) -> BoolArray:
    az_ok = np.abs(azimuth) <= np.deg2rad(AZIMUTH_LIMIT_DEG.value)
    el_ok = (elevation >= np.deg2rad(ELEVATION_MIN_DEG.value)) & (
        elevation <= np.deg2rad(ELEVATION_MAX_DEG.value)
    )
    return az_ok & el_ok


# ┌────────────────────────────────────────────────────────────┐
# │ Readouts  « odometry quality from one flow field »         │
# └────────────────────────────────────────────────────────────┘
def estimate_foe(field: FlowField, mask: BoolArray | None = None) -> FloatArray:
    """Direction all flow vectors radiate from, by least squares on great circles.

    Each flow vector lies on the great circle through its particle and the focus
    of expansion, so the plane normal n_i = u_i x t_i is orthogonal to the focus.
    The focus is the eigenvector of sum(n_i n_i^T) with the smallest eigenvalue,
    signed so that flow points away from it. Returns nan for fewer than two vectors.
    """
    mask = field.in_fov if mask is None else mask
    use = mask & (field.magnitude > 0)
    if use.sum() < 2:
        return np.full(3, np.nan)
    u, t = field.direction[use], field.tangent[use]
    normals = unit_vectors(np.cross(u, t))
    _, vectors = np.linalg.eigh(normals.T @ normals)
    foe = vectors[:, 0]
    radial = foe - np.einsum("ij,j->i", u, foe)[:, None] * u
    if np.einsum("ij,ij->", t, radial) > 0:
        foe = -foe
    return foe


def foe_heading_error(foe: FloatArray, translation_body: FloatArray) -> float:
    """Angle between the estimated focus and the true direction of travel [rad]."""
    heading = np.asarray(translation_body, dtype=float)[:3]
    if not np.all(np.isfinite(foe)) or np.linalg.norm(heading) == 0:
        return float("nan")
    return float(angle_between(foe, heading))


def distance_rank_correlation(field: FlowField, mask: BoolArray | None = None) -> float:
    """Spearman rho between inverse flow magnitude and distance; 1 = perfect depth order."""
    mask = field.in_fov if mask is None else mask
    use = mask & (field.magnitude > 0)
    if use.sum() < 3:
        return float("nan")
    rho = spearmanr(1.0 / field.magnitude[use], field.distance[use]).statistic
    return float(rho)


def translation_rotation_index(translation_sum: float, rotation_sum: float) -> float:
    """(T - R) / (T + R) of summed flow magnitudes; +1 pure translation, -1 pure rotation."""
    total = translation_sum + rotation_sum
    if total == 0:
        return float("nan")
    return float((translation_sum - rotation_sum) / total)


@dataclass(frozen=True)
class FlowMetrics:
    n_particles: int
    n_valid: int
    n_in_fov: int
    mean_magnitude_rad: float
    median_magnitude_rad: float
    foe_error_rad: float
    spearman_rho: float
    trans_rot_index: float

    def as_dict(self) -> dict[str, float | int]:
        return dict(self.__dict__)


def summarise(
    field: FlowField,
    translation_body: FloatArray,
    translation_sum: float = float("nan"),
    rotation_sum: float = float("nan"),
) -> FlowMetrics:
    in_fov = field.in_fov
    magnitudes = field.magnitude[in_fov]
    return FlowMetrics(
        n_particles=int(field.valid.size),
        n_valid=int(field.valid.sum()),
        n_in_fov=int(in_fov.sum()),
        mean_magnitude_rad=float(magnitudes.mean()) if magnitudes.size else float("nan"),
        median_magnitude_rad=float(np.median(magnitudes)) if magnitudes.size else float("nan"),
        foe_error_rad=foe_heading_error(estimate_foe(field), translation_body),
        spearman_rho=distance_rank_correlation(field),
        trans_rot_index=translation_rotation_index(translation_sum, rotation_sum),
    )
