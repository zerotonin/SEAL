# ╔══════════════════════════════════════════════════════════════════╗
# ║  sealsim — dive                                                  ║
# ║  « a seal dive from surface videos and a depth logger »          ║
# ╠══════════════════════════════════════════════════════════════════╣
# ║  Horizontal movement is a Markov chain over 50 two-dimensional   ║
# ║  prototypical movements (thrust, slip, yaw) from 25 Hz video.    ║
# ║  Depth and pitch follow the U or V phase statistics digitised    ║
# ║  from MINOSplus Fig. 16 at the logger rate of 0.2 Hz. The two    ║
# ║  sources were never recorded together, so the x-y path ignores   ║
# ║  pitch, as in the thesis, and body velocities are recovered      ║
# ║  from the resulting pose sequence. Kept as provenance for the    ║
# ║  13 PMs.                                                         ║
# ╚══════════════════════════════════════════════════════════════════╝

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.ndimage import gaussian_filter1d

from sealsim import config
from sealsim.constants import (
    DIVE_LOGGER_RATE_HZ,
    DIVE_SHAPES,
    FLOOR_MARGIN_M,
    OCEAN_FLOOR_Z_M,
    OCEAN_SURFACE_Z_M,
    PHASE_TRANSITION_SIGMA_S,
    PM2D_FILE,
    PM5D_FILE,
    PM_START_CDF_FILE,
    PM_TRANSITION_CDF_FILE,
    VELOCITY_COLUMNS,
    VIDEO_FRAME_RATE_HZ,
    DivePhase,
    FloatArray,
    IntArray,
)
from sealsim.geometry import body_to_world, rates_between

# ┌────────────────────────────────────────────────────────────┐
# │ Tables  « prototypical movements and their Markov chain »  │
# └────────────────────────────────────────────────────────────┘
PACKAGE_DATA_DIR = Path(__file__).resolve().parent / "data"


def default_data_dir() -> Path:
    """Input tables ship inside the package; SEALSIM_INPUT_DATA or ``input_data`` overrides."""
    override = config.get("input_data", default=None)
    if override:
        return Path(override).expanduser()
    return PACKAGE_DATA_DIR


@dataclass(frozen=True)
class PMTables:
    """50 two-dimensional PMs [thrust m/s, slip m/s, yaw rad/s] with start and transition CDFs."""

    movements: FloatArray
    start_cdf: FloatArray
    transition_cdf: FloatArray


def load_pm_tables(data_dir: Path | None = None) -> PMTables:
    folder = (data_dir or default_data_dir()) / "prototypical_movements"
    movements = np.loadtxt(folder / PM2D_FILE, delimiter=",")
    movements[:, 2] = np.deg2rad(movements[:, 2])
    return PMTables(
        movements=movements,
        start_cdf=np.loadtxt(folder / PM_START_CDF_FILE, delimiter=","),
        transition_cdf=np.loadtxt(folder / PM_TRANSITION_CDF_FILE, delimiter=","),
    )


def load_pm5d(data_dir: Path | None = None) -> pd.DataFrame:
    """The 13 five-dimensional PMs behind every figure, with group labels."""
    folder = (data_dir or default_data_dir()) / "prototypical_movements"
    return pd.read_csv(folder / PM5D_FILE)


def pm5d_velocity(table: pd.DataFrame, pm_id: int) -> FloatArray:
    row = table.loc[table["pm_id"] == pm_id]
    if row.empty:
        raise KeyError(f"pm_id {pm_id} not in table; have {table['pm_id'].tolist()}")
    columns = ["thrust_mps", "slip_mps", "lift_mps", "yaw_radps", "pitch_radps", "roll_radps"]
    return row[columns].to_numpy(dtype=float)[0]


def sample_pm_sequence(tables: PMTables, n: int, rng: np.random.Generator) -> IntArray:
    """Markov chain over PM indices, drawn by inverse CDF lookup."""
    draws = rng.uniform(size=n)
    sequence = np.empty(n, dtype=int)
    sequence[0] = np.searchsorted(tables.start_cdf, draws[0])
    for i in range(1, n):
        sequence[i] = np.searchsorted(tables.transition_cdf[sequence[i - 1]], draws[i])
    return np.clip(sequence, 0, tables.movements.shape[0] - 1)


