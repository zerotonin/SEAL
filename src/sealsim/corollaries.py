# ╔══════════════════════════════════════════════════════════════════╗
# ║  sealsim — corollaries                                           ║
# ║  « the law beyond the uniform ball: moments, horizons, time »    ║
# ╠══════════════════════════════════════════════════════════════════╣
# ║  The proposition gives Omega_crit = (3/2) v E[d^2]/E[d^3] for    ║
# ║  every distribution of reaches. This module evaluates that form  ║
# ║  for arbitrary grain-size samples (Sauter mean diameter), caps   ║
# ║  the reach at a contrast horizon (attenuation regime), and puts  ║
# ║  the law in its time form (turn per reach crossing) and as a     ║
# ║  speed estimator (flow over angular size). Pure numpy, no        ║
# ║  simulation.                                                     ║
# ╚══════════════════════════════════════════════════════════════════╝

from __future__ import annotations

import numpy as np

from sealsim.cloud import visibility_distance
from sealsim.constants import (
    ACUITY_SINGLE_TARGET,
    CONTRAST_INHERENT,
    CONTRAST_THRESHOLD,
    FloatArray,
)

ISOTROPIC_MEAN_SIN = np.pi / 4.0


# ┌────────────────────────────────────────────────────────────┐
# │ Grain-size samples  « uniform, log-normal, Junge »         │
# └────────────────────────────────────────────────────────────┘
def uniform_diameters(low_m: float, high_m: float, n: int,
                      rng: np.random.Generator) -> FloatArray:
    """Diameters uniform in [low, high]: the preset of the main simulations."""
    return rng.uniform(low_m, high_m, size=n)


def lognormal_diameters(median_m: float, geometric_sd: float, n: int,
                        rng: np.random.Generator) -> FloatArray:
    """Log-normal diameters, the usual fit to flocs and marine snow."""
    return rng.lognormal(np.log(median_m), np.log(geometric_sd), size=n)


def junge_diameters(low_m: float, high_m: float, slope: float, n: int,
                    rng: np.random.Generator) -> FloatArray:
    """Power-law number spectrum dN/dd ~ d^-slope between two cut-offs (Junge).

    Inverse transform sampling; a slope of exactly 1 is excluded.
    """
    if slope == 1.0:
        raise ValueError("slope 1 needs the logarithmic form; use 1.001 or 0.999")
    k = 1.0 - slope
    u = rng.uniform(size=n)
    return (low_m**k + u * (high_m**k - low_m**k)) ** (1.0 / k)


# ┌────────────────────────────────────────────────────────────┐
# │ Moments and the law  « Sauter form, reach form »           │
# └────────────────────────────────────────────────────────────┘
def sauter_mean_diameter(diameters_m: FloatArray) -> float:
    """D[3,2] = E[d^3] / E[d^2], the volume-to-surface mean of the sample."""
    d = np.asarray(diameters_m, dtype=float)
    return float(np.mean(d**3) / np.mean(d**2))


def critical_rate_from_reaches(speed_mps: float, reaches_m: FloatArray) -> float:
    """Omega_crit = (3/2) v E[d^2] / E[d^3] over any sample of reaches [rad/s]."""
    d = np.asarray(reaches_m, dtype=float)
    return float(1.5 * speed_mps * np.mean(d**2) / np.mean(d**3))


def critical_rate(speed_mps: float, diameters_m: FloatArray,
                  acuity_deg: float = ACUITY_SINGLE_TARGET.value,
                  horizon_m: float | None = None) -> float:
    """Critical rotation rate [rad/s] for a grain sample, optionally under a horizon."""
    return critical_rate_from_reaches(speed_mps,
                                      effective_reach(diameters_m, acuity_deg, horizon_m))


def critical_rate_sauter(speed_mps: float, sauter_m: FloatArray | float,
                         acuity_deg: float = ACUITY_SINGLE_TARGET.value) -> FloatArray | float:
    """The acuity-limited law in Sauter form: Omega_crit = 3 v tan(theta) / (2 D32)."""
    return 1.5 * speed_mps * np.tan(np.deg2rad(acuity_deg)) / np.asarray(sauter_m, dtype=float)


