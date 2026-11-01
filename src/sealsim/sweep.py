# ╔══════════════════════════════════════════════════════════════════╗
# ║  sealsim — sweep                                                 ║
# ║  « experiments are data: a YAML grid becomes a job list »        ║
# ╠══════════════════════════════════════════════════════════════════╣
# ║  An experiment file names vision presets, a grid of conditions   ║
# ║  and fixed settings. The Cartesian product is enumerated in a    ║
# ║  fixed order, so job i means the same condition on every         ║
# ║  machine and the seed is base_seed + i. SLURM arrays take a      ║
# ║  chunk of the list; a laptop takes all of it.                    ║
# ╚══════════════════════════════════════════════════════════════════╝

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Iterator

import numpy as np
import yaml

from sealsim.cloud import CloudSpec
from sealsim.constants import DEFAULT_SEAL_DEPTH_M
from sealsim.dive import load_pm5d, pm5d_velocity
from sealsim.environment import Environment, UniformCurrent
from sealsim.simulate import StepConfig

CURRENT_DIRECTIONS: dict[str, tuple[float, float, float]] = {
    "head": (-1.0, 0.0, 0.0),
    "follow": (1.0, 0.0, 0.0),
    "cross": (0.0, 1.0, 0.0),
    "up": (0.0, 0.0, 1.0),
    "down": (0.0, 0.0, -1.0),
}


# ┌────────────────────────────────────────────────────────────┐
# │ Experiment  « the parsed YAML »                            │
# └────────────────────────────────────────────────────────────┘
@dataclass(frozen=True)
class Experiment:
    name: str
    description: str
    vision: dict[str, dict[str, Any]]
    grid: dict[str, list[Any]]
    fixed: dict[str, Any] = field(default_factory=dict)
    source: Path | None = None

    @property
    def n_jobs(self) -> int:
        return int(np.prod([len(v) for v in self.grid.values()])) if self.grid else 1

    def condition(self, index: int) -> dict[str, Any]:
        """Grid point number `index` in row-major order of the grid keys."""
        if not 0 <= index < self.n_jobs:
            raise IndexError(f"job {index} outside 0..{self.n_jobs - 1}")
        keys = list(self.grid)
        sizes = [len(self.grid[k]) for k in keys]
        picks = np.unravel_index(index, sizes) if keys else ()
        cond = {k: self.grid[k][int(i)] for k, i in zip(keys, picks)}
        return {"job_index": index, **self.fixed, **cond}

    def conditions(self) -> Iterator[dict[str, Any]]:
        return (self.condition(i) for i in range(self.n_jobs))


def load_experiment(path: Path) -> Experiment:
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    missing = {"name", "grid"} - set(data)
    if missing:
        raise ValueError(f"{path.name} lacks {sorted(missing)}")
    grid = {k: (v if isinstance(v, list) else [v]) for k, v in data["grid"].items()}
    return Experiment(
        name=str(data["name"]), description=str(data.get("description", "")).strip(),
        vision=data.get("vision", {}), grid=grid, fixed=data.get("fixed", {}), source=path,
    )


def expand_all(experiment: Experiment) -> list[dict[str, Any]]:
    return list(experiment.conditions())


def chunk_indices(n_jobs: int, chunk: int, n_chunks: int) -> range:
    """Jobs for array task `chunk` of `n_chunks`; every job lands in exactly one chunk."""
    if not 0 <= chunk < n_chunks:
        raise IndexError(f"chunk {chunk} outside 0..{n_chunks - 1}")
    per = -(-n_jobs // n_chunks)
    return range(min(chunk * per, n_jobs), min((chunk + 1) * per, n_jobs))


# ┌────────────────────────────────────────────────────────────┐
# │ Conditions  « one grid point becomes one StepConfig »      │
# └────────────────────────────────────────────────────────────┘
def build_step_config(
    cond: dict[str, Any], experiment: Experiment, pm_table=None
) -> StepConfig:
    velocity = _velocity(cond, pm_table)
    cloud = _cloud(cond, experiment)
    env = Environment(
        floor_z=float(cond.get("floor_z", Environment().floor_z)),
        current=UniformCurrent(_current(cond)),
    )
    base_seed = int(cond.get("base_seed", 0))
    return StepConfig(
        velocity=tuple(float(v) for v in velocity),
        position=(0.0, 0.0, float(cond.get("depth_m", DEFAULT_SEAL_DEPTH_M))),
        euler=tuple(float(v) for v in cond.get("euler", (0.0, 0.0, 0.0))),
        dt=cond.get("dt"),
        cloud=cloud, environment=env,
        seed=base_seed + int(cond["job_index"]),
        decompose=bool(cond.get("decompose", True)),
    )


def _velocity(cond: dict[str, Any], pm_table) -> np.ndarray:
    if "velocity" in cond:
        return np.asarray(cond["velocity"], dtype=float)
    if "pm_id" in cond:
        table = load_pm5d() if pm_table is None else pm_table
        return pm5d_velocity(table, int(cond["pm_id"]))
    thrust = float(cond.get("thrust_mps", 0.0))
    yaw = np.deg2rad(float(cond.get("yaw_rate_degps", 0.0)))
    pitch = np.deg2rad(float(cond.get("pitch_rate_degps", 0.0)))
    return np.array([thrust, 0.0, 0.0, yaw, pitch, 0.0])


def _cloud(cond: dict[str, Any], experiment: Experiment) -> CloudSpec:
    preset = dict(experiment.vision.get(cond.get("vision", ""), {}))
    spec = CloudSpec(
        acuity_deg=float(cond.get("acuity_deg", preset.get("acuity_deg", CloudSpec().acuity_deg))),
        diameter_range_m=tuple(cond.get("diameter_range_m",
                                        preset.get("diameter_range_m",
                                                   CloudSpec().diameter_range_m))),
        n_particles=cond.get("n_particles"),
        number_density_per_m3=cond.get("number_density_per_m3"),
    )
    if spec.n_particles is None and spec.number_density_per_m3 is None:
        raise ValueError("condition needs n_particles or number_density_per_m3")
    return spec


def _current(cond: dict[str, Any]) -> tuple[float, float, float]:
    if "current" in cond:
        return tuple(float(v) for v in cond["current"])
    speed = float(cond.get("current_speed_mps", 0.0))
    direction = CURRENT_DIRECTIONS[str(cond.get("current_direction", "head"))]
    return tuple(speed * d for d in direction)


def job_stem(experiment: Experiment, index: int) -> str:
    return f"{experiment.name}_job{index:05d}"
