# ╔══════════════════════════════════════════════════════════════════╗
# ║  sealsim — tests.test_results_cli                                ║
# ║  « files round-trip and the CLI runs end to end »                ║
# ╠══════════════════════════════════════════════════════════════════╣
# ║  What is written must be readable by the figure scripts.         ║
# ╚══════════════════════════════════════════════════════════════════╝

from __future__ import annotations

import numpy as np
import pandas as pd

from sealsim import cli, results
from sealsim.cloud import CloudSpec
from sealsim.dive import generate_dive
from sealsim.simulate import StepConfig, run_step


def test_save_step_round_trip(tmp_path):
    cfg = StepConfig(velocity=(1.0, 0, 0, 0, 0, 0), cloud=CloudSpec(n_particles=300))
    parquet, meta = results.save_step(run_step(cfg), tmp_path, "s")
    frame = pd.read_parquet(parquet)
    assert len(frame) == 300 and "translation_magnitude_rad" in frame.columns
    data = results.load_metadata(meta)
    assert data["kind"] == "step" and data["metrics"]["n_particles"] == 300
    assert data["config"]["cloud"]["n_particles"] == 300
    collected = results.collect_metadata(tmp_path)
    assert collected.loc[0, "metrics.n_particles"] == 300


def test_save_dive_round_trip(tmp_path):
    traj = generate_dive("v", 20.0, 20.0, np.random.default_rng(0))
    metrics = pd.DataFrame({"foe_error_rad": np.zeros(traj.velocity_body.shape[0])})
    parquet, meta = results.save_dive(traj, metrics, tmp_path, "d", {"seed": 0})
    frame = pd.read_parquet(parquet)
    assert "foe_error_rad" in frame.columns and len(frame) == 401
    assert results.load_metadata(meta)["shape"] == "v"


def test_cli_step_writes_outputs(tmp_path):
    rc = cli.main(["step", "--velocity", "1.5", "0", "0", "0", "0", "0",
                   "--n-particles", "200", "--out", str(tmp_path), "--stem", "t"])
    assert rc == 0
    assert (tmp_path / "t.parquet").exists() and (tmp_path / "t.yaml").exists()


def test_cli_step_from_pm_table():
    assert cli.main(["step", "--pm", "10", "--n-particles", "200"]) == 0


def test_cli_dive_with_flow(tmp_path):
    rc = cli.main(["dive", "--shape", "v", "--duration", "5", "--sample-rate", "10",
                   "--flow", "--n-particles", "200", "--out", str(tmp_path)])
    assert rc == 0
    frame = pd.read_parquet(tmp_path / "dive.parquet")
    assert "foe_error_rad" in frame.columns
