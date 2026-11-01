# ╔══════════════════════════════════════════════════════════════════╗
# ║  sealsim — stats                                                 ║
# ║  « reRandomStats wrappers: run every comparison, decide later »  ║
# ╠══════════════════════════════════════════════════════════════════╣
# ║  Pairwise Fisher resampling tests with Benjamini-Hochberg        ║
# ║  correction across condition levels. Replicates are simulation   ║
# ║  seeds, so these tests describe sampling noise of the particle   ║
# ║  cloud; effect sizes carry the argument, the p-values document   ║
# ║  it. The dependency is optional (pip install -e '.[stats]').     ║
# ╚══════════════════════════════════════════════════════════════════╝

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

DEFAULT_TEST = "Fisher:medianDiff"
DEFAULT_DRAWS = 10_000
INSTALL_HINT = "pip install git+https://github.com/zerotonin/reRandomStats.git"


def _multi_group_test():
    try:
        from rerandomstats import MultiGroupTest
    except ImportError as exc:  # pragma: no cover - exercised only without the extra
        raise ImportError(f"sealsim.stats needs reRandomStats: {INSTALL_HINT}") from exc
    return MultiGroupTest


def pairwise_groups(
    values: np.ndarray,
    groups: np.ndarray,
    test: str = DEFAULT_TEST,
    draws: int = DEFAULT_DRAWS,
    seed: int = 0,
) -> pd.DataFrame:
    """All pairwise comparisons between group labels, BH-FDR corrected."""
    values = np.asarray(values, dtype=float)
    groups = np.asarray(groups).astype(str)
    keep = np.isfinite(values)
    if len(np.unique(groups[keep])) < 2:
        return pd.DataFrame()
    tester = _multi_group_test()(list(values[keep]), list(groups[keep]), test,
                                 combination_n=draws, correction_type="fdr_bh", seed=seed)
    frame = tester.main()
    frame.insert(0, "test", test)
    frame.insert(1, "draws", draws)
    return frame


def compare_levels(
    table: pd.DataFrame,
    value: str,
    level: str,
    within: str | None = None,
    test: str = DEFAULT_TEST,
    draws: int = DEFAULT_DRAWS,
    seed: int = 0,
) -> pd.DataFrame:
    """Pairwise tests between the levels of one column, optionally inside each `within` group."""
    if within is None:
        return pairwise_groups(table[value].to_numpy(), table[level].to_numpy(), test, draws,
                               seed)
    parts = []
    for key, group in table.groupby(within, sort=False):
        result = pairwise_groups(group[value].to_numpy(), group[level].to_numpy(), test,
                                 draws, seed)
        if not result.empty:
            result.insert(0, within, key)
            parts.append(result)
    return pd.concat(parts, ignore_index=True) if parts else pd.DataFrame()


def describe_levels(table: pd.DataFrame, value: str, by: list[str]) -> pd.DataFrame:
    """n, median and interquartile range per level; the numbers behind every raincloud."""
    grouped = table.groupby(by)[value]
    out = grouped.agg(n="count", median="median",
                      q25=lambda s: s.quantile(0.25), q75=lambda s: s.quantile(0.75))
    return out.reset_index()


def save_stats(frame: pd.DataFrame, stem: str, output_dir: Path) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    path = output_dir / f"{stem}.csv"
    frame.to_csv(path, index=False)
    return path
