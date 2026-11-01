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

## Layout

```
src/sealsim/      the package (config, cli; physics modules follow in Sprint 1)
data/             prototypical movements, dive profiles, PROVENANCE.md
tests/            pytest suite incl. the legacy regression fixture
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
