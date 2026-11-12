# ╔══════════════════════════════════════════════════════════════════╗
# ║  sealsim — figures_robustness                                    ║
# ║  « Figures 7 and 8: corollaries and reviewer checks »            ║
# ╠══════════════════════════════════════════════════════════════════╣
# ║  Fig. 7, the law for real suspended matter. A: Omega_crit against║
# ║  the Sauter mean diameter for five grain classes. B: the two     ║
# ║  regimes against the contrast horizon. C: speed precision        ║
# ║  against grains in view. Fig. 8, what the proposition leaves out.║
# ║  A: instantaneous index per azimuth band. B: bow-flow bias       ║
# ║  against head radius. C: heading error of three observers        ║
# ║  against the rotation ratio. Both run in seconds; no sweep data. ║
# ╚══════════════════════════════════════════════════════════════════╝

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from sealsim import corollaries as co
from sealsim import robustness as rb
from sealsim import viz
from sealsim.cloud import CloudSpec
from sealsim.constants import (
    ACUITY_SINGLE_TARGET,
    BODY_RADIUS,
    GRAIN_CLASSES,
    HEAD_RADIUS,
    PARTICLE_DIAMETER_RANGE_M,
    WONG,
    GrainClass,
)
from sealsim.dive import default_data_dir, load_pm5d, pm5d_velocity
from sealsim.figures import MAIN_DENSITY, critical_ratio, observed_rotation_rates_degps
from sealsim.geometry import to_spherical, unit_vectors
from sealsim.opticflow import fov_mask
from sealsim.simulate import StepConfig, run_step

SPEED = 1.5
FAST_SPEED = 3.7
SEEDS = tuple(range(10))
YAW_GRID_DEGPS = np.array([0, 30, 60, 90, 124, 167, 200, 250, 300, 350, 400, 456, 520,
                           600, 700, 800, 900], dtype=float)
MAIN_SPEC = CloudSpec(acuity_deg=ACUITY_SINGLE_TARGET.value,
                      diameter_range_m=PARTICLE_DIAMETER_RANGE_M,
                      number_density_per_m3=MAIN_DENSITY)
SLIP_PM = 11
NOISES = {"additive": rb.ObserverNoise(0.1, 0.0),
          "weber_0.1": rb.ObserverNoise(0.1, 0.1),
          "weber_0.3": rb.ObserverNoise(0.1, 0.3)}
COLOURS = {
    "sand": WONG["vermilion"], "silt": WONG["reddish_purple"], "flocs": WONG["bluish_green"],
    "marine snow": WONG["blue"], "Junge spectrum": WONG["orange"],
    "frontal": WONG["vermilion"], "oblique": WONG["orange"], "lateral": WONG["blue"],
    "foe_template": WONG["black"], "additive": WONG["bluish_green"],
    "weber_0.1": WONG["sky_blue"], "weber_0.3": WONG["reddish_purple"],
}
LABELS = {
    "foe_template": "FOE template, no rotation estimate",
    "additive": "ideal decomposer, additive noise",
    "weber_0.1": "ideal decomposer, Weber fraction 0.1",
    "weber_0.3": "ideal decomposer, Weber fraction 0.3",
    "frontal": "frontal, 0 to 30°", "oblique": "oblique, 30 to 60°",
    "lateral": "lateral, 60 to 104°",
}


def sample_class(grain_class: GrainClass, n: int, rng: np.random.Generator) -> np.ndarray:
    kind, p = grain_class.kind, grain_class.params
    if kind == "uniform":
        return co.uniform_diameters(p[0], p[1], n, rng)
    if kind == "lognormal":
        return co.lognormal_diameters(p[0], p[1], n, rng)
    if kind == "junge":
        return co.junge_diameters(p[0], p[1], p[2], n, rng)
    raise ValueError(f"unknown grain class kind {kind!r}")


def seal_turn_ratios(reach_m: float, speed: float = SPEED) -> tuple[float, float]:
    low, high = observed_rotation_rates_degps()
    return (co.rotation_ratio(np.deg2rad(low), reach_m, speed),
            co.rotation_ratio(np.deg2rad(high), reach_m, speed))


def fov_fraction(rng: np.random.Generator, n: int = 200_000) -> float:
    """Share of the sphere inside the seal's visual field."""
    _, az, el = to_spherical(unit_vectors(rng.normal(size=(n, 3))))
    return float(fov_mask(az, el).mean())


