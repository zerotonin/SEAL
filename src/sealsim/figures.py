# ╔══════════════════════════════════════════════════════════════════╗
# ║  sealsim — figures                                               ║
# ║  « manuscript figures from the collected sweep tables »          ║
# ╠══════════════════════════════════════════════════════════════════╣
# ║  Panel plan from the lab's manuscript note: cutouts in the main  ║
# ║  text, globes in the supplement. Fig. 2: three PM flow fields    ║
# ║  and the readouts per PM group. Fig. 3: one PM in clear and      ║
# ║  turbid water, readouts against particle density, both vision    ║
# ║  presets. Fig. 4: one PM under head, cross and following         ║
# ║  current and the index against current speed for saccades and    ║
# ║  fast translations. Supplement: globes, critical rotation,       ║
# ║  depth. Each figure returns the paths it wrote.                  ║
# ╚══════════════════════════════════════════════════════════════════╝

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import yaml
from scipy.optimize import minimize_scalar

from sealsim import stats, viz
from sealsim.dive import default_data_dir, load_pm5d
from sealsim.geometry import spherical_to_unit, tangent_basis, to_spherical
from sealsim.opticflow import FlowField, estimate_foe
from sealsim.results import load_metadata

PM_GROUPS: dict[int, str] = {
    1: "fast_translation", 2: "fast_translation", 3: "fast_translation",
    4: "slow_translation", 5: "slow_translation", 6: "slow_translation",
    7: "slow_translation", 8: "slow_translation", 9: "slow_translation",
    10: "rotation", 11: "rotation", 12: "rotation", 13: "rotation",
}
SACCADES = (10, 11)
FAST_TRANSLATIONS = (2, 3)
EXAMPLE_PMS = {"fast_translation": 2, "slow_translation": 4, "rotation": 10}
GROUP_ORDER = ("fast_translation", "slow_translation", "rotation")
MAIN_VISION = "north_sea"
MAIN_DENSITY = 10_000.0
MAIN_CURRENT = 0.6


# ┌────────────────────────────────────────────────────────────┐
# │ Data access  « tables, one job's field, overlays »         │
# └────────────────────────────────────────────────────────────┘
def load_table(tables_dir: Path, experiment: str) -> pd.DataFrame:
    table = pd.read_parquet(tables_dir / f"{experiment}.parquet")
    if "condition.pm_id" in table:
        table["pm_group"] = table["condition.pm_id"].map(PM_GROUPS)
    if "metrics.foe_error_rad" in table:
        table["foe_error_deg"] = np.rad2deg(table["metrics.foe_error_rad"])
    return table


def find_job(table: pd.DataFrame, **condition) -> pd.Series:
    """Row of the first job matching every given condition column."""
    mask = np.ones(len(table), dtype=bool)
    for key, value in condition.items():
        column = table[f"condition.{key}"]
        mask &= (np.isclose(column, value) if np.issubdtype(column.dtype, np.number)
                 else column == value)
    hits = table[mask]
    if hits.empty:
        raise KeyError(f"no job with {condition}")
    return hits.iloc[0]


def load_field(results_dir: Path, experiment: str, job: pd.Series) -> pd.DataFrame:
    stem = Path(job["file"]).stem
    return pd.read_parquet(results_dir / experiment / f"{stem}.parquet")


def field_marks(results_dir: Path, experiment: str, job: pd.Series,
                frame: pd.DataFrame) -> viz.FlowPanelMarks:
    """Focus of expansion re-estimated from the saved field, heading from the config."""
    meta = load_metadata(results_dir / experiment / Path(job["file"]).name)
    velocity = np.asarray(meta["config"]["velocity"], dtype=float)
    heading = None
    if np.linalg.norm(velocity[:3]) > 0:
        _, h_az, h_el = to_spherical(velocity[:3])
        heading = (float(h_az), float(h_el))
    foe = estimate_foe(_field_from_frame(frame))
    if np.all(np.isfinite(foe)):
        _, f_az, f_el = to_spherical(foe)
        return viz.FlowPanelMarks(foe=(float(f_az), float(f_el)), heading=heading)
    return viz.FlowPanelMarks(foe=None, heading=heading)


