# sealsim

**SEnsory Aquatic odometry simuLator.** A harbour seal (*Phoca vitulina*) agent swims
through a cloud of suspended particles; the package computes the optic flow those
particles produce on the retina and asks whether turbid water can serve as an odometer.

[![tests](https://github.com/zerotonin/SEAL/actions/workflows/tests.yml/badge.svg)](https://github.com/zerotonin/SEAL/actions/workflows/tests.yml)
[![docs](https://github.com/zerotonin/SEAL/actions/workflows/docs.yml/badge.svg)](https://github.com/zerotonin/SEAL/actions/workflows/docs.yml)

> **Status (November 2026): under reconstruction.** The 2019 to 2022 research code is
> frozen in `_legacy/` and pinned by a regression test. The new `sealsim` package is
> being built sprint by sprint; see the lab-internal dev plan for the sequence.

## Install

```bash
conda env create -f environment.yml        # or environment-gpu.yml on a CUDA machine
conda activate sealsim
pip install -e ".[dev]"
cp local_paths.template.json local_paths.json   # then fill in data_root (step one, not optional)
sealsim config                                  # shows what was resolved
```

Every entry point refuses to run without `local_paths.json` or the matching
`SEALSIM_*` environment variables. Keys: `data_root`, `code_root`, `conda_setup`,
`conda_env`, and for the `hpc` profile `slurm_account`, `slurm_partition`.
Optional: `input_data` points at a copy of the `data/` tables outside the checkout.

## Quickstart

```bash
# one 6-DoF step (thrust, slip, lift in m/s; yaw, pitch, roll rates in rad/s)
sealsim step --velocity 1.8 0 0 2.2 0 0 --n-particles 5000
# the same for prototypical movement 10 (yaw right) in a 0.6 m/s head current
sealsim step --pm 10 --current -0.6 0 0 --out results/demo --stem pm10_current
# a 240 s U-dive at 100 Hz with flow readouts per step
sealsim dive --shape u --duration 240 --flow --n-particles 2000 --out results/demo
# a whole experiment grid (or one chunk of it, for a SLURM array), then one table
sealsim sweep experiments/currents.yaml --out results/currents
sealsim sweep experiments/currents.yaml --chunk 3 --n-chunks 20 --quiet
sealsim collect results/currents --out results/currents_table
```

Experiments are YAML files in `experiments/`: named vision presets, a grid of
conditions and fixed settings. Job *i* is the same grid point on every machine and
its seed is `base_seed + i`, so any run can be regenerated from the YAML alone.
Without `--out`, results go to `<data_root>/<experiment name>` from `local_paths.json`.

```python
import numpy as np
from sealsim import CloudSpec, Environment, StepConfig, UniformCurrent, run_step

cfg = StepConfig(
    velocity=(1.8, 0.0, 0.0, 2.2, 0.0, 0.0),
    cloud=CloudSpec(acuity_deg=0.27, diameter_range_m=(0.5e-3, 2e-3), n_particles=5000),
    environment=Environment(current=UniformCurrent((-0.153, 0.0, 0.0))),
    seed=0,
)
result = run_step(cfg)
print(result.metrics)            # FOE heading error, Spearman rho, trans/rot index
print(np.rad2deg(result.field.flow[result.field.in_fov]))
```

Every step writes a parquet table (one row per particle) and a yaml file with the
full configuration, seed, package version and readouts, so a figure can always be
traced back to the run that produced it.

## Figures and statistics

```bash
pip install -e ".[stats]"            # reRandomStats, for the pairwise tests
sealsim figures                      # all: 2 3 4 S1 S2 S3 -> <data_root>/figures
sealsim figures --which 3 S2
```

Every figure is written as SVG with editable text, as PNG and with a CSV of the
numbers plotted. Where groups are compared, a `*_stats_*.csv` holds the pairwise
Fisher resampling tests (median difference, 10 000 draws, Benjamini-Hochberg).
Flow panels are retinal cutouts in degrees with equal axes; dense fields are
thinned to 800 arrows and the title says so. The full-sphere Hammer globes are
supplementary. Colours follow Wong (2011).

## GPU and HPC runs

The array code runs on numpy or on [CuPy](https://cupy.dev); pick with `--backend
numpy|cupy|auto` or `SEALSIM_BACKEND`. A seed means the same particles on both
backends because the cloud is sampled on the CPU and moved to the device.

```bash
pip install -e ".[gpu]"                      # cupy-cuda12x, needs an NVIDIA driver
sealsim step --pm 10 --n-particles 200000 --backend cupy
python scripts/benchmark_backend.py          # prints the table below for this machine
```

One three-run step (full, translation only, rotation only) on a 20-core workstation:

| particles | numpy [ms] | cupy [ms] |
|---|---|---|
| 1,000 | 2.9 | to be measured on a GPU node |
| 10,000 | 17.9 | |
| 100,000 | 240 | |
| 1,000,000 | 1860 | |

The paper's single-step sweeps (`experiments/*.yaml`, 4200 jobs, at most 32 000
particles each) finish in about two minutes on one CPU core. The GPU path is for
clouds above 10^5 particles, for example 5.5 arcmin acuity with millimetre grains
(1.25 m radius), and for long dives.

On a SLURM cluster the `hpc` profile of `local_paths.json` supplies account,
partition, conda and data root; nothing cluster-specific is in the repository.

```bash
source slurm/load_paths.sh                   # hpc profile -> SEALSIM_* and SBATCH_*
slurm/submit_sweep.sh experiments/currents.yaml 20     # job array of 20 chunks, 1 GPU each
squeue --me
slurm/collect.sh currents                    # short batch job -> <data_root>/tables/currents
```

Array tasks log timestamped lines instead of progress bars. The login node only
submits; every computation runs on a compute node.

## Conventions

* Body frame: x forward (thrust), y left (slip), z up (lift). World frame z up, depth
  negative. Yaw is positive to the right, pitch positive nose-up, roll positive
  right-side-down, matching the signs in the data tables and the thesis.
* Retina: azimuth positive to the left, elevation positive up. Flow is the
  great-circle displacement of a particle's direction between two samples.
* A particle of diameter *a* is visible out to *d = a / tan(acuity)*; the cloud radius
  is the reach of the largest grain. Particles are uniform in volume and re-enter by
  point reflection when they leave, which keeps the density exact.
* A step lasts at most as long as it takes to travel half the cloud radius or to
  rotate by pi, unless `dt` is given.

## Layout

```
src/sealsim/      constants, geometry, cloud, environment, agent, opticflow,
                  dive, simulate, sweep, results, backend, viz, stats,
                  figures, config, cli
experiments/      one YAML per sweep (densities, currents, depth, critical rotation)
slurm/            load_paths.sh, submit_sweep.sh, run_chunk.sbatch, collect.sh
scripts/          benchmark_backend.py
data/             prototypical movements, dive profiles, PROVENANCE.md
tests/            pytest suite incl. analytic flow tests and the legacy regression fixture
docs/             Sphinx (Napoleon, Furo)
_legacy/          original flat scripts, untouched, plus their 2021-2022 outputs
```

## Provenance

The original simulator was written by Anne S. Oepen for her MSc thesis
(Göttingen, January 2021, supervised by Bart R. H. Geurten and Frederike D. Hanke),
with extensions by Bart R. H. Geurten in 2021 and 2022. The 2026 rewrite is by
Bart R. H. Geurten. Input data and their sources are listed in `data/PROVENANCE.md`.

## Citation

A `CITATION.cff` and Zenodo DOI will accompany the first tagged release of the
rebuilt package. Until then cite the thesis:

Oepen, A. S. (2021). *Turbidity: burden or benefit? Optic flow based odometry in a
semiaquatic species, the harbor seal (Phoca vitulina).* MSc thesis, Georg-August-Universität
Göttingen.

## Licence

MIT, see `LICENSE`.