# ┌────────────────────────────────────────────────────────────┐
# │ Figure 7  « the law for real suspended matter »            │
# └────────────────────────────────────────────────────────────┘
def figure_7(results_dir: Path, tables_dir: Path, out_dir: Path) -> list[Path]:
    viz.apply_style()
    rng = np.random.default_rng(0)
    fig, (ax_a, ax_b, ax_c) = plt.subplots(1, 3, figsize=(viz.DOUBLE_COLUMN_IN,
                                                          0.34 * viz.DOUBLE_COLUMN_IN))
    parts = [_panel_sauter(ax_a, rng), _panel_horizon(ax_b, rng), _panel_speed(ax_c, rng)]
    for ax, label in zip((ax_a, ax_b, ax_c), "ABC"):
        viz.panel_label(ax, label)
    fig.tight_layout()
    return viz.save_figure(fig, "fig7_suspended_matter", out_dir,
                           pd.concat(parts, ignore_index=True))


def _panel_sauter(ax, rng: np.random.Generator) -> pd.DataFrame:
    theta = ACUITY_SINGLE_TARGET.value
    rows = []
    for grain_class in GRAIN_CLASSES:
        d = sample_class(grain_class, 200_000, rng)
        d32 = co.sauter_mean_diameter(d)
        rate = np.rad2deg(co.critical_rate(SPEED, d, theta))
        ax.scatter(d32 * 1e6, rate, color=COLOURS[grain_class.name], s=28, zorder=4,
                   edgecolor="black", linewidth=0.4, label=grain_class.name)
        rows.append({"panel": "A", "grain_class": grain_class.name, "sauter_um": d32 * 1e6,
                     "reach_max_m": float(co.regime_crossover_horizon(d, theta)),
                     "critical_rate_degps": rate, "speed_mps": SPEED})
    grid = np.logspace(1, 4, 100)
    for speed, style in ((SPEED, "-"), (FAST_SPEED, "--")):
        ax.plot(grid, np.rad2deg(co.critical_rate_sauter(speed, grid * 1e-6, theta)), style,
                color="black", lw=0.8, label=f"3v tanθ / (2 D[3,2]), {speed:g} m/s")
    low, high = observed_rotation_rates_degps()
    ax.axhspan(low, high, color=viz.COLOURS["neutral"], alpha=0.15, lw=0)
    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_xlabel("Sauter mean diameter D[3,2] [µm]")
    ax.set_ylabel(r"$\Omega_\mathrm{crit}$ [°/s]")
    ax.legend(frameon=False, fontsize=viz.FONT_SIZE - 2, loc="lower left")
    return pd.DataFrame(rows)


def _panel_horizon(ax, rng: np.random.Generator) -> pd.DataFrame:
    theta = ACUITY_SINGLE_TARGET.value
    horizons = np.logspace(np.log10(0.05), 1, 120)
    rows = []
    for name in ("sand", "marine snow"):
        grain_class = next(g for g in GRAIN_CLASSES if g.name == name)
        d = sample_class(grain_class, 100_000, rng)
        rates = np.rad2deg([co.critical_rate(SPEED, d, theta, horizon_m=h) for h in horizons])
        ax.plot(horizons, rates, color=COLOURS[name], label=name)
        rows += [{"panel": "B", "scene": name, "horizon_m": h, "critical_rate_degps": r}
                 for h, r in zip(horizons, rates)]
    structure = np.rad2deg(1.5 * SPEED / horizons)
    ax.plot(horizons, structure, color="black", lw=0.8, label="structure at the horizon")
    rows += [{"panel": "B", "scene": "structure", "horizon_m": h, "critical_rate_degps": r}
             for h, r in zip(horizons, structure)]
    low, high = observed_rotation_rates_degps()
    ax.axhspan(low, high, color=viz.COLOURS["neutral"], alpha=0.15, lw=0)
    switch = co.horizon_at_turn_rate(SPEED, np.deg2rad(low))
    ax.axvline(switch, color="black", linestyle=":", lw=0.8)
    ax.annotate(f"{switch:.1f} m", xy=(switch, 2000), xytext=(3, 0), textcoords="offset points",
                fontsize=viz.FONT_SIZE - 1)
    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_xlabel(r"contrast horizon $R_\mathrm{vis}$ [m]")
    ax.set_ylabel(r"$\Omega_\mathrm{crit}$ [°/s] at 1.5 m/s")
    ax.legend(frameon=False, fontsize=viz.FONT_SIZE - 2, loc="upper right")
    return pd.DataFrame(rows)


