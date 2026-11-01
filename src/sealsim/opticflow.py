# ╔══════════════════════════════════════════════════════════════════╗
# ║  sealsim — opticflow                                             ║
# ║  « what the retina sees and what can be read from it »           ║
# ╠══════════════════════════════════════════════════════════════════╣
# ║  Flow is the great-circle displacement of each particle          ║
# ║  direction between two samples, expressed in the body frame of   ║
# ║  each sample. Three odometry readouts are computed on every run  ║
# ║  (lab rule: run everything, decide later): the                   ║
# ║  focus-of-expansion heading error, the Spearman correlation      ║
# ║  between inverse flow magnitude and distance, and the            ║
# ║  translational/rotational flow index. Works on numpy and cupy    ║
# ║  fields; only the 3 x 3 eigenproblem of the focus estimate runs  ║
# ║  on the CPU.                                                     ║
# ╚══════════════════════════════════════════════════════════════════╝

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from scipy.spatial.transform import Rotation

from sealsim.backend import array_module_of, to_backend, to_numpy
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
    """Retinal flow from world-axis offsets before and after a step.

    Row vectors times the rotation matrix equal the inverse rotation applied to
    column vectors, so world offsets go to the body frame as ``p @ R``.
    """
    xp = array_module_of(pre_world)
    pre_body = pre_world @ to_backend(rot0.as_matrix(), xp)
    post_body = post_world @ to_backend(rot1.as_matrix(), xp)
    r0, az, el = to_spherical(pre_body)
    r1 = xp.linalg.norm(post_body, axis=1)
    magnitude, tangent, flow = great_circle_flow(pre_body, post_body)
    return FlowField(
        azimuth=az, elevation=el, flow=flow, magnitude=magnitude, tangent=tangent,
        direction=unit_vectors(pre_body), distance=0.5 * (r0 + r1),
        valid=xp.asarray(valid, dtype=bool) & xp.isfinite(magnitude),
    )


def fov_mask(azimuth: FloatArray, elevation: FloatArray) -> BoolArray:
    xp = array_module_of(azimuth)
    az_ok = xp.abs(azimuth) <= np.deg2rad(AZIMUTH_LIMIT_DEG.value)
    el_ok = (elevation >= np.deg2rad(ELEVATION_MIN_DEG.value)) & (
        elevation <= np.deg2rad(ELEVATION_MAX_DEG.value)
    )
    return az_ok & el_ok


# ┌────────────────────────────────────────────────────────────┐
# │ Readouts  « odometry quality from one flow field »         │
# └────────────────────────────────────────────────────────────┘
def estimate_foe(field: FlowField, mask: BoolArray | None = None) -> np.ndarray:
    """Direction all flow vectors radiate from, by least squares on great circles.

    Each flow vector lies on the great circle through its particle and the focus
    of expansion, so the plane normal n_i = u_i x t_i is orthogonal to the focus.
    The focus is the eigenvector of sum(n_i n_i^T) with the smallest eigenvalue,
    signed so that flow points away from it. Returns nan for fewer than two vectors.
    """
    xp = array_module_of(field.magnitude)
    mask = field.in_fov if mask is None else mask
    use = mask & (field.magnitude > 0)
    if int(use.sum()) < 2:
        return np.full(3, np.nan)
    u, t = field.direction[use], field.tangent[use]
    normals = unit_vectors(xp.cross(u, t))
    _, vectors = np.linalg.eigh(to_numpy(normals.T @ normals))
    foe = vectors[:, 0]
    foe_x = to_backend(foe, xp)
    radial = foe_x - xp.einsum("ij,j->i", u, foe_x)[:, None] * u
    if float(xp.einsum("ij,ij->", t, radial)) > 0:
        foe = -foe
    return foe


def foe_heading_error(foe: np.ndarray, translation_body: FloatArray) -> float:
    """Angle between the estimated focus and the true direction of travel [rad]."""
    heading = np.asarray(translation_body, dtype=float)[:3]
    if not np.all(np.isfinite(foe)) or np.linalg.norm(heading) == 0:
        return float("nan")
    return float(angle_between(foe, heading))


def rank_correlation(x: FloatArray, y: FloatArray) -> float:
    """Spearman rho for continuous data (ties are not averaged; they have measure zero)."""
    xp = array_module_of(x, y)
    rx, ry = _ranks(x, xp), _ranks(y, xp)
    rx, ry = rx - rx.mean(), ry - ry.mean()
    denominator = xp.sqrt((rx**2).sum() * (ry**2).sum())
    return float((rx * ry).sum() / denominator) if float(denominator) > 0 else float("nan")


def _ranks(values: FloatArray, xp) -> FloatArray:
    order = xp.argsort(values)
    ranks = xp.empty(values.shape[0], dtype=float)
    ranks[order] = xp.arange(values.shape[0], dtype=float)
    return ranks


def distance_rank_correlation(field: FlowField, mask: BoolArray | None = None) -> float:
    """Spearman rho between inverse flow magnitude and distance; 1 = perfect depth order."""
    mask = field.in_fov if mask is None else mask
    use = mask & (field.magnitude > 0)
    if int(use.sum()) < 3:
        return float("nan")
    return rank_correlation(1.0 / field.magnitude[use], field.distance[use])


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
    xp = array_module_of(field.magnitude)
    in_fov = field.in_fov
    magnitudes = field.magnitude[in_fov]
    has_any = int(magnitudes.shape[0]) > 0
    return FlowMetrics(
        n_particles=int(field.valid.shape[0]),
        n_valid=int(field.valid.sum()),
        n_in_fov=int(in_fov.sum()),
        mean_magnitude_rad=float(magnitudes.mean()) if has_any else float("nan"),
        median_magnitude_rad=float(xp.median(magnitudes)) if has_any else float("nan"),
        foe_error_rad=foe_heading_error(estimate_foe(field), translation_body),
        spearman_rho=distance_rank_correlation(field),
        trans_rot_index=translation_rotation_index(translation_sum, rotation_sum),
    )
