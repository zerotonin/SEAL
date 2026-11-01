# ╔══════════════════════════════════════════════════════════════════╗
# ║  sealsim — viz                                                   ║
# ║  « Wong palette, Mercator cutouts, Hammer globes, rainclouds »   ║
# ╠══════════════════════════════════════════════════════════════════╣
# ║  Every figure leaves as SVG (editable text), PNG and a CSV of    ║
# ║  the numbers behind it. Flow panels are retinal cutouts in       ║
# ║  degrees with equal axes; the full-sphere Hammer projection is   ║
# ║  for the supplement. Distributions are rainclouds, never bars.   ║
# ╚══════════════════════════════════════════════════════════════════╝

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Sequence

import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.axes import Axes
from matplotlib.figure import Figure

from sealsim.constants import (
    AZIMUTH_LIMIT_DEG,
    ELEVATION_MAX_DEG,
    ELEVATION_MIN_DEG,
    WONG,
)

# ┌────────────────────────────────────────────────────────────┐
# │ Figure constants  « sizes, dpi, semantic colours »         │
# └────────────────────────────────────────────────────────────┘
FIGURE_DPI = 300
SINGLE_COLUMN_IN = 85 / 25.4
DOUBLE_COLUMN_IN = 180 / 25.4
FONT_SIZE = 8
MAX_ARROWS = 800

COLOURS: dict[str, str] = {
    "fast_translation": WONG["vermilion"],
    "slow_translation": WONG["orange"],
    "rotation": WONG["blue"],
    "rotation_yaw_right": WONG["blue"],
    "rotation_yaw_left": WONG["sky_blue"],
    "rotation_pitch_down": WONG["reddish_purple"],
    "rotation_pitch_up": WONG["bluish_green"],
    "north_sea": WONG["bluish_green"],
    "thesis": WONG["reddish_purple"],
    "head": WONG["blue"],
    "cross": WONG["orange"],
    "follow": WONG["sky_blue"],
    "clear": WONG["sky_blue"],
    "turbid": WONG["vermilion"],
    "flow": "#1f2a44",
    "foe": WONG["orange"],
    "heading": WONG["black"],
    "fov": WONG["bluish_green"],
    "neutral": "#7f7f7f",
}
LABELS: dict[str, str] = {
    "fast_translation": "fast translation",
    "slow_translation": "slow translation",
    "rotation": "rotation",
    "north_sea": "0.27° acuity, 0.5–2 mm grains",
    "thesis": "5.5′ acuity, 20–160 µm grains",
    "head": "head current",
    "cross": "cross current",
    "follow": "following current",
    "foe_error_deg": "FOE heading error [°]",
    "spearman_rho": r"Spearman $\rho$",
    "trans_rot_index": "translation–rotation index",
    "n_in_fov": "particles in the visual field",
}


def apply_style() -> None:
    """Editable SVG text, small fonts, no top/right spines."""
    matplotlib.rcParams.update({
        "svg.fonttype": "none",
        "font.size": FONT_SIZE,
        "axes.titlesize": FONT_SIZE,
        "axes.labelsize": FONT_SIZE,
        "xtick.labelsize": FONT_SIZE - 1,
        "ytick.labelsize": FONT_SIZE - 1,
        "legend.fontsize": FONT_SIZE - 1,
        "axes.spines.top": False,
        "axes.spines.right": False,
        "figure.dpi": 100,
        "savefig.dpi": FIGURE_DPI,
    })


def save_figure(
    fig: Figure, stem: str, output_dir: Path, data: pd.DataFrame | None = None
) -> list[Path]:
    """Export SVG + PNG and, when given, the CSV companion table."""
    output_dir.mkdir(parents=True, exist_ok=True)
    paths = [output_dir / f"{stem}.svg", output_dir / f"{stem}.png"]
    fig.savefig(paths[0], bbox_inches="tight")
    fig.savefig(paths[1], bbox_inches="tight", dpi=FIGURE_DPI)
    if data is not None:
        csv = output_dir / f"{stem}.csv"
        data.to_csv(csv, index=False)
        paths.append(csv)
    plt.close(fig)
    return paths


