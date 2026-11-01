# ╔══════════════════════════════════════════════════════════════════╗
# ║  sealsim — tests.test_backend                                    ║
# ║  « same numbers on numpy and on cupy »                           ║
# ╠══════════════════════════════════════════════════════════════════╣
# ║  numpy is always exercised; the cupy tests skip cleanly on       ║
# ║  machines and CI runners without a CUDA device.                  ║
# ╚══════════════════════════════════════════════════════════════════╝

from __future__ import annotations

import numpy as np
import pytest
from scipy.stats import spearmanr

from sealsim import backend
from sealsim.cloud import CloudSpec
from sealsim.opticflow import rank_correlation
from sealsim.simulate import StepConfig, run_step

needs_cupy = pytest.mark.skipif(not backend.cupy_available(), reason="no cupy or no CUDA device")


def test_numpy_is_the_default_and_round_trips():
    assert backend.get_array_module("numpy") is np
    a = np.arange(3.0)
    assert backend.array_module_of(a) is np
    assert backend.backend_name(np) == "numpy"
    np.testing.assert_array_equal(backend.to_numpy(a), a)
    np.testing.assert_array_equal(backend.to_backend(a, np), a)


def test_unknown_backend_raises():
    with pytest.raises(backend.BackendError):
        backend.get_array_module("tpu")


@pytest.mark.skipif(backend.cupy_available(), reason="cupy present")
def test_cupy_request_fails_loudly_without_device():
    with pytest.raises(backend.BackendError):
        backend.get_array_module("cupy")
    assert backend.get_array_module("auto") is np


def test_rank_correlation_matches_scipy_without_ties():
    rng = np.random.default_rng(0)
    x = rng.normal(size=500)
    y = x + rng.normal(size=500)
    assert rank_correlation(x, y) == pytest.approx(spearmanr(x, y).statistic, abs=1e-12)


@needs_cupy
def test_cupy_step_matches_numpy_step():
    cfg = StepConfig(velocity=(1.8, 0.1, -0.05, 2.2, 0.3, 0.0), seed=3,
                     cloud=CloudSpec(n_particles=4000))
    cpu = run_step(cfg)
    gpu = run_step(StepConfig(**{**cfg.__dict__, "backend": "cupy"}))
    assert backend.backend_name(backend.array_module_of(gpu.field.magnitude)) == "cupy"
    np.testing.assert_allclose(backend.to_numpy(gpu.field.magnitude), cpu.field.magnitude,
                               rtol=1e-10, atol=1e-12)
    np.testing.assert_array_equal(backend.to_numpy(gpu.field.in_fov), cpu.field.in_fov)
    for key, value in cpu.metrics.as_dict().items():
        assert gpu.metrics.as_dict()[key] == pytest.approx(value, rel=1e-8, abs=1e-10), key


@needs_cupy
def test_cli_step_on_cupy(tmp_path):
    from sealsim.cli import main

    rc = main(["step", "--pm", "2", "--n-particles", "1000", "--backend", "cupy",
               "--out", str(tmp_path)])
    assert rc == 0 and (tmp_path / "step.parquet").exists()
