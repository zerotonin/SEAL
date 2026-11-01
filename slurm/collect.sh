#!/usr/bin/env bash
# Gather the run yamls of one experiment into a table, as a short batch job
# (the login node is for orchestration only).
#
#   slurm/collect.sh <experiment name>
set -euo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck disable=SC1091
source "$HERE/load_paths.sh" hpc

NAME="$1"
LOG_DIR="$SEALSIM_DATA_ROOT/logs/$NAME"
mkdir -p "$LOG_DIR" "$SEALSIM_DATA_ROOT/tables"
sbatch --account="$SBATCH_ACCOUNT" --partition="$SBATCH_PARTITION" \
    --job-name="sealsim-collect-$NAME" --time=00:20:00 --mem=8G --cpus-per-task=1 \
    --output="$LOG_DIR/collect_%j.out" --error="$LOG_DIR/collect_%j.err" \
    --wrap="source '$SEALSIM_CONDA_SETUP' && conda activate '$SEALSIM_CONDA_ENV' \
            && cd '$SEALSIM_CODE_ROOT' \
            && sealsim collect '$SEALSIM_DATA_ROOT/$NAME' --out '$SEALSIM_DATA_ROOT/tables/$NAME'"