def _field_from_frame(frame: pd.DataFrame) -> FlowField:
    az, el = frame["azimuth_rad"].to_numpy(), frame["elevation_rad"].to_numpy()
    flow = frame[["flow_azimuth_rad", "flow_elevation_rad"]].to_numpy()
    magnitude = frame["magnitude_rad"].to_numpy()
    e_az, e_el = tangent_basis(az, el)
    with np.errstate(invalid="ignore", divide="ignore"):
        tangent = (flow[:, :1] * e_az + flow[:, 1:] * e_el) / magnitude[:, None]
    tangent = np.nan_to_num(tangent)
    return FlowField(
        azimuth=az, elevation=el, flow=flow, magnitude=magnitude, tangent=tangent,
        direction=spherical_to_unit(az, el), distance=frame["distance_m"].to_numpy(),
        valid=frame["valid"].to_numpy(),
    )


def _title(meta_row: pd.Series, extra: str = "") -> str:
    pm = int(meta_row["condition.pm_id"]) if "condition.pm_id" in meta_row else None
    base = f"PM {pm}, {viz.LABELS.get(PM_GROUPS.get(pm, ''), '')}" if pm else ""
    return f"{base}, {extra}".strip(", ") if extra else base


def _flow_panel(ax, results_dir: Path, experiment: str, job: pd.Series, colour: str,
                title: str) -> None:
    frame = load_field(results_dir, experiment, job)
    n_shown = viz.plot_flow_mercator(ax, frame, field_marks(results_dir, experiment, job,
                                                            frame), colour=colour)
    viz.shown_title(ax, title, n_shown, int(frame["valid"].sum()))


# ┌────────────────────────────────────────────────────────────┐
# │ Figure 2  « prototypical movements and their readouts »    │
# └────────────────────────────────────────────────────────────┘
def figure_2(results_dir: Path, tables_dir: Path, out_dir: Path) -> list[Path]:
    viz.apply_style()
    table = load_table(tables_dir, "pm_radius_density")
    main = table[(table["condition.vision"] == MAIN_VISION)
                 & np.isclose(table["condition.number_density_per_m3"], MAIN_DENSITY)]
    fig, axes = plt.subplots(2, 3, figsize=(viz.DOUBLE_COLUMN_IN, 0.62 * viz.DOUBLE_COLUMN_IN),
                             gridspec_kw={"height_ratios": [1.0, 0.9]})
    for ax, (group, pm) in zip(axes[0], EXAMPLE_PMS.items()):
        job = find_job(main, pm_id=pm, replicate=0)
        _flow_panel(ax, results_dir, "pm_radius_density", job, viz.COLOURS[group],
                    _title(job, f"dt = {job['dt_s'] * 1e3:.0f} ms"))
    for label, ax in zip("A1 A2 A3".split(), axes[0]):
        viz.panel_label(ax, label)
    readouts = [("foe_error_deg", "foe_error_deg"), ("metrics.spearman_rho", "spearman_rho"),
                ("metrics.trans_rot_index", "trans_rot_index")]
    csv_parts, stat_parts = [], []
    for ax, label, (column, key) in zip(axes[1], "B1 B2 B3".split(), readouts):
        samples = [main.loc[main["pm_group"] == g, column].to_numpy() for g in GROUP_ORDER]
        viz.plot_raincloud(ax, samples, [viz.LABELS[g] for g in GROUP_ORDER],
                           [viz.COLOURS[g] for g in GROUP_ORDER])
        ax.set_xlabel(viz.LABELS[key])
        viz.panel_label(ax, label)
        csv_parts.append(main[["condition.pm_id", "pm_group", "condition.replicate", column]]
                         .rename(columns={column: key}).assign(readout=key))
        result = stats.compare_levels(main, column, "pm_group")
        if not result.empty:
            stat_parts.append(result.assign(readout=key))
    fig.tight_layout()
    paths = viz.save_figure(fig, "fig2_prototypical_movements", out_dir,
                            pd.concat(csv_parts, ignore_index=True))
    if stat_parts:
        paths.append(stats.save_stats(pd.concat(stat_parts, ignore_index=True),
                                      "fig2_stats_pm_groups", out_dir))
    return paths


