# ╔══════════════════════════════════════════════════════════════════╗
# ║  sealsim — tests.test_sweep                                      ║
# ║  « a grid is enumerated once, in order, with fixed seeds »       ║
# ╠══════════════════════════════════════════════════════════════════╣
# ║  Chunks cover every job exactly once, conditions build valid     ║
# ║  configurations, and the shipped experiment files parse.         ║
# ╚══════════════════════════════════════════════════════════════════╝

from __future__ import annotations

from pathlib import Path

import numpy as np
import pytest
import yaml

from sealsim import sweep
from sealsim.cli import main
from sealsim.results import collect_metadata

EXPERIMENTS = Path(__file__).resolve().parents[1] / "experiments"


def _write(tmp_path: Path, **grid) -> Path:
    data = {
        "name": "t", "description": "test",
        "vision": {"v": {"acuity_deg": 0.27, "diameter_range_m": [0.0005, 0.002]}},
        "grid": grid, "fixed": {"vision": "v", "n_particles": 100, "base_seed": 7},
    }
    path = tmp_path / "t.yaml"
    path.write_text(yaml.safe_dump(data), encoding="utf-8")
    return path


def test_grid_is_row_major_and_seeds_follow_index(tmp_path):
    exp = sweep.load_experiment(_write(tmp_path, pm_id=[2, 10], replicate=[0, 1, 2]))
    assert exp.n_jobs == 6
    conds = sweep.expand_all(exp)
    assert [c["pm_id"] for c in conds] == [2, 2, 2, 10, 10, 10]
    assert [c["replicate"] for c in conds] == [0, 1, 2, 0, 1, 2]
    cfg = sweep.build_step_config(conds[4], exp)
    assert cfg.seed == 7 + 4 and cfg.velocity[3] == pytest.approx(2.1617)


def test_chunks_partition_the_jobs():
    covered = [i for c in range(4) for i in sweep.chunk_indices(10, c, 4)]
    assert covered == list(range(10))
    with pytest.raises(IndexError):
        sweep.chunk_indices(10, 4, 4)


def test_current_direction_and_rate_conditions(tmp_path):
    exp = sweep.load_experiment(_write(tmp_path, current_speed_mps=[0.6],
                                       current_direction=["cross"], yaw_rate_degps=[90]))
    cfg = sweep.build_step_config(exp.condition(0), exp)
    assert cfg.environment.current.velocity == (0.0, 0.6, 0.0)
    assert cfg.velocity[3] == pytest.approx(np.pi / 2) and cfg.velocity[0] == 0.0


@pytest.mark.parametrize("name", sorted(p.name for p in EXPERIMENTS.glob("*.yaml")))
def test_shipped_experiments_build(name):
    exp = sweep.load_experiment(EXPERIMENTS / name)
    assert exp.n_jobs > 0
    first = sweep.build_step_config(exp.condition(0), exp)
    last = sweep.build_step_config(exp.condition(exp.n_jobs - 1), exp)
    assert first.cloud.count() > 0 and last.seed > first.seed


def test_cli_sweep_and_collect_round_trip(tmp_path):
    out = tmp_path / "out"
    rc = main(["sweep", str(EXPERIMENTS / "smoke.yaml"), "--out", str(out),
               "--chunk", "1", "--n-chunks", "2"])
    assert rc == 0
    assert len(list(out.glob("*.yaml"))) == 2
    rc = main(["sweep", str(EXPERIMENTS / "smoke.yaml"), "--out", str(out),
               "--chunk", "0", "--n-chunks", "2"])
    assert rc == 0 and len(list(out.glob("*.parquet"))) == 4
    rc = main(["collect", str(out), "--out", str(tmp_path / "table")])
    assert rc == 0
    table = collect_metadata(out)
    assert len(table) == 4 and "condition.pm_id" in table.columns
    assert (tmp_path / "table.parquet").exists() and (tmp_path / "table.csv").exists()
