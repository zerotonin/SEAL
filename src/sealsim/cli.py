# ╔══════════════════════════════════════════════════════════════════╗
# ║  sealsim — cli                                                   ║
# ║  « one entry point, one subcommand per pipeline stage »          ║
# ╠══════════════════════════════════════════════════════════════════╣
# ║  sealsim config show the resolved machine settings sealsim step  ║
# ║  one 6-DoF step through a fresh cloud sealsim dive generate a U  ║
# ║  or V dive, optionally with flow Progress bars live here, never  ║
# ║  in the library modules.                                         ║
# ╚══════════════════════════════════════════════════════════════════╝

from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd
from rich.console import Console
from rich.table import Table

from sealsim import __version__
from sealsim import config as cfg
from sealsim.cloud import CloudSpec
from sealsim.constants import (
    DEFAULT_SAMPLE_RATE_HZ,
    DEFAULT_SEAL_DEPTH_M,
    PARTICLE_DIAMETER_RANGE_M,
    VELOCITY_COLUMNS,
)
from sealsim.environment import Environment, UniformCurrent

console = Console()


# ┌────────────────────────────────────────────────────────────┐
# │ Parser  « arguments grouped by what they configure »       │
# └────────────────────────────────────────────────────────────┘
def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="sealsim", description="SEnsory Aquatic odometry simuLator"
    )
    parser.add_argument("--version", action="version", version=f"sealsim {__version__}")
    sub = parser.add_subparsers(dest="command", required=True)

    p_cfg = sub.add_parser("config", help="show resolved machine settings")
    p_cfg.add_argument("--profile", default=None)
    p_cfg.add_argument("--export", action="store_true")

    p_step = sub.add_parser("step", help="one step through a fresh particle cloud")
    motion = p_step.add_mutually_exclusive_group(required=True)
    motion.add_argument("--velocity", nargs=6, type=float, metavar=tuple(VELOCITY_COLUMNS),
                        help="m/s and rad/s in the body frame")
    motion.add_argument("--pm", type=int, help="pm_id from data/prototypical_movements")
    p_step.add_argument("--dt", type=float, default=None,
                        help="step duration [s]; default: half-radius rule")
    p_step.add_argument("--depth", type=float, default=DEFAULT_SEAL_DEPTH_M)
    p_step.add_argument("--euler", nargs=3, type=float, default=(0.0, 0.0, 0.0),
                        metavar=("yaw", "pitch", "roll"))
    _add_cloud_arguments(p_step)
    _add_environment_arguments(p_step)
    p_step.add_argument("--seed", type=int, default=0)
    p_step.add_argument("--no-decompose", action="store_true")
    p_step.add_argument("--out", type=Path, default=None, help="directory for parquet + yaml")
    p_step.add_argument("--stem", default="step")

    p_dive = sub.add_parser("dive", help="generate a dive trajectory")
    p_dive.add_argument("--shape", choices=("u", "v"), default="u")
    p_dive.add_argument("--duration", type=float, default=240.0, help="seconds")
    p_dive.add_argument("--sample-rate", type=float, default=DEFAULT_SAMPLE_RATE_HZ)
    p_dive.add_argument("--flow", action="store_true", help="compute flow readouts per step")
    _add_cloud_arguments(p_dive)
    _add_environment_arguments(p_dive)
    p_dive.add_argument("--seed", type=int, default=0)
    p_dive.add_argument("--out", type=Path, default=None)
    p_dive.add_argument("--stem", default="dive")
    return parser


def _add_cloud_arguments(parser: argparse.ArgumentParser) -> None:
    group = parser.add_argument_group("cloud")
    group.add_argument("--acuity", type=float, default=CloudSpec().acuity_deg, help="degrees")
    group.add_argument("--diameter", nargs=2, type=float, default=PARTICLE_DIAMETER_RANGE_M,
                       metavar=("min_m", "max_m"))
    count = group.add_mutually_exclusive_group()
    count.add_argument("--n-particles", type=int, default=None)
    count.add_argument("--density", type=float, default=None, help="particles per m^3")


