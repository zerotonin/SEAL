# ╔══════════════════════════════════════════════════════════════════╗
# ║  sealsim — cli                                                   ║
# ║  « one entry point, one subcommand per pipeline stage »          ║
# ╠══════════════════════════════════════════════════════════════════╣
# ║  `sealsim config`  show the resolved machine settings.           ║
# ║  Later sprints add: step, dive, sweep, collect, figures.         ║
# ╚══════════════════════════════════════════════════════════════════╝

from __future__ import annotations

import argparse

from sealsim import __version__
from sealsim import config as cfg


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="sealsim", description="SEnsory Aquatic odometry simuLator"
    )
    parser.add_argument("--version", action="version", version=f"sealsim {__version__}")
    sub = parser.add_subparsers(dest="command", required=True)
    p_cfg = sub.add_parser("config", help="show resolved machine settings")
    p_cfg.add_argument("--profile", default=None)
    p_cfg.add_argument("--export", action="store_true")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.command == "config":
        cfg_argv = []
        if args.profile:
            cfg_argv += ["--profile", args.profile]
        if args.export:
            cfg_argv.append("--export")
        return cfg.main(cfg_argv)
    raise SystemExit(f"unknown command {args.command}")


if __name__ == "__main__":
    raise SystemExit(main())
