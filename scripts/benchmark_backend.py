# ╔══════════════════════════════════════════════════════════════════╗
# ║  sealsim — scripts.benchmark_backend                             ║
# ║  « how long one step takes, per backend and cloud size »         ║
# ╠══════════════════════════════════════════════════════════════════╣
# ║  Run on a workstation and on a GPU node; paste the table into    ║
# ║  the README. Times the full three-run step (full, translation    ║
# ║  only, rotation only) that every sweep job performs.             ║
# ╚══════════════════════════════════════════════════════════════════╝

from __future__ import annotations

import argparse
import time
from pathlib import Path

import numpy as np

from sealsim.backend import cupy_available
from sealsim.cloud import CloudSpec
from sealsim.simulate import StepConfig, run_step

SIZES = (1_000, 10_000, 100_000, 1_000_000)
VELOCITY = (1.8, 0.0, 0.0, 2.2, 0.0, 0.0)


def time_step(n_particles: int, backend: str, repeats: int) -> float:
    cfg = StepConfig(velocity=VELOCITY, cloud=CloudSpec(n_particles=n_particles),
                     backend=backend, seed=0)
    run_step(cfg)
    times = []
    for _ in range(repeats):
        start = time.perf_counter()
        run_step(cfg)
        if backend == "cupy":
            import cupy

            cupy.cuda.Stream.null.synchronize()
        times.append(time.perf_counter() - start)
    return float(np.median(times))


def main() -> int:
    parser = argparse.ArgumentParser(description="time sealsim steps on numpy and cupy")
    parser.add_argument("--repeats", type=int, default=5)
    parser.add_argument("--out", type=Path, default=None, help="write a markdown table here")
    args = parser.parse_args()
    backends = ["numpy"] + (["cupy"] if cupy_available() else [])
    rows = ["| particles | " + " | ".join(f"{b} [ms]" for b in backends) + " |",
            "|---|" + "---|" * len(backends)]
    for n in SIZES:
        cells = [f"{time_step(n, b, args.repeats) * 1e3:.1f}" for b in backends]
        rows.append(f"| {n:,} | " + " | ".join(cells) + " |")
        print(rows[-1], flush=True)
    if not cupy_available():
        rows.append("")
        rows.append("cupy column missing: no CUDA device on this machine.")
    table = "\n".join(rows) + "\n"
    if args.out:
        args.out.write_text(table, encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