# ┌────────────────────────────────────────────────────────────┐
# │ Profiles  « depth and pitch from the phase statistics »    │
# └────────────────────────────────────────────────────────────┘
def generate_depth_pitch(
    phases: tuple[DivePhase, ...],
    duration_s: float,
    sample_rate: float,
    rng: np.random.Generator,
    floor_z: float = OCEAN_FLOOR_Z_M.value,
    surface_z: float = OCEAN_SURFACE_Z_M,
) -> tuple[FloatArray, FloatArray, IntArray]:
    """Depth [m], pitch [deg] and phase index at the simulation rate.

    The logger sampled every 5 s, so pitch and vertical speed are drawn once per
    logger interval, held, and smoothed with a short Gaussian that stands in for
    the saccadic transitions between phases. Descent ends early when the floor
    is reached, ascent when the surface is reached.
    """
    n = int(round(duration_s * sample_rate)) + 1
    logger_dt = 1.0 / DIVE_LOGGER_RATE_HZ
    n_knots = int(np.ceil(duration_s / logger_dt)) + 1
    knot_time = np.arange(n_knots) * logger_dt
    ends = np.array([p.end_fraction for p in phases]) * duration_s
    last = len(phases) - 1

    pitch_knots = np.empty(n_knots)
    speed_knots = np.empty(n_knots)
    phase_knots = np.empty(n_knots, dtype=int)
    z = surface_z
    phase = 0
    for k, t in enumerate(knot_time):
        while phase < last and t >= ends[phase]:
            phase += 1
        if phases[phase].name == "down" and z <= floor_z + FLOOR_MARGIN_M:
            phase += 1
        elif phases[phase].name == "up" and z >= surface_z:
            phase += 1
        p = phases[phase]
        pitch_knots[k] = rng.normal(p.pitch_mean_deg, p.pitch_sd_deg)
        speed_knots[k] = rng.normal(p.vertical_speed_mean_mps, p.vertical_speed_sd_mps)
        phase_knots[k] = phase
        z = float(np.clip(z + speed_knots[k] * logger_dt, floor_z, surface_z))

    time = np.arange(n) / sample_rate
    idx = np.minimum((time / logger_dt).astype(int), n_knots - 1)
    sigma = PHASE_TRANSITION_SIGMA_S * sample_rate
    pitch = gaussian_filter1d(pitch_knots[idx], sigma, mode="nearest")
    speed = gaussian_filter1d(speed_knots[idx], sigma, mode="nearest")
    depth = np.clip(surface_z + np.cumsum(speed) / sample_rate, floor_z, surface_z)
    depth = np.minimum(depth, surface_z - 1e-5)
    return depth, pitch, phase_knots[idx]


# ┌────────────────────────────────────────────────────────────┐
# │ Trajectory  « the assembled 6-DoF pose sequence »          │
# └────────────────────────────────────────────────────────────┘
@dataclass
class DiveTrajectory:
    shape: str
    sample_rate: float
    position: FloatArray
    euler: FloatArray
    velocity_body: FloatArray
    pm_index: IntArray
    phase: IntArray

    @property
    def time(self) -> FloatArray:
        return np.arange(self.position.shape[0]) / self.sample_rate

    def to_frame(self) -> pd.DataFrame:
        n = self.position.shape[0]
        velocity = np.vstack([self.velocity_body, np.full((1, 6), np.nan)])
        data = {
            "time_s": self.time,
            "x_m": self.position[:, 0], "y_m": self.position[:, 1], "z_m": self.position[:, 2],
            "yaw_rad": self.euler[:, 0], "pitch_rad": self.euler[:, 1],
            "roll_rad": self.euler[:, 2],
            "pm_index": self.pm_index, "phase": self.phase,
        }
        for j, name in enumerate(VELOCITY_COLUMNS):
            data[name] = velocity[:n, j]
        return pd.DataFrame(data)


def generate_dive(
    shape: str,
    duration_s: float,
    sample_rate: float,
    rng: np.random.Generator,
    tables: PMTables | None = None,
) -> DiveTrajectory:
    if shape not in DIVE_SHAPES:
        raise ValueError(f"shape must be one of {sorted(DIVE_SHAPES)}, got {shape!r}")
    tables = tables or load_pm_tables()
    n = int(round(duration_s * sample_rate)) + 1
    time = np.arange(n) / sample_rate

    n_video = int(round(duration_s * VIDEO_FRAME_RATE_HZ)) + 1
    pm_video = sample_pm_sequence(tables, n_video, rng)
    video_time = np.arange(n_video) / VIDEO_FRAME_RATE_HZ
    thrust, slip, yaw_rate = (
        np.interp(time, video_time, tables.movements[pm_video, j]) for j in range(3)
    )
    pm_index = pm_video[np.minimum((time * VIDEO_FRAME_RATE_HZ).astype(int), n_video - 1)]
    yaw = np.concatenate([[0.0], np.cumsum(0.5 * (yaw_rate[1:] + yaw_rate[:-1])) / sample_rate])

    depth, pitch_deg, phase = generate_depth_pitch(
        DIVE_SHAPES[shape], duration_s, sample_rate, rng
    )
    vx = thrust * np.cos(yaw) + slip * np.sin(yaw)
    vy = -thrust * np.sin(yaw) + slip * np.cos(yaw)
    x = np.concatenate([[0.0], np.cumsum(0.5 * (vx[1:] + vx[:-1])) / sample_rate])
    y = np.concatenate([[0.0], np.cumsum(0.5 * (vy[1:] + vy[:-1])) / sample_rate])

    position = np.column_stack([x, y, depth])
    euler = np.column_stack([yaw, np.deg2rad(pitch_deg), np.zeros(n)])
    return DiveTrajectory(
        shape=shape, sample_rate=sample_rate, position=position, euler=euler,
        velocity_body=body_velocities(position, euler, 1.0 / sample_rate),
        pm_index=pm_index, phase=phase,
    )


def body_velocities(position: FloatArray, euler: FloatArray, dt: float) -> FloatArray:
    """(thrust, slip, lift, yaw, pitch, roll rates) that step each pose to the next."""
    translation = body_to_world(euler[:-1]).inv().apply(np.diff(position, axis=0)) / dt
    rates = rates_between(euler[:-1], euler[1:], dt)
    return np.hstack([translation, rates])