def _panel_speed(ax, rng: np.random.Generator) -> pd.DataFrame:
    counts = np.unique(np.logspace(1, 3.5, 12).astype(int))
    rows = []
    for name in ("sand", "flocs"):
        grain_class = next(g for g in GRAIN_CLASSES if g.name == name)
        d = sample_class(grain_class, 50_000, rng)
        cv = np.array([co.speed_estimate_cv(d, int(n), rng, n_draws=1000) for n in counts])
        ax.plot(counts, 100 * cv, marker="o", markersize=3, color=COLOURS[name], label=name)
        rows += [{"panel": "C", "grain_class": name, "n_grains": int(n), "cv_percent": 100 * c}
                 for n, c in zip(counts, cv)]
    reach = co.effective_reach(sample_class(GRAIN_CLASSES[0], 100_000, rng),
                               ACUITY_SINGLE_TARGET.value)
    in_view = MAIN_DENSITY * 4 / 3 * np.pi * float(np.mean(reach**3)) * fov_fraction(rng)
    ax.axvline(in_view, color=viz.COLOURS["neutral"], linestyle=":", lw=0.8)
    ax.annotate(f"{in_view:.0f} sand grains\nat {MAIN_DENSITY:g} m$^{{-3}}$",
                xy=(in_view, 30), xytext=(3, 0), textcoords="offset points",
                fontsize=viz.FONT_SIZE - 2)
    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_xlabel("grains in view")
    ax.set_ylabel("CV of the speed estimate [%]")
    ax.legend(frameon=False, fontsize=viz.FONT_SIZE - 2, loc="lower left")
    return pd.DataFrame(rows)


# ┌────────────────────────────────────────────────────────────┐
# │ Figure 8  « what the proposition leaves out »              │
# └────────────────────────────────────────────────────────────┘
def figure_8(results_dir: Path, tables_dir: Path, out_dir: Path) -> list[Path]:
    viz.apply_style()
    fig, (ax_a, ax_b, ax_c) = plt.subplots(1, 3, figsize=(viz.DOUBLE_COLUMN_IN,
                                                          0.34 * viz.DOUBLE_COLUMN_IN))
    parts = [_panel_bands(ax_a), _panel_bow_flow(ax_b), _panel_observers(ax_c)]
    for ax, label in zip((ax_a, ax_b, ax_c), "ABC"):
        viz.panel_label(ax, label)
    fig.tight_layout()
    return viz.save_figure(fig, "fig8_observers", out_dir, pd.concat(parts, ignore_index=True))


def _panel_bands(ax) -> pd.DataFrame:
    reach = MAIN_SPEC.radius_m
    rows = []
    for seed in SEEDS:
        for yaw in YAW_GRID_DEGPS:
            frame = rb.instant_regional_index(MAIN_SPEC, SPEED, yaw, seed=seed)
            frame["ratio"] = co.rotation_ratio(np.deg2rad(yaw), reach, SPEED)
            frame["seed"] = seed
            rows.append(frame)
    table = pd.concat(rows, ignore_index=True)
    summary = viz.plot_trend(ax, table, "ratio", "index", "band", COLOURS, LABELS)
    full = critical_ratio(*PARTICLE_DIAMETER_RANGE_M)
    rng = np.random.default_rng(1)
    predicted = {band.name: rb.band_critical_ratio(band, full, rng) for band in rb.DEFAULT_BANDS}
    for name, value in predicted.items():
        ax.axvline(value, color=COLOURS[name], linestyle=":", lw=1)
    ax.axvspan(*seal_turn_ratios(reach), color=viz.COLOURS["neutral"], alpha=0.15, lw=0)
    ax.axhline(0.0, color="black", lw=0.6)
    ax.set_xlabel(r"$\Omega\,R\,/\,v$")
    ax.set_ylabel("index, instantaneous flow")
    ax.legend(frameon=False, fontsize=viz.FONT_SIZE - 2, loc="upper right")
    summary["panel"] = "A"
    summary["predicted_crossing"] = summary["band"].map(predicted)
    return summary


