# Changelog

All notable changes to sealsim. The format follows Keep a Changelog; versions follow
semantic versioning and are tagged `vX.Y.Z`.

## [Unreleased]

### Added
- `corollaries`: the law for any grain-size distribution (Sauter mean diameter),
  under a contrast horizon, in its time form and as a speed estimator; samplers for
  uniform, log-normal and Junge size spectra.
- `robustness`: translation-rotation index per azimuth band (step and instantaneous),
  bow-flow bias from a dipole potential flow around the head, Cramer-Rao bound on
  heading for an ideal decomposer with additive or Weber noise, FOE template observer.
- `figures_robustness`: manuscript Figures 7 (suspended matter, horizon, speed) and
  8 (bands, bow flow, observers); `sealsim figures --which 7 8`.
- Constants: literature grain classes, contrast and body-size quantities with sources.
- Tests for both new modules (11).

## [1.0.0] - 2026-11-02

First release of the rebuilt package.

### Added
- `sealsim` package (src layout): constants with sourced `Quantity` values, geometry,
  particle cloud, environment with currents, six-DoF agent, great-circle optic flow,
  three odometry readouts, Markov-chain dive generator, step and dive simulation,
  YAML sweeps with SLURM chunking, parquet results and collection.
- numpy and CuPy backends behind one array module; `--backend` on every command.
- `slurm/` helpers reading account, partition and paths from `local_paths.json`.
- `viz`, `stats` and `figures`: Wong palette, SVG + PNG + CSV export, rainclouds,
  reRandomStats pairwise tests, manuscript figures 2 to 4 and S1 to S3.
- Input tables shipped inside the package (`sealsim/data/`) with `PROVENANCE.md`.
- Tests (88), GitHub Actions for tests, docs and releases, Sphinx site with a model
  reference and the provenance page.

### Changed
- Visibility radius corrected: the legacy code used 1.74 mm (a degrees-for-radians
  slip); the model now derives `R = a_max / tan(acuity)` per vision preset.
- Flow is the great-circle displacement in the body frame of each sample instead of
  elementwise azimuth and elevation differences; rotation matrices applied with the
  correct transpose; frames no longer mixed.
- Particles resample uniformly in the ball and re-enter by point reflection; the
  hollow core and the radial sampling bias are gone.
- Dive phase indices, step duration rule and 50-PM Markov chain rewritten from the
  tables; Brownian motion dropped as negligible at these scales.

### Removed
- Flat research scripts, now frozen under `_legacy/` and pinned by a regression test.

## [0.2-legacy] - 2026-11-02
Frozen state of the 2021 to 2022 research scripts before the rewrite.

## [0.1-thesis] - 2026-11-02
State of the code at the time of the 2021 MSc thesis.
