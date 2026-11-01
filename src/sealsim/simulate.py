# ╔══════════════════════════════════════════════════════════════════╗
# ║  sealsim — simulate                                              ║
# ║  « one step, or a whole dive, through the cloud »                ║
# ╠══════════════════════════════════════════════════════════════════╣
# ║  The orchestration layer: build a cloud from a seed, move it by  ║
# ║  (current - seal velocity) dt, step the agent, compute the flow  ║
# ║  and its readouts. A step is run three times from the same       ║
# ║  cloud (full, translation only, rotation only) for the flow      ║
# ║  index. The backend field of StepConfig picks numpy or cupy.     ║
# ╚══════════════════════════════════════════════════════════════════╝

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Iterator

import numpy as np

from sealsim.agent import SealState, advance, rotation_part, translation_part, world_velocity
from sealsim.backend import get_array_module, to_backend
from sealsim.cloud import CloudSpec, ParticleCloud, advect_cloud, build_cloud, visible_at
from sealsim.constants import (
    DEFAULT_SEAL_DEPTH_M,
    MAX_STEP_FRACTION_OF_RADIUS,
    MAX_STEP_ROTATION_RAD,
    FloatArray,
    Vec3,
    Vec6,
)
from sealsim.dive import DiveTrajectory
from sealsim.environment import Environment
from sealsim.opticflow import FlowField, FlowMetrics, compute_flow, summarise


# ┌────────────────────────────────────────────────────────────┐
# │ Configuration  « everything a single step depends on »     │
# └────────────────────────────────────────────────────────────┘
@dataclass(frozen=True)
class StepConfig:
    velocity: Vec6
    position: Vec3 = (0.0, 0.0, DEFAULT_SEAL_DEPTH_M)
    euler: Vec3 = (0.0, 0.0, 0.0)
    dt: float | None = None
    cloud: CloudSpec = field(default_factory=lambda: CloudSpec(n_particles=1000))
    environment: Environment = field(default_factory=Environment)
    seed: int = 0
    decompose: bool = True
    backend: str = "numpy"


def step_duration(cfg: StepConfig) -> float:
    """Longest dt that moves at most half the cloud radius and rotates less than pi."""
    if cfg.dt is not None:
        return float(cfg.dt)
    v = np.asarray(cfg.velocity, dtype=float)
    limits = []
    speed = np.linalg.norm(v[:3])
    if speed > 0:
        limits.append(MAX_STEP_FRACTION_OF_RADIUS * cfg.cloud.radius_m / speed)
    rate = np.linalg.norm(v[3:])
    if rate > 0:
        limits.append(MAX_STEP_ROTATION_RAD / rate)
    if not limits:
        raise ValueError("velocity is zero; give dt explicitly")
    return float(min(limits))


# ┌────────────────────────────────────────────────────────────┐
# │ Single step  « the unit every sweep is built from »        │
# └────────────────────────────────────────────────────────────┘
@dataclass
class StepResult:
    config: StepConfig
    dt: float
    before: SealState
    after: SealState
    field: FlowField
    metrics: FlowMetrics
    components: dict[str, FlowField]


def run_step(cfg: StepConfig) -> StepResult:
    rng = np.random.default_rng(cfg.seed)
    cloud = build_cloud(cfg.cloud, rng, get_array_module(cfg.backend))
    dt = step_duration(cfg)
    state = SealState.at(cfg.position, cfg.euler)
    velocity = np.asarray(cfg.velocity, dtype=float)

    components: dict[str, FlowField] = {}
    trans_sum = rot_sum = float("nan")
    if cfg.decompose:
        trans_field, _ = advance_cloud(cloud.copy(), cfg.environment, state,
                                       translation_part(velocity), dt)
        rot_field, _ = advance_cloud(cloud.copy(), cfg.environment, state,
                                     rotation_part(velocity), dt)
        components = {"translation": trans_field, "rotation": rot_field}
    field_full, after = advance_cloud(cloud, cfg.environment, state, velocity, dt)
    if cfg.decompose:
        common = field_full.in_fov & trans_field.in_fov & rot_field.in_fov
        trans_sum = float(trans_field.magnitude[common].sum())
        rot_sum = float(rot_field.magnitude[common].sum())
    metrics = summarise(field_full, velocity, trans_sum, rot_sum)
    return StepResult(cfg, dt, state, after, field_full, metrics, components)


def advance_cloud(
    cloud: ParticleCloud,
    env: Environment,
    state: SealState,
    velocity: FloatArray,
    dt: float,
) -> tuple[FlowField, SealState]:
    """Move cloud and seal by one step; return the flow seen and the new pose."""
    xp = cloud.xp
    absolute = to_backend(state.position, xp) + cloud.position
    seal_velocity = to_backend(world_velocity(state, velocity), xp)
    displacement = (env.current_at(absolute) - seal_velocity) * dt
    step = advect_cloud(cloud, displacement)
    after = advance(state, velocity, dt)
    absolute_after = to_backend(after.position, xp) + step.post
    valid = (
        visible_at(cloud, step.pre)
        & visible_at(cloud, step.post)
        & env.in_water(absolute[:, 2])
        & env.in_water(absolute_after[:, 2])
        & ~step.exited
    )
    return compute_flow(step.pre, step.post, state.rotation(), after.rotation(), valid), after


# ┌────────────────────────────────────────────────────────────┐
# │ Dive  « the same step, chained along a trajectory »        │
# └────────────────────────────────────────────────────────────┘
def iter_dive_steps(
    trajectory: DiveTrajectory,
    cloud_spec: CloudSpec,
    env: Environment,
    seed: int = 0,
    backend: str = "numpy",
) -> Iterator[tuple[int, FlowMetrics]]:
    """Yield (sample index, metrics) per step; the caller adds progress reporting."""
    rng = np.random.default_rng(seed)
    cloud = build_cloud(cloud_spec, rng, get_array_module(backend))
    dt = 1.0 / trajectory.sample_rate
    for i in range(trajectory.velocity_body.shape[0]):
        state = SealState(trajectory.position[i], trajectory.euler[i])
        velocity = trajectory.velocity_body[i]
        field_i, _ = advance_cloud(cloud, env, state, velocity, dt)
        yield i, summarise(field_i, velocity)
