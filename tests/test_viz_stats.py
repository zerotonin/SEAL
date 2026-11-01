# ╔══════════════════════════════════════════════════════════════════╗
# ║  sealsim — tests.test_viz_stats                                  ║
# ║  « triple output, raincloud, trend, stats wrappers »             ║
# ╠══════════════════════════════════════════════════════════════════╣
# ║  Synthetic tables only; the manuscript figures need a results    ║
# ║  directory and are exercised by `sealsim figures` on real        ║
# ║  sweeps.                                                         ║
# ╚══════════════════════════════════════════════════════════════════╝

from __future__ import annotations

import matplotlib
import numpy as np
import pandas as pd
import pytest

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

from sealsim import figures, stats, viz  # noqa: E402

needs_stats = pytest.mark.skipif(
    pytest.importorskip("rerandomstats", reason="reRandomStats not installed") is None,
    reason="reRandomStats not installed",
)


def _frame(n: int = 50, seed: int = 0) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    az = rng.uniform(-np.pi, np.pi, n)
    el = rng.uniform(-0.5, 1.0, n)
    return pd.DataFrame({
        "azimuth_rad": az, "elevation_rad": el,
        "flow_azimuth_rad": 0.02 * np.sin(az), "flow_elevation_rad": 0.02 * np.cos(el),
        "magnitude_rad": 0.02 * np.hypot(np.sin(az), np.cos(el)),
        "distance_m": rng.uniform(0.1, 0.4, n), "valid": np.ones(n, dtype=bool),
    })


def test_save_figure_writes_svg_png_csv(tmp_path):
    viz.apply_style()
    fig, ax = plt.subplots()
    ax.plot([0, 1], [0, 1])
    paths = viz.save_figure(fig, "demo", tmp_path, pd.DataFrame({"x": [0, 1]}))
    assert [p.suffix for p in paths] == [".svg", ".png", ".csv"]
    assert all(p.exists() for p in paths)
    assert "<text" in paths[0].read_text(encoding="utf-8")


def test_mercator_thins_and_counts():
    fig, ax = plt.subplots()
    n_shown = viz.plot_flow_mercator(ax, _frame(2000), max_arrows=100)
    assert n_shown == 100
    assert ax.get_aspect() == 1.0
    plt.close(fig)


def test_raincloud_and_trend():
    fig, (ax1, ax2) = plt.subplots(1, 2)
    viz.plot_raincloud(ax1, [np.arange(10.0), np.arange(5.0) + 3], ["a", "b"], ["#000", "#111"])
    assert [t.get_text() for t in ax1.get_yticklabels()] == ["a", "b"]
    table = pd.DataFrame({"x": np.tile([1, 2, 3], 4), "y": np.arange(12.0),
                          "g": ["p"] * 6 + ["q"] * 6})
    summary = viz.plot_trend(ax2, table, "x", "y", "g", {"p": "#000", "q": "#111"})
    assert set(summary.columns) == {"g", "x", "q25", "median", "q75"}
    assert len(summary) == 6
    plt.close(fig)


def test_field_from_frame_recovers_foe():
    frame = _frame(300)
    field = figures._field_from_frame(frame)
    assert field.direction.shape == (300, 3)
    np.testing.assert_allclose(np.linalg.norm(field.tangent, axis=1), 1.0, atol=1e-9)


def test_pm_groups_cover_all_13():
    assert sorted(figures.PM_GROUPS) == list(range(1, 14))
    assert set(figures.PM_GROUPS.values()) == set(figures.GROUP_ORDER)


def test_describe_levels():
    table = pd.DataFrame({"v": [1.0, 2.0, 3.0, 10.0], "g": ["a", "a", "b", "b"]})
    out = stats.describe_levels(table, "v", ["g"])
    assert list(out["n"]) == [2, 2]
    assert list(out["median"]) == [1.5, 6.5]


@needs_stats
def test_compare_levels_runs_and_corrects(tmp_path):
    rng = np.random.default_rng(1)
    table = pd.DataFrame({"v": np.r_[rng.normal(0, 1, 20), rng.normal(3, 1, 20),
                                     rng.normal(0, 1, 20)],
                          "g": ["a"] * 20 + ["b"] * 20 + ["c"] * 20})
    out = stats.compare_levels(table, "v", "g", draws=500)
    assert len(out) == 3
    assert (out["test"] == stats.DEFAULT_TEST).all()
    path = stats.save_stats(out, "s", tmp_path)
    assert path.exists()