# ┌────────────────────────────────────────────────────────────┐
# │ Figure 3  « turbidity »                                    │
# └────────────────────────────────────────────────────────────┘
def figure_3(results_dir: Path, tables_dir: Path, out_dir: Path) -> list[Path]:
    viz.apply_style()
    table = load_table(tables_dir, "pm_radius_density")
    densities = np.sort(table["condition.number_density_per_m3"].unique())
    clear, turbid = float(densities[0]), float(densities[-1])
    main = table[table["condition.vision"] == MAIN_VISION]
    pm = EXAMPLE_PMS["fast_translation"]

    fig = plt.figure(figsize=(viz.DOUBLE_COLUMN_IN, 0.9 * viz.DOUBLE_COLUMN_IN))
    grid = fig.add_gridspec(3, 2, height_ratios=[1.0, 0.8, 0.8])
    for col, (name, density) in enumerate([("clear", clear), ("turbid", turbid)]):
        ax = fig.add_subplot(grid[0, col])
        job = find_job(main, pm_id=pm, number_density_per_m3=density, replicate=0)
        _flow_panel(ax, results_dir, "pm_radius_density", job, viz.COLOURS[name],
                    _title(job, f"{density:g} m$^{{-3}}$ ({name} water)"))
        viz.panel_label(ax, f"A{col + 1}")

    csv_parts = []
    panels = [("B1", "foe_error_deg", "foe_error_deg"),
              ("B2", "metrics.spearman_rho", "spearman_rho"),
              ("C", "metrics.trans_rot_index", "trans_rot_index")]
    for (label, column, key), cell in zip(panels, [grid[1, 0], grid[1, 1], grid[2, 0]]):
        ax = fig.add_subplot(cell)
        summary = viz.plot_trend(ax, main, "condition.number_density_per_m3", column,
                                 "pm_group", viz.COLOURS, viz.LABELS, logx=True)
        ax.set_xlabel("particle number density [m$^{-3}$]")
        ax.set_ylabel(viz.LABELS[key])
        viz.panel_label(ax, label)
        csv_parts.append(summary.assign(readout=key, vision=MAIN_VISION))
    axes_last = fig.add_subplot(grid[2, 1])
    summary = viz.plot_trend(axes_last, table, "condition.number_density_per_m3",
                             "metrics.n_in_fov", "condition.vision", viz.COLOURS, viz.LABELS,
                             logx=True)
    axes_last.set_yscale("symlog", linthresh=1.0)
    axes_last.set_ylim(bottom=0.0)
    axes_last.set_xlabel("particle number density [m$^{-3}$]")
    axes_last.set_ylabel(viz.LABELS["n_in_fov"])
    axes_last.legend(frameon=False)
    viz.panel_label(axes_last, "D")
    csv_parts.append(summary.assign(readout="n_in_fov"))
    fig.axes[2].legend(frameon=False)
    fig.tight_layout()
    paths = viz.save_figure(fig, "fig3_turbidity", out_dir, pd.concat(csv_parts,
                                                                       ignore_index=True))
    result = stats.compare_levels(main, "foe_error_deg", "condition.number_density_per_m3",
                                  within="pm_group")
    if not result.empty:
        paths.append(stats.save_stats(result, "fig3_stats_density_levels", out_dir))
    return paths


# ┌────────────────────────────────────────────────────────────┐
# │ Figure 4  « currents »                                     │
# └────────────────────────────────────────────────────────────┘
def figure_4(results_dir: Path, tables_dir: Path, out_dir: Path) -> list[Path]:
    viz.apply_style()
    table = load_table(tables_dir, "currents")
    main = table[table["condition.vision"] == MAIN_VISION].copy()
    pm = EXAMPLE_PMS["fast_translation"]
    speeds = np.sort(main["condition.current_speed_mps"].unique())
    speed = MAIN_CURRENT if np.any(np.isclose(speeds, MAIN_CURRENT)) else float(speeds[-1])

    fig = plt.figure(figsize=(viz.DOUBLE_COLUMN_IN, 0.75 * viz.DOUBLE_COLUMN_IN))
    grid = fig.add_gridspec(2, 3, height_ratios=[1.0, 0.9])
    for col, direction in enumerate(("head", "cross", "follow")):
        ax = fig.add_subplot(grid[0, col])
        job = find_job(main, pm_id=pm, current_direction=direction, current_speed_mps=speed,
                       replicate=0)
        _flow_panel(ax, results_dir, "currents", job, viz.COLOURS[direction],
                    f"{viz.LABELS[direction]}, {speed:g} m/s" + ("" if col else
                                                                  f" (PM {pm})"))
        viz.panel_label(ax, f"A{'i' * (col + 1)}")

    main["movement"] = np.where(main["condition.pm_id"].isin(SACCADES), "saccades",
                                np.where(main["condition.pm_id"].isin(FAST_TRANSLATIONS),
                                         "fast translations", "other"))
    subset = main[main["movement"] != "other"]
    ax = fig.add_subplot(grid[1, :])
    colours = {"saccades": viz.COLOURS["rotation"],
               "fast translations": viz.COLOURS["fast_translation"]}
    csv_parts = []
    for direction, style in (("head", "-"), ("cross", "--"), ("follow", ":")):
        part = subset[subset["condition.current_direction"] == direction]
        summary = viz.plot_trend(ax, part, "condition.current_speed_mps",
                                 "metrics.trans_rot_index", "movement", colours,
                                 {k: f"{k}, {viz.LABELS[direction]}" for k in colours},
                                 linestyle=style)
        csv_parts.append(summary.assign(current_direction=direction))
    ax.set_xlabel("current speed [m/s]")
    ax.set_ylabel(viz.LABELS["trans_rot_index"])
    ax.legend(frameon=False, ncol=2)
    viz.panel_label(ax, "B")
    fig.tight_layout()
    paths = viz.save_figure(fig, "fig4_currents", out_dir, pd.concat(csv_parts,
                                                                      ignore_index=True))
    subset = subset.assign(cell=subset["movement"] + "|" + subset["condition.current_direction"])
    result = stats.compare_levels(subset, "metrics.trans_rot_index",
                                  "condition.current_speed_mps", within="cell")
    if not result.empty:
        paths.append(stats.save_stats(result, "fig4_stats_current_levels", out_dir))
    return paths


