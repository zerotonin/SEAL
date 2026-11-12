# ╔══════════════════════════════════════════════════════════════════╗
# ║  sealsim — robustness                                            ║
# ║  « the calculations that answer the reviewer »                   ║
# ╠══════════════════════════════════════════════════════════════════╣
# ║  Three checks on what the proposition leaves out. Regional       ║
# ║  index: the balance inside azimuth bands of the visual field,    ║
# ║  where the angular factors no longer cancel. Bow flow: a dipole  ║
# ║  potential flow around the head displaces the nearest grains,    ║
# ║  which carry most of the translational sum. Ideal observer: the  ║
# ║  Cramer-Rao bound on heading for a decomposer with additive or   ║
# ║  with signal-dependent (Weber) noise, on the grains of a step.   ║
# ╚══════════════════════════════════════════════════════════════════╝

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd

from sealsim.cloud import CloudSpec, build_cloud
from sealsim.constants import (
    AZIMUTH_LIMIT_DEG,
    HEAD_RADIUS,
    FloatArray,
)
from sealsim.geometry import body_angular_velocity, tangent_basis, to_spherical, unit_vectors
from sealsim.opticflow import FlowField, estimate_foe, foe_heading_error, fov_mask
from sealsim.simulate import StepResult


# ┌────────────────────────────────────────────────────────────┐
# │ Regional index  « azimuth bands of the field »             │
# └────────────────────────────────────────────────────────────┘
@dataclass(frozen=True)
class AzimuthBand:
    name: str
    low_deg: float
    high_deg: float


DEFAULT_BANDS: tuple[AzimuthBand, ...] = (
    AzimuthBand("frontal", 0.0, 30.0),
    AzimuthBand("oblique", 30.0, 60.0),
    AzimuthBand("lateral", 60.0, AZIMUTH_LIMIT_DEG.value),
)


def regional_index(result: StepResult,
                   bands: tuple[AzimuthBand, ...] = DEFAULT_BANDS) -> pd.DataFrame:
    """Translation-rotation index per azimuth band of one decomposed step."""
    trans, rot = result.components["translation"], result.components["rotation"]
    common = result.field.in_fov & trans.in_fov & rot.in_fov
    azimuth = np.abs(np.rad2deg(np.asarray(trans.azimuth)))
    rows = []
    for band in bands:
        use = common & (azimuth >= band.low_deg) & (azimuth < band.high_deg)
        t = float(np.asarray(trans.magnitude)[use].sum())
        r = float(np.asarray(rot.magnitude)[use].sum())
        index = (t - r) / (t + r) if t + r > 0 else float("nan")
        rows.append({"band": band.name, "n": int(use.sum()), "index": index,
                     "translation_sum": t, "rotation_sum": r})
    return pd.DataFrame(rows)


def instant_regional_index(spec: CloudSpec, speed_mps: float, yaw_degps: float,
                           bands: tuple[AzimuthBand, ...] = DEFAULT_BANDS,
                           seed: int = 0) -> pd.DataFrame:
    """The same index from instantaneous flow rates, free of the sampling step."""
    u, r = _visible_grains(spec, seed)
    velocity = np.array([speed_mps, 0.0, 0.0])
    omega = body_angular_velocity(np.array([np.deg2rad(yaw_degps), 0.0, 0.0]))
    trans = np.linalg.norm(_angular_flow(u, r, np.broadcast_to(-velocity, u.shape)), axis=1)
    rot = np.linalg.norm(np.cross(omega, u), axis=1)
    _, az, el = to_spherical(u)
    azimuth = np.abs(np.rad2deg(az))
    rows = []
    for band in bands:
        use = fov_mask(az, el) & (azimuth >= band.low_deg) & (azimuth < band.high_deg)
        t, rr = float(trans[use].sum()), float(rot[use].sum())
        rows.append({"band": band.name, "n": int(use.sum()),
                     "index": (t - rr) / (t + rr) if t + rr > 0 else float("nan"),
                     "translation_sum": t, "rotation_sum": rr})
    return pd.DataFrame(rows)


def _visible_grains(spec: CloudSpec, seed: int,
                    exclude_centre: FloatArray | None = None,
                    exclude_radius: float = 0.0) -> tuple[FloatArray, FloatArray]:
    """Directions and distances of the grains within their own reach."""
    cloud = build_cloud(spec, np.random.default_rng(seed))
    r = np.linalg.norm(cloud.position, axis=1)
    keep = r <= cloud.visibility_distance
    if exclude_centre is not None:
        keep &= np.linalg.norm(cloud.position - exclude_centre, axis=1) > exclude_radius
    return cloud.position[keep] / r[keep, None], r[keep]


