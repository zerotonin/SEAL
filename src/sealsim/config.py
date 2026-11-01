# ╔══════════════════════════════════════════════════════════════════╗
# ║  sealsim — config                                                ║
# ║  « machine-specific paths without a single hard-coded one »      ║
# ╠══════════════════════════════════════════════════════════════════╣
# ║  Resolves data_root, code_root, conda and SLURM settings from, in ║
# ║  order of priority: environment variable SEALSIM_<KEY>, the      ║
# ║  git-ignored local_paths.json (profiles local / hpc), a default. ║
# ║                                                                  ║
# ║  Pure standard library so `python -m sealsim.config --export`    ║
# ║  works on a login node before any environment is activated.      ║
# ╚══════════════════════════════════════════════════════════════════╝

from __future__ import annotations

import argparse
import json
import os
import shlex
import sys
from pathlib import Path

ENV_PREFIX = "SEALSIM_"
TEMPLATE_NAME = "local_paths.template.json"
LOCAL_NAME = "local_paths.json"
DEFAULT_PROFILE = "local"

PATH_KEYS: tuple[str, ...] = (
    "data_root",
    "code_root",
    "conda_setup",
    "conda_env",
    "slurm_account",
    "slurm_partition",
)
PATH_LIKE_KEYS: frozenset[str] = frozenset({"data_root", "code_root", "conda_setup"})


class ConfigError(RuntimeError):
    """Raised when a required machine setting cannot be resolved."""


# ┌────────────────────────────────────────────────────────────┐
# │ Locating files  « repo root and the per-machine json »     │
# └────────────────────────────────────────────────────────────┘


def repo_root() -> Path:
    """Return the checkout root (parent of ``src/``) or the install prefix."""
    here = Path(__file__).resolve()
    for parent in here.parents:
        if (parent / TEMPLATE_NAME).is_file():
            return parent
    return here.parents[2]


def local_paths_file() -> Path:
    return repo_root() / LOCAL_NAME


def is_configured() -> bool:
    return local_paths_file().is_file()


def load_config() -> dict:
    path = local_paths_file()
    if not path.is_file():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


# ┌────────────────────────────────────────────────────────────┐
# │ Resolution  « env var > json profile > default »           │
# └────────────────────────────────────────────────────────────┘


def active_profile(cfg: dict | None = None) -> str:
    if ENV_PREFIX + "PROFILE" in os.environ:
        return os.environ[ENV_PREFIX + "PROFILE"]
    cfg = load_config() if cfg is None else cfg
    return cfg.get("active_profile", DEFAULT_PROFILE)


def _expand(key: str, value: str) -> str:
    if key not in PATH_LIKE_KEYS:
        return value
    p = Path(os.path.expanduser(value))
    if not p.is_absolute():
        p = repo_root() / p
    return str(p)


def _is_placeholder(value: str) -> bool:
    return value.strip().startswith("<") and value.strip().endswith(">")


def get(key: str, default: str | None = None, profile: str | None = None) -> str | None:
    """Resolve one key; ``None`` when nothing is set and no default given."""
    if key not in PATH_KEYS:
        raise KeyError(f"unknown config key {key!r}; known: {PATH_KEYS}")
    env_name = ENV_PREFIX + key.upper()
    if env_name in os.environ:
        return _expand(key, os.environ[env_name])
    cfg = load_config()
    prof = profile or active_profile(cfg)
    value = cfg.get("profiles", {}).get(prof, {}).get(key)
    if value is not None and not _is_placeholder(str(value)):
        return _expand(key, str(value))
    return default


def require(key: str, profile: str | None = None) -> str:
    """Resolve one key or fail loudly, naming the template to copy."""
    value = get(key, profile=profile)
    if value is None:
        raise ConfigError(
            f"{key!r} is not set. Export {ENV_PREFIX + key.upper()} or copy "
            f"{TEMPLATE_NAME} to {LOCAL_NAME} next to the repo root and fill "
            f"in profile {profile or active_profile()!r}."
        )
    return value


def data_root(profile: str | None = None) -> Path:
    return Path(require("data_root", profile))


# ┌────────────────────────────────────────────────────────────┐
# │ CLI  « shell exports for the SLURM helpers »               │
# └────────────────────────────────────────────────────────────┘


def _export_lines(profile: str | None) -> list[str]:
    lines = [f"export {ENV_PREFIX}PROFILE={shlex.quote(profile or active_profile())}"]
    for key in PATH_KEYS:
        value = get(key, profile=profile)
        if value is not None:
            lines.append(f"export {ENV_PREFIX}{key.upper()}={shlex.quote(value)}")
    account = get("slurm_account", profile=profile)
    partition = get("slurm_partition", profile=profile)
    if account:
        lines.append(f"export SBATCH_ACCOUNT={shlex.quote(account)}")
    if partition:
        lines.append(f"export SBATCH_PARTITION={shlex.quote(partition)}")
    return lines


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Resolve sealsim machine settings.")
    parser.add_argument("--profile", default=None, help="profile name (default: active)")
    parser.add_argument("--export", action="store_true", help="print shell export lines")
    args = parser.parse_args(argv)
    if not is_configured() and not any(
        (ENV_PREFIX + k.upper()) in os.environ for k in PATH_KEYS
    ):
        print(
            f"sealsim: {LOCAL_NAME} not found. Copy {TEMPLATE_NAME} to {LOCAL_NAME} "
            f"and fill it in before running anything.",
            file=sys.stderr,
        )
        return 1
    if args.export:
        print("\n".join(_export_lines(args.profile)))
        return 0
    print(f"profile: {args.profile or active_profile()}")
    for key in PATH_KEYS:
        print(f"{key:16s} {get(key, profile=args.profile)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