# ┌────────────────────────────────────────────────────────────┐
# │ Flow panels  « retinal cutout and full sphere »            │
# └────────────────────────────────────────────────────────────┘
@dataclass(frozen=True)
class FlowPanelMarks:
    """Optional overlays: focus of expansion and heading, as (azimuth, elevation) in rad."""

    foe: tuple[float, float] | None = None
    heading: tuple[float, float] | None = None


def plot_flow_mercator(
    ax: Axes,
    frame: pd.DataFrame,
    marks: FlowPanelMarks | None = None,
    colour: str = COLOURS["flow"],
    cutout: tuple[tuple[float, float], tuple[float, float]] = ((-125.0, 125.0), (-35.0, 90.0)),
    arrow_width: float = 0.004,
    max_arrows: int = MAX_ARROWS,
) -> int:
    """Quiver of per-step retinal displacement in degrees; arrows are true size.

    Dense fields are thinned to ``max_arrows`` random vectors (fixed seed) so the
    pattern stays readable; returns the number drawn.
    """
    f = subsample_frame(frame, max_arrows)
    az, el = np.rad2deg(f["azimuth_rad"]), np.rad2deg(f["elevation_rad"])
    u, v = np.rad2deg(f["flow_azimuth_rad"]), np.rad2deg(f["flow_elevation_rad"])
    ax.quiver(az, el, u, v, angles="xy", scale_units="xy", scale=1.0, width=arrow_width,
              color=colour, alpha=0.8, zorder=2)
    _draw_fov(ax, degrees=True)
    _draw_marks(ax, marks, degrees=True)
    ax.set_aspect("equal")
    ax.set_xlim(*cutout[0])
    ax.set_ylim(*cutout[1])
    ax.set_xlabel("azimuth [°]")
    ax.set_ylabel("elevation [°]")
    return len(f)


def plot_flow_hammer(
    ax: Axes,
    frame: pd.DataFrame,
    marks: FlowPanelMarks | None = None,
    colour: str = COLOURS["flow"],
    max_arrows: int = MAX_ARROWS,
) -> int:
    """Whole retina on a Hammer projection (axes created with projection='hammer')."""
    f = subsample_frame(frame, max_arrows)
    ax.quiver(f["azimuth_rad"], f["elevation_rad"], f["flow_azimuth_rad"],
              f["flow_elevation_rad"], angles="xy", scale_units="xy", scale=1.0,
              width=0.003, color=colour, alpha=0.8, zorder=2)
    _draw_fov(ax, degrees=False)
    _draw_marks(ax, marks, degrees=False)
    ax.grid(True, alpha=0.3)
    ax.set_xticklabels([])
    return len(f)


def subsample_frame(frame: pd.DataFrame, max_arrows: int, seed: int = 0) -> pd.DataFrame:
    """Valid rows only, thinned to at most ``max_arrows`` with a fixed seed."""
    f = frame[frame["valid"]]
    if len(f) <= max_arrows:
        return f
    return f.sample(n=max_arrows, random_state=seed)


def _draw_fov(ax: Axes, degrees: bool) -> None:
    az = AZIMUTH_LIMIT_DEG.value
    lo, hi = ELEVATION_MIN_DEG.value, ELEVATION_MAX_DEG.value
    x = np.array([-az, -az, az, az, -az])
    y = np.array([lo, hi, hi, lo, lo])
    if not degrees:
        x, y = np.deg2rad(x), np.deg2rad(y)
    ax.plot(x, y, color=COLOURS["fov"], linewidth=1.2, zorder=1)


def _draw_marks(ax: Axes, marks: FlowPanelMarks | None, degrees: bool) -> None:
    if marks is None:
        return
    convert = np.rad2deg if degrees else (lambda v: v)
    if marks.heading is not None:
        ax.scatter(convert(marks.heading[0]), convert(marks.heading[1]), marker="x", s=60,
                   color=COLOURS["heading"], zorder=4, label="heading")
    if marks.foe is not None and np.all(np.isfinite(marks.foe)):
        ax.scatter(convert(marks.foe[0]), convert(marks.foe[1]), marker="+", s=90,
                   color=COLOURS["foe"], linewidths=1.5, zorder=5, label="FOE estimate")


