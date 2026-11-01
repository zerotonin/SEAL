#!/usr/bin/env bash
# sealsim: resolve local_paths.json into SEALSIM_* and SBATCH_* variables.
#
#   source slurm/load_paths.sh [profile]      (default profile: hpc)
#
# Pure-stdlib config.py, so this works on a login node before conda is active.
# Meant to be sourced; it does not set -e so that it cannot kill your shell.
_sealsim_profile="${1:-hpc}"
_sealsim_repo="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
if _sealsim_exports="$(python3 "$_sealsim_repo/src/sealsim/config.py" --export --profile "$_sealsim_profile")"; then
    eval "$_sealsim_exports"
    export SEALSIM_CODE_ROOT="${SEALSIM_CODE_ROOT:-$_sealsim_repo}"
    echo "sealsim: profile $_sealsim_profile, data_root $SEALSIM_DATA_ROOT, partition ${SBATCH_PARTITION:-unset}"
else
    echo "sealsim: could not resolve local_paths.json; copy local_paths.template.json and fill it in" >&2
    return 1 2>/dev/null || exit 1
fi
unset _sealsim_profile _sealsim_repo _sealsim_exports