def band_critical_ratio(band: AzimuthBand, full_sphere_ratio: float,
                        rng: np.random.Generator, n: int = 200_000) -> float:
    """Predicted crossing in a band: N_c E_band[sin phi] / E_band[sin psi].

    Heading straight ahead, rotation about the yaw axis; directions isotropic,
    restricted to the band and to the seal's elevation range.
    """
    u = unit_vectors(rng.normal(size=(n, 3)))
    _, az, el = to_spherical(u)
    in_band = (np.abs(np.rad2deg(az)) >= band.low_deg) & (np.abs(np.rad2deg(az)) < band.high_deg)
    use = in_band & fov_mask(az, el)
    sin_phi = np.sqrt(1.0 - u[use, 0] ** 2)
    sin_psi = np.sqrt(1.0 - u[use, 2] ** 2)
    return float(full_sphere_ratio * sin_phi.mean() / sin_psi.mean())


# ┌────────────────────────────────────────────────────────────┐
# │ Bow flow  « dipole around the head »                       │
# └────────────────────────────────────────────────────────────┘
@dataclass(frozen=True)
class BowFlowBias:
    body_radius_m: float
    reach_m: float
    translational_gain: float      # mean |T| with dipole over without
    index_without: float
    index_with: float
    foe_error_deg: float           # FOE of the translational field with dipole
    apparent_rotation_degps: float  # best-fit rotation of the dipole-induced flow
    n_grains: int


def dipole_relative_velocity(positions: FloatArray, velocity: FloatArray,
                             body_radius: float, centre: FloatArray) -> FloatArray:
    """Water velocity relative to a sphere moving at ``velocity`` through still water.

    Potential flow: u = -V + (a^3 / 2 s^3) [3 (V . s_hat) s_hat - V], with s the offset
    from the sphere's centre. Grains ride with the water, so this is what the eye sees.
    """
    s = positions - centre
    dist = np.linalg.norm(s, axis=1, keepdims=True)
    s_hat = s / dist
    radial = (s_hat @ velocity)[:, None] * s_hat
    return -velocity + (body_radius**3 / (2.0 * dist**3)) * (3.0 * radial - velocity)


def bow_flow_bias(spec: CloudSpec, velocity_body: FloatArray, yaw_degps: float,
                  body_radius_m: float = HEAD_RADIUS.value, seed: int = 0) -> BowFlowBias:
    """Instantaneous flow of the visible grains with and without the head's bow flow.

    The eye sits at the front pole of a sphere of radius ``body_radius_m`` centred
    ``body_radius_m`` behind it; grains inside the sphere are discarded. The apparent
    rotation is what a decomposer with one free depth per grain and the true heading
    attributes to rotation when it is shown the bow-flow field.
    """
    centre = np.array([-body_radius_m, 0.0, 0.0])
    u, r = _visible_grains(spec, seed, centre, body_radius_m)
    velocity = np.asarray(velocity_body, dtype=float)
    omega = body_angular_velocity(np.array([np.deg2rad(yaw_degps), 0.0, 0.0]))
    plain = _angular_flow(u, r, np.broadcast_to(-velocity, u.shape))
    with_bow = _angular_flow(u, r, dipole_relative_velocity(u * r[:, None], velocity,
                                                            body_radius_m, centre))
    rotation = -np.cross(omega, u)
    field = _instant_field(u, r, with_bow)
    in_fov = field.in_fov
    mag = lambda f: np.linalg.norm(f, axis=1)[in_fov].sum()  # noqa: E731
    t0, t1, rr = mag(plain), mag(with_bow), mag(rotation)
    return BowFlowBias(
        body_radius_m=body_radius_m, reach_m=spec.radius_m,
        translational_gain=float(t1 / t0),
        index_without=float((t0 - rr) / (t0 + rr)), index_with=float((t1 - rr) / (t1 + rr)),
        foe_error_deg=float(np.rad2deg(foe_heading_error(estimate_foe(field), velocity))),
        apparent_rotation_degps=float(np.rad2deg(_fit_rotation(u[in_fov], with_bow[in_fov],
                                                                velocity))),
        n_grains=int(in_fov.sum()),
    )


def _angular_flow(u: FloatArray, r: FloatArray, relative_velocity: FloatArray) -> FloatArray:
    """Angular velocity of a direction: the transverse part of the motion over r."""
    radial = np.einsum("ij,ij->i", relative_velocity, u)[:, None] * u
    return (relative_velocity - radial) / r[:, None]


def _instant_field(u: FloatArray, r: FloatArray, flow: FloatArray) -> FlowField:
    magnitude = np.linalg.norm(flow, axis=1)
    with np.errstate(invalid="ignore", divide="ignore"):
        tangent = np.where(magnitude[:, None] > 0, flow / magnitude[:, None], 0.0)
    _, az, el = to_spherical(u)
    return FlowField(azimuth=az, elevation=el, flow=flow, magnitude=magnitude, tangent=tangent,
                     direction=u, distance=r, valid=np.isfinite(magnitude))