def _add_environment_arguments(parser: argparse.ArgumentParser) -> None:
    group = parser.add_argument_group("environment")
    group.add_argument("--current", nargs=3, type=float, default=(0.0, 0.0, 0.0),
                       metavar=("vx", "vy", "vz"), help="world-frame m/s")
    group.add_argument("--floor", type=float, default=Environment().floor_z)


# ┌────────────────────────────────────────────────────────────┐
# │ Commands  « thin glue between argparse and the library »   │
# └────────────────────────────────────────────────────────────┘
def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.command == "config":
        return _cmd_config(args)
    if args.command == "step":
        return _cmd_step(args)
    if args.command == "dive":
        return _cmd_dive(args)
    raise SystemExit(f"unknown command {args.command}")


def _cmd_config(args: argparse.Namespace) -> int:
    cfg_argv: list[str] = []
    if args.profile:
        cfg_argv += ["--profile", args.profile]
    if args.export:
        cfg_argv.append("--export")
    return cfg.main(cfg_argv)


def _cloud_from_args(args: argparse.Namespace) -> CloudSpec:
    n_particles = args.n_particles if (args.n_particles or args.density) else 1000
    return CloudSpec(
        acuity_deg=args.acuity, diameter_range_m=tuple(args.diameter),
        n_particles=n_particles, number_density_per_m3=args.density,
    )


def _environment_from_args(args: argparse.Namespace) -> Environment:
    return Environment(floor_z=args.floor, current=UniformCurrent(tuple(args.current)))


def _cmd_step(args: argparse.Namespace) -> int:
    from sealsim import results
    from sealsim.dive import load_pm5d, pm5d_velocity
    from sealsim.simulate import StepConfig, run_step

    velocity = args.velocity if args.velocity else pm5d_velocity(load_pm5d(), args.pm)
    config = StepConfig(
        velocity=tuple(float(v) for v in velocity),
        position=(0.0, 0.0, args.depth), euler=tuple(args.euler), dt=args.dt,
        cloud=_cloud_from_args(args), environment=_environment_from_args(args),
        seed=args.seed, decompose=not args.no_decompose,
    )
    result = run_step(config)
    _print_metrics(result.metrics.as_dict(), f"step  dt = {result.dt:.4g} s, "
                   f"R = {config.cloud.radius_m:.3f} m, N = {config.cloud.count()}")
    if args.out:
        parquet, meta = results.save_step(result, args.out, args.stem)
        console.print(f"wrote {parquet.name} and {meta.name} to {args.out}")
    return 0


def _cmd_dive(args: argparse.Namespace) -> int:
    from tqdm import tqdm

    from sealsim import results
    from sealsim.dive import generate_dive
    from sealsim.simulate import iter_dive_steps

    rng = np.random.default_rng(args.seed)
    trajectory = generate_dive(args.shape, args.duration, args.sample_rate, rng)
    metrics = None
    if args.flow:
        steps = iter_dive_steps(trajectory, _cloud_from_args(args),
                                _environment_from_args(args), seed=args.seed)
        rows = {i: m.as_dict() for i, m in tqdm(steps, total=trajectory.velocity_body.shape[0],
                                                  desc="flow per step")}
        metrics = pd.DataFrame.from_dict(rows, orient="index")
    console.print(f"{args.shape}-dive  {args.duration:.0f} s at {args.sample_rate:g} Hz, "
                  f"deepest point {trajectory.position[:, 2].min():.1f} m")
    if args.out:
        extra = {"seed": args.seed, "cloud": results.to_plain(_cloud_from_args(args))}
        parquet, meta = results.save_dive(trajectory, metrics, args.out, args.stem, extra)
        console.print(f"wrote {parquet.name} and {meta.name} to {args.out}")
    return 0


def _print_metrics(metrics: dict[str, float | int], title: str) -> None:
    table = Table(title=title)
    table.add_column("readout")
    table.add_column("value", justify="right")
    for key, value in metrics.items():
        text = f"{value:.4g}" if isinstance(value, float) else str(value)
        table.add_row(key, text)
    console.print(table)


if __name__ == "__main__":
    raise SystemExit(main())