# ┌────────────────────────────────────────────────────────────┐
# │ Distributions  « rainclouds and trends with spread »       │
# └────────────────────────────────────────────────────────────┘
def plot_raincloud(
    ax: Axes,
    samples: Sequence[np.ndarray],
    labels: Sequence[str],
    colours: Sequence[str],
    rng_seed: int = 0,
) -> None:
    """Half violin, jittered points and a box per group, groups along y."""
    rng = np.random.default_rng(rng_seed)
    for i, (values, colour) in enumerate(zip(samples, colours)):
        values = np.asarray(values, dtype=float)
        values = values[np.isfinite(values)]
        if values.size == 0:
            continue
        if values.size > 2 and np.ptp(values) > 0:
            parts = ax.violinplot(values, positions=[i], widths=0.8, showextrema=False,
                                  points=200, **_horizontal())
            for body in parts["bodies"]:
                body.set_facecolor(colour)
                body.set_edgecolor("none")
                body.set_alpha(0.5)
                path = body.get_paths()[0]
                vertices = path.vertices
                vertices[:, 1] = np.clip(vertices[:, 1], i, i + 0.4)
        jitter = i - 0.08 - rng.uniform(0.0, 0.22, size=values.size)
        ax.scatter(values, jitter, s=6, color=colour, alpha=0.7, linewidths=0, zorder=3)
        ax.boxplot(values, positions=[i - 0.02], widths=0.12, showfliers=False,
                   medianprops={"color": "black"}, boxprops={"color": "black"},
                   whiskerprops={"color": "black"}, capprops={"color": "black"}, zorder=4,
                   **_horizontal())
    ax.set_yticks(range(len(labels)))
    ax.set_yticklabels(labels)
    ax.set_ylim(-0.6, len(labels) - 0.3)


def _horizontal() -> dict[str, object]:
    """Keyword for horizontal box/violin plots across the matplotlib 3.10 rename."""
    major, minor = (int(v) for v in matplotlib.__version__.split(".")[:2])
    return {"orientation": "horizontal"} if (major, minor) >= (3, 10) else {"vert": False}


def plot_trend(
    ax: Axes,
    table: pd.DataFrame,
    x: str,
    y: str,
    hue: str,
    colours: dict[str, str],
    labels: dict[str, str] | None = None,
    logx: bool = False,
    linestyle: str = "-",
) -> pd.DataFrame:
    """Median line with interquartile band per hue level; returns the summary table."""
    rows = []
    for level, group in table.groupby(hue, sort=False):
        summary = group.groupby(x)[y].quantile([0.25, 0.5, 0.75]).unstack()
        summary.columns = ["q25", "median", "q75"]
        summary = summary.reset_index()
        colour = colours.get(str(level), COLOURS["neutral"])
        label = (labels or {}).get(str(level), str(level))
        ax.fill_between(summary[x], summary["q25"], summary["q75"], color=colour, alpha=0.2,
                        linewidth=0)
        ax.plot(summary[x], summary["median"], linestyle, marker="o", markersize=3,
                color=colour, label=label)
        summary.insert(0, hue, level)
        rows.append(summary)
    if logx:
        ax.set_xscale("log")
    return pd.concat(rows, ignore_index=True) if rows else pd.DataFrame()


def panel_label(ax: Axes, text: str, offset_points: tuple[float, float] = (-34.0, 4.0)) -> None:
    """Bold letter above the top-left corner, placed in points so axis width does not matter."""
    ax.annotate(text, xy=(0.0, 1.0), xycoords="axes fraction", xytext=offset_points,
                textcoords="offset points", fontsize=FONT_SIZE + 2, fontweight="bold",
                va="bottom", ha="left", annotation_clip=False)


def shown_title(ax: Axes, text: str, n_shown: int, n_total: int) -> None:
    """Right-aligned two-line title that states how many arrows were thinned away."""
    counter = f"{n_shown} of {n_total} vectors" if n_shown < n_total else f"{n_total} vectors"
    ax.set_title(f"{text}\n{counter}", loc="right", fontsize=FONT_SIZE - 1)