def critical_ratio_uniform(q: float) -> float:
    """Omega_crit R / v for reaches uniform on [qR, R]: 2 (1 - q^3) / (1 - q^4)."""
    return float(2.0 * (1.0 - q**3) / (1.0 - q**4))


def rotation_ratio(omega_radps: float, reach_m: float, speed_mps: float) -> float:
    """The dimensionless rotation ratio N = Omega R / v."""
    return float(omega_radps * reach_m / speed_mps)


# ┌────────────────────────────────────────────────────────────┐
# │ Contrast horizon  « the attenuation regime »               │
# └────────────────────────────────────────────────────────────┘
def contrast_horizon(attenuation_per_m: float,
                     inherent_contrast: float = CONTRAST_INHERENT.value,
                     threshold_contrast: float = CONTRAST_THRESHOLD.value) -> float:
    """Koschmieder range: distance at which C0 exp(-c r) falls to the threshold."""
    return float(np.log(inherent_contrast / threshold_contrast) / attenuation_per_m)


def attenuation_for_horizon(horizon_m: float,
                            inherent_contrast: float = CONTRAST_INHERENT.value,
                            threshold_contrast: float = CONTRAST_THRESHOLD.value) -> float:
    """Beam attenuation coefficient [1/m] that puts the contrast horizon at ``horizon_m``."""
    return float(np.log(inherent_contrast / threshold_contrast) / horizon_m)


def effective_reach(diameters_m: FloatArray, acuity_deg: float,
                    horizon_m: float | None = None) -> FloatArray:
    """Each grain's reach: its acuity reach, cut at the contrast horizon if given."""
    reach = np.asarray(visibility_distance(diameters_m, acuity_deg), dtype=float)
    if horizon_m is None:
        return reach
    return np.minimum(reach, horizon_m)


def horizon_at_turn_rate(speed_mps: float, omega_radps: float) -> float:
    """Horizon [m] at which a turn becomes critical in the attenuation limit, 3v/(2 Omega).

    Beyond this visibility rotation at ``omega_radps`` dominates the flow; a saccadic
    strategy pays. Below it translation dominates throughout the turn.
    """
    return float(1.5 * speed_mps / omega_radps)


def regime_crossover_horizon(diameters_m: FloatArray,
                             acuity_deg: float = ACUITY_SINGLE_TARGET.value) -> float:
    """Horizon above which no grain is cut: the acuity reach of the largest grain."""
    return float(np.max(visibility_distance(diameters_m, acuity_deg)))


# ┌────────────────────────────────────────────────────────────┐
# │ Time form and speed  « turn per crossing, odometer »       │
# └────────────────────────────────────────────────────────────┘
def crossing_time_s(reach_m: float, speed_mps: float) -> float:
    """Time in which the visible scene is replaced, R / v."""
    return float(reach_m / speed_mps)


def turn_per_crossing_deg(ratio: float) -> float:
    """The rotation ratio read as an angle: N radians turned per reach crossing."""
    return float(np.rad2deg(ratio))


def speed_from_flow(flow_radps: FloatArray, angular_size_rad: FloatArray,
                    mean_inverse_diameter_per_m: float,
                    mean_sin: float = ISOTROPIC_MEAN_SIN) -> float:
    """Speed through the water from per-grain flow over angular size.

    Flow over angular size equals v sin(phi) / a for every grain, so its mean over
    grains divided by E[sin phi] E[1/a] estimates v once the size prior is known.
    """
    per_grain = np.asarray(flow_radps, dtype=float) / np.asarray(angular_size_rad, dtype=float)
    return float(per_grain.mean() / (mean_sin * mean_inverse_diameter_per_m))


def speed_estimate_cv(diameters_m: FloatArray, n_grains: int, rng: np.random.Generator,
                      n_draws: int = 2000) -> float:
    """Coefficient of variation of the speed estimate from ``n_grains`` isotropic grains."""
    d = np.asarray(diameters_m, dtype=float)
    sizes = rng.choice(d, size=(n_draws, n_grains))
    cos_phi = rng.uniform(-1.0, 1.0, size=(n_draws, n_grains))
    per_grain = np.sqrt(1.0 - cos_phi**2) / sizes
    estimates = per_grain.mean(axis=1)
    return float(estimates.std(ddof=1) / estimates.mean())