# ┌────────────────────────────────────────────────────────────┐
# │ Supplement  « globes, critical rotation, depth »           │
# └────────────────────────────────────────────────────────────┘
def figure_s1_globes(results_dir: Path, tables_dir: Path, out_dir: Path) -> list[Path]:
    viz.apply_style()
    table = load_table(tables_dir, "pm_radius_density")
    main = table[(table["condition.vision"] == MAIN_VISION)
                 & np.isclose(table["condition.number_density_per_m3"], MAIN_DENSITY)]
    fig = plt.figure(figsize=(viz.DOUBLE_COLUMN_IN, 0.4 * viz.DOUBLE_COLUMN_IN))
    rows = []
    for i, (group, pm) in enumerate(EXAMPLE_PMS.items()):
        ax = fig.add_subplot(1, 3, i + 1, projection="hammer")
        job = find_job(main, pm_id=pm, replicate=0)
        frame = load_field(results_dir, "pm_radius_density", job)
        n_shown = viz.plot_flow_hammer(ax, frame, field_marks(results_dir, "pm_radius_density",
                                                              job, frame),
                                       colour=viz.COLOURS[group])
        viz.shown_title(ax, _title(job), n_shown, int(frame["valid"].sum()))
        rows.append(frame.assign(pm_id=pm))
    fig.tight_layout()
    return viz.save_figure(fig, "figS1_globes", out_dir, pd.concat(rows, ignore_index=True))


def figure_5_critical_rotation(results_dir: Path, tables_dir: Path,
                               out_dir: Path) -> list[Path]:
    """A: index against yaw rate per preset. B: the same against Omega R / v."""
    viz.apply_style()
    table = load_table(tables_dir, "critical_rotation")
    thrust = float(table["condition.thrust_mps"].iloc[0])
    table["omega_R_over_v"] = (np.deg2rad(table["condition.yaw_rate_degps"])
                               * table["cloud_radius_m"] / thrust)
    fig, (ax_a, ax_b) = plt.subplots(1, 2, figsize=(viz.DOUBLE_COLUMN_IN,
                                                    0.42 * viz.DOUBLE_COLUMN_IN))
    summary_a = viz.plot_trend(ax_a, table, "condition.yaw_rate_degps",
                               "metrics.trans_rot_index", "condition.vision", viz.COLOURS,
                               viz.LABELS)
    low, high = observed_rotation_rates_degps()
    ax_a.axvspan(low, high, color=viz.COLOURS["neutral"], alpha=0.15, lw=0,
                 label="rotational PMs")
    ax_a.set_xlabel(f"yaw rate [°/s] at {thrust:g} m/s thrust")
    ax_a.legend(frameon=False)
    summary_b = viz.plot_trend(ax_b, table, "omega_R_over_v", "metrics.trans_rot_index",
                               "condition.vision", viz.COLOURS, viz.LABELS)
    for vision, group in table.groupby("condition.vision"):
        a_min, a_max = _pair(group["config.cloud.diameter_range_m"].iloc[0])
        ax_b.axvline(critical_ratio(a_min, a_max), color=viz.COLOURS.get(vision, "grey"),
                     linestyle=":", lw=1)
    fitted = fit_critical_ratio(summary_b)
    grid = np.linspace(0.0, summary_b["omega_R_over_v"].max(), 200)
    curve_label = (r"$(\mathcal{N}_c-\mathcal{N})/(\mathcal{N}_c+\mathcal{N})$, "
                   rf"$\mathcal{{N}}_c$ = {fitted:.2f}")
    (curve,) = ax_b.plot(grid, index_curve(grid, fitted), color="black", lw=1,
                         label=curve_label)
    ax_b.legend(handles=[curve], frameon=False, loc="lower left")
    ax_b.set_xlabel(r"$\Omega\,R\,/\,v$")
    for ax, label in ((ax_a, "A"), (ax_b, "B")):
        ax.axhline(0.0, color="black", lw=0.6)
        ax.set_ylabel(viz.LABELS["trans_rot_index"])
        viz.panel_label(ax, label)
    fig.tight_layout()
    theory = pd.DataFrame({"omega_R_over_v": grid, "median": index_curve(grid, fitted),
                           "panel": "B_theory", "fitted_critical_ratio": fitted})
    data = pd.concat([summary_a.assign(panel="A"), summary_b.assign(panel="B"), theory],
                     ignore_index=True)
    return viz.save_figure(fig, "fig5_critical_rotation", out_dir, data)