def _panel_bow_flow(ax) -> pd.DataFrame:
    reach = MAIN_SPEC.radius_m
    radii = np.linspace(0.02 * reach, 0.5 * reach, 13)
    pm = load_pm5d(default_data_dir())
    slip_velocity = pm5d_velocity(pm, SLIP_PM)[:3]
    rows = []
    for radius in radii:
        for seed in SEEDS[:3]:
            thrust = rb.bow_flow_bias(MAIN_SPEC, (SPEED, 0.0, 0.0), 0.0, body_radius_m=radius,
                                      seed=seed)
            slip = rb.bow_flow_bias(MAIN_SPEC, slip_velocity, 0.0, body_radius_m=radius,
                                    seed=seed)
            rows.append({"body_radius_m": radius, "radius_over_reach": radius / reach,
                         "gain_thrust": thrust.translational_gain,
                         "gain_slip_pm": slip.translational_gain,
                         "foe_error_slip_pm_deg": slip.foe_error_deg,
                         "apparent_rotation_slip_pm_degps": slip.apparent_rotation_degps})
    table = pd.DataFrame(rows).groupby("radius_over_reach", as_index=False).mean()
    table.insert(0, "panel", "B")
    ax.plot(table["radius_over_reach"], table["gain_thrust"], color=WONG["vermilion"],
            marker="o", markersize=3, label="translational sum, pure thrust")
    ax.plot(table["radius_over_reach"], table["gain_slip_pm"], color=WONG["orange"],
            marker="o", markersize=3, label=f"translational sum, PM {SLIP_PM}")
    ax.set_xlabel("head radius / reach")
    ax.set_ylim(0.8, 1.02)
    ax.set_ylabel("with bow flow / without")
    twin = ax.twinx()
    twin.plot(table["radius_over_reach"], table["apparent_rotation_slip_pm_degps"],
              color=WONG["blue"], marker="s", markersize=3,
              label=f"apparent rotation, PM {SLIP_PM}")
    twin.set_ylabel("apparent rotation [°/s]", color=WONG["blue"])
    twin.tick_params(axis="y", colors=WONG["blue"])
    twin.spines["right"].set_visible(True)
    for value, name, dx in ((HEAD_RADIUS.value, "head", -2), (BODY_RADIUS.value, "trunk", 2)):
        ax.axvline(value / reach, color=viz.COLOURS["neutral"], linestyle=":", lw=0.8)
        ax.annotate(name, xy=(value / reach, 1.02), xytext=(dx, 0), textcoords="offset points",
                    fontsize=viz.FONT_SIZE - 2, ha="right" if dx < 0 else "left", va="top")
    handles = ax.get_legend_handles_labels()[0] + twin.get_legend_handles_labels()[0]
    ax.legend(handles=handles, frameon=False, fontsize=viz.FONT_SIZE - 2, loc="lower left",
              bbox_to_anchor=(0.0, 0.0))
    return pd.concat([table, bow_flow_per_pm(pm)], ignore_index=True)


def bow_flow_per_pm(pm: pd.DataFrame) -> pd.DataFrame:
    """Bow-flow bias of every PM at head radius, for the CSV companion and the text."""
    rows = []
    for pm_id in pm["pm_id"]:
        velocity = pm5d_velocity(pm, int(pm_id))
        if np.linalg.norm(velocity[:3]) == 0:
            continue
        bias = rb.bow_flow_bias(MAIN_SPEC, velocity[:3], np.rad2deg(velocity[3]),
                                body_radius_m=HEAD_RADIUS.value)
        rows.append({"panel": "B_pm", "pm_id": int(pm_id), "body_radius_m": HEAD_RADIUS.value,
                     "gain_thrust": bias.translational_gain,
                     "index_without": bias.index_without, "index_with": bias.index_with,
                     "foe_error_slip_pm_deg": bias.foe_error_deg,
                     "apparent_rotation_slip_pm_degps": bias.apparent_rotation_degps})
    return pd.DataFrame(rows)


def _panel_observers(ax) -> pd.DataFrame:
    reach = MAIN_SPEC.radius_m
    rows = []
    for seed in SEEDS:
        for yaw in YAW_GRID_DEGPS:
            cfg = StepConfig(velocity=(SPEED, 0.0, 0.0, np.deg2rad(yaw), 0.0, 0.0),
                             cloud=MAIN_SPEC, seed=seed)
            errors = rb.observer_errors(run_step(cfg), NOISES)
            ratio = co.rotation_ratio(np.deg2rad(yaw), reach, SPEED)
            rows += [{"observer": name, "ratio": ratio, "seed": seed, "error_deg": value}
                     for name, value in errors.items()]
    table = pd.DataFrame(rows)
    summary = viz.plot_trend(ax, table, "ratio", "error_deg", "observer", COLOURS, LABELS)
    field_crossing = critical_ratio(*PARTICLE_DIAMETER_RANGE_M) * 0.782 / 0.855
    ax.axvline(field_crossing, color="black", linestyle=":", lw=0.8)
    ax.axvspan(*seal_turn_ratios(reach), color=viz.COLOURS["neutral"], alpha=0.15, lw=0)
    ax.set_yscale("log")
    ax.set_ylim(0.05, 300)
    ax.set_xlabel(r"$\Omega\,R\,/\,v$")
    ax.set_ylabel("heading error [°]")
    ax.legend(frameon=False, fontsize=viz.FONT_SIZE - 3, loc="upper left", handlelength=1.5)
    summary["panel"] = "C"
    return summary


FIGURES = {"7": figure_7, "8": figure_8}