def _fit_rotation(u: FloatArray, flow: FloatArray, velocity: FloatArray) -> float:
    """|omega| from a least-squares fit of one inverse depth per grain plus one rotation.

    Columns: -(I - u u^T) h for grain i's inverse depth, [u_i]x for omega; rows: the
    three flow components of every grain. Returns the fitted rotation rate [rad/s].
    """
    n = u.shape[0]
    h = velocity / np.linalg.norm(velocity)
    design = np.zeros((3 * n, n + 3))
    trans_template = -(h[None, :] - (u @ h)[:, None] * u)
    for i in range(n):
        design[3 * i:3 * i + 3, i] = trans_template[i]
        design[3 * i:3 * i + 3, n:] = _skew(u[i])
    solution, *_ = np.linalg.lstsq(design, flow.reshape(-1), rcond=None)
    return float(np.linalg.norm(solution[n:]))


def _skew(v: FloatArray) -> FloatArray:
    return np.array([[0.0, -v[2], v[1]], [v[2], 0.0, -v[0]], [-v[1], v[0], 0.0]])


# ┌────────────────────────────────────────────────────────────┐
# │ Ideal observer  « Cramer-Rao bound on heading »            │
# └────────────────────────────────────────────────────────────┘
@dataclass(frozen=True)
class ObserverNoise:
    """Flow-vector noise: sigma^2 = additive^2 + (weber * |flow|)^2, in rad/s."""

    additive_radps: float = 0.1
    weber_fraction: float = 0.0


def heading_crb_deg(directions: FloatArray, distances: FloatArray, velocity: FloatArray,
                    omega: FloatArray, noise: ObserverNoise) -> float:
    """Cramer-Rao bound (degrees) on heading for an observer that also fits rotation
    and one unknown inverse depth per grain.

    The flow model f_i = -mu_i (I - u u^T) h - omega x u_i is linear in mu_i and
    omega, so with additive noise the bound does not depend on omega at all. With
    Weber noise the rotational flow inflates every grain's noise and the bound rises.
    """
    speed = float(np.linalg.norm(velocity))
    h = velocity / speed
    u = np.asarray(directions, dtype=float)
    mu = speed / np.asarray(distances, dtype=float)
    flow = -mu[:, None] * (h - (u @ h)[:, None] * u) - np.cross(omega, u)
    sigma2 = noise.additive_radps**2 + (noise.weber_fraction * np.linalg.norm(flow, axis=1))**2
    _, az, el = to_spherical(u)
    e1, e2 = tangent_basis(az, el)
    basis = np.stack([e1, e2], axis=1)                              # (n, 2, 3)
    d_h = _heading_tangents(h)                                      # (3, 2)
    proj = np.eye(3)[None] - u[:, :, None] * u[:, None, :]          # (n, 3, 3)
    j_h = -mu[:, None, None] * (proj @ d_h)                         # (n, 3, 2)
    j_w = np.stack([_skew(row) for row in u])                       # (n, 3, 3)
    j_mu = -(proj @ h)                                              # (n, 3)
    g = np.einsum("nab,nbc->nac", basis, np.concatenate([j_h, j_w], axis=2))  # (n, 2, 5)
    b = np.einsum("nab,nb->na", basis, j_mu)                        # (n, 2)
    w = 1.0 / sigma2
    fim = np.einsum("n,nac,nad->cd", w, g, g)
    cross = np.einsum("n,nac,na->nc", w, g, b)
    c = np.einsum("n,na,na->n", w, b, b)
    fim -= np.einsum("nc,nd,n->cd", cross, cross, 1.0 / c)
    cov = np.linalg.inv(fim)
    return float(np.rad2deg(np.sqrt(cov[0, 0] + cov[1, 1])))


def _heading_tangents(h: FloatArray) -> FloatArray:
    """Two unit vectors spanning the directions in which the heading can change."""
    _, az, el = to_spherical(h[None])
    e1, e2 = tangent_basis(az, el)
    return np.stack([e1[0], e2[0]], axis=1)


def observer_errors(result: StepResult, noises: dict[str, ObserverNoise]) -> dict[str, float]:
    """Heading errors [deg] on one step: the FOE template observer and each CRB."""
    trans = result.components["translation"]
    use = trans.in_fov & result.field.in_fov
    velocity = np.asarray(result.config.velocity, dtype=float)
    omega = body_angular_velocity(velocity[3:])
    out = {"foe_template": float(np.rad2deg(result.metrics.foe_error_rad))}
    for name, noise in noises.items():
        out[name] = heading_crb_deg(np.asarray(trans.direction)[use],
                                    np.asarray(trans.distance)[use], velocity[:3], omega, noise)
    return out