def _pair(value) -> tuple[float, float]:
    """A two-element range as stored in the collected table (list, array or its string)."""
    if isinstance(value, str):
        value = yaml.safe_load(value)
    low, high = (float(v) for v in np.ravel(np.asarray(value, dtype=float))[:2])
    return low, high


def index_curve(ratio: np.ndarray, critical: float) -> np.ndarray:
    """Translation-rotation index predicted for rotation number ``ratio``."""
    return (critical - ratio) / (critical + ratio)


def fit_critical_ratio(summary: pd.DataFrame) -> float:
    """Least-squares critical rotation number of the index curve through the medians."""
    x = summary["omega_R_over_v"].to_numpy(float)
    y = summary["median"].to_numpy(float)
    cost = lambda nc: float(np.mean((index_curve(x, nc) - y) ** 2))  # noqa: E731
    return float(minimize_scalar(cost, bounds=(0.5, 10.0), method="bounded").x)


def critical_ratio(a_min: float, a_max: float) -> float:
    """Predicted Omega_crit R / v for grains uniform in [a_min, a_max].

    With each grain visible out to d = a / tan(acuity), uniform positions in the ball
    of radius R = d_max, and flow summed over the visible grains, the translational and
    rotational sums are equal when Omega = (3/2) v E[d^2] / E[d^3].
    """
    q = a_min / a_max
    e_d2 = (1 - q**3) / (3 * (1 - q))
    e_d3 = (1 - q**4) / (4 * (1 - q))
    return 1.5 * e_d2 / e_d3


def figure_s2_depth(results_dir: Path, tables_dir: Path, out_dir: Path) -> list[Path]:
    viz.apply_style()
    table = load_table(tables_dir, "depth")
    main = table[table["condition.vision"] == MAIN_VISION]
    fig, axes = plt.subplots(1, 2, figsize=(viz.DOUBLE_COLUMN_IN, 0.4 * viz.DOUBLE_COLUMN_IN))
    parts = []
    for ax, (column, key) in zip(axes, [("metrics.n_in_fov", "n_in_fov"),
                                        ("foe_error_deg", "foe_error_deg")]):
        summary = viz.plot_trend(ax, main, "condition.depth_m", column, "pm_group",
                                 viz.COLOURS, viz.LABELS)
        ax.set_xlabel("seal depth [m]")
        ax.set_ylabel(viz.LABELS[key])
        parts.append(summary.assign(readout=key))
    axes[0].legend(frameon=False)
    fig.tight_layout()
    return viz.save_figure(fig, "figS2_depth", out_dir, pd.concat(parts, ignore_index=True))


def observed_rotation_rates_degps() -> tuple[float, float]:
    """Range of angular speed over the rotational prototypical movements."""
    pm = load_pm5d(default_data_dir())
    rotational = pm[pm["group"].str.startswith("rotation")]
    rates = np.rad2deg(np.linalg.norm(rotational[["yaw_radps", "pitch_radps", "roll_radps"]]
                                      .to_numpy(), axis=1))
    return float(rates.min()), float(rates.max())


FIGURES = {
    "2": figure_2, "3": figure_3, "4": figure_4, "5": figure_5_critical_rotation,
    "S1": figure_s1_globes, "S2": figure_s2_depth,
}


def all_figures() -> dict:
    """Sweep-based figures plus the robustness figures, which import this module."""
    from sealsim.figures_robustness import FIGURES as ROBUSTNESS
    return {**FIGURES, **ROBUSTNESS}


def make_figures(which: list[str], results_dir: Path, tables_dir: Path,
                 out_dir: Path) -> list[Path]:
    paths: list[Path] = []
    figures = all_figures()
    for key in which:
        paths += figures[key](results_dir, tables_dir, out_dir)
    return paths


