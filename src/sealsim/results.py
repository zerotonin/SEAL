# ╔══════════════════════════════════════════════════════════════════╗
# ║  sealsim — results                                               ║
# ║  « parquet for the numbers, yaml for the provenance »            ║
# ╠══════════════════════════════════════════════════════════════════╣
# ║  Every run writes <stem>.parquet (one row per particle or per    ║
# ║  sample) and <stem>.yaml (version, seed, configuration,          ║
# ║  metrics). collect_metadata() flattens a directory of yaml       ║
# ║  files into one table, which is what the figure scripts read.    ║
# ╚══════════════════════════════════════════════════════════════════╝

from __future__ import annotations

import dataclasses
import datetime as dt
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
import yaml

from sealsim import __version__
from sealsim.dive import DiveTrajectory
from sealsim.opticflow import FlowField
from sealsim.simulate import StepResult


# ┌────────────────────────────────────────────────────────────┐
# │ Step  « one flow field and its readouts »                  │
# └────────────────────────────────────────────────────────────┘
def field_to_frame(field: FlowField, diameter: np.ndarray | None = None) -> pd.DataFrame:
    frame = pd.DataFrame({
        "azimuth_rad": field.azimuth,
        "elevation_rad": field.elevation,
        "flow_azimuth_rad": field.flow[:, 0],
        "flow_elevation_rad": field.flow[:, 1],
        "magnitude_rad": field.magnitude,
        "distance_m": field.distance,
        "valid": field.valid,
        "in_fov": field.in_fov,
    })
    if diameter is not None:
        frame["diameter_m"] = diameter
    return frame


def save_step(
    result: StepResult, out_dir: Path, stem: str, extra: dict[str, Any] | None = None
) -> tuple[Path, Path]:
    out_dir.mkdir(parents=True, exist_ok=True)
    frame = field_to_frame(result.field)
    for name, component in result.components.items():
        frame[f"{name}_magnitude_rad"] = component.magnitude
        frame[f"{name}_in_fov"] = component.in_fov
    parquet = out_dir / f"{stem}.parquet"
    frame.to_parquet(parquet, index=False)
    meta = {
        "kind": "step",
        **_provenance(),
        "config": to_plain(result.config),
        "dt_s": result.dt,
        "cloud_radius_m": result.config.cloud.radius_m,
        "n_particles": result.config.cloud.count(),
        "seal_before": {"position": result.before.position.tolist(),
                        "euler": result.before.euler.tolist()},
        "seal_after": {"position": result.after.position.tolist(),
                       "euler": result.after.euler.tolist()},
        "metrics": result.metrics.as_dict(),
        **to_plain(extra or {}),
    }
    return parquet, write_yaml(meta, out_dir / f"{stem}.yaml")


# ┌────────────────────────────────────────────────────────────┐
# │ Dive  « a trajectory and its per-step readouts »           │
# └────────────────────────────────────────────────────────────┘
def save_dive(
    trajectory: DiveTrajectory,
    metrics: pd.DataFrame | None,
    out_dir: Path,
    stem: str,
    extra: dict[str, Any] | None = None,
) -> tuple[Path, Path]:
    out_dir.mkdir(parents=True, exist_ok=True)
    frame = trajectory.to_frame()
    if metrics is not None:
        frame = frame.merge(metrics, left_index=True, right_index=True, how="left")
    parquet = out_dir / f"{stem}.parquet"
    frame.to_parquet(parquet, index=False)
    meta = {
        "kind": "dive",
        **_provenance(),
        "shape": trajectory.shape,
        "sample_rate_hz": trajectory.sample_rate,
        "duration_s": float(trajectory.time[-1]),
        "min_depth_m": float(trajectory.position[:, 2].min()),
        **(extra or {}),
    }
    if metrics is not None:
        meta["metrics_summary"] = {
            col: float(np.nanmedian(metrics[col]))
            for col in metrics.columns if np.isfinite(metrics[col]).any()
        }
    return parquet, write_yaml(meta, out_dir / f"{stem}.yaml")


# ┌────────────────────────────────────────────────────────────┐
# │ Helpers  « serialisation and collection »                  │
# └────────────────────────────────────────────────────────────┘
def _provenance() -> dict[str, str]:
    return {
        "sealsim_version": __version__,
        "written": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
    }


def to_plain(obj: Any) -> Any:
    """Dataclasses, numpy and paths to yaml-friendly Python values."""
    if dataclasses.is_dataclass(obj) and not isinstance(obj, type):
        plain = {f.name: to_plain(getattr(obj, f.name)) for f in dataclasses.fields(obj)}
        plain["__class__"] = type(obj).__name__
        return plain
    if isinstance(obj, np.ndarray):
        return obj.tolist()
    if isinstance(obj, (np.floating, np.integer)):
        return obj.item()
    if isinstance(obj, (list, tuple)):
        return [to_plain(v) for v in obj]
    if isinstance(obj, dict):
        return {str(k): to_plain(v) for k, v in obj.items()}
    if isinstance(obj, Path):
        return str(obj)
    return obj


def write_yaml(data: dict[str, Any], path: Path) -> Path:
    path.write_text(yaml.safe_dump(data, sort_keys=False), encoding="utf-8")
    return path


def load_metadata(path: Path) -> dict[str, Any]:
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def collect_metadata(directory: Path, pattern: str = "*.yaml") -> pd.DataFrame:
    """One row per yaml file with nested keys flattened as a.b.c."""
    rows = [
        {"file": str(p.relative_to(directory)), **_flatten(load_metadata(p))}
        for p in sorted(directory.rglob(pattern))
    ]
    return pd.DataFrame(rows)


def _flatten(data: dict[str, Any], prefix: str = "") -> dict[str, Any]:
    flat: dict[str, Any] = {}
    for key, value in data.items():
        name = f"{prefix}{key}"
        if isinstance(value, dict):
            flat.update(_flatten(value, f"{name}."))
        elif isinstance(value, list):
            flat[name] = str(value)
        else:
            flat[name] = value
    return flat
