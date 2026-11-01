#!/usr/bin/env bash
# Submit an experiment grid as a SLURM job array.
#
#   slurm/submit_sweep.sh experiments/currents.yaml [N_CHUNKS] [extra sbatch flags]
#
# Account, partition, data root and conda come from local_paths.json (hpc profile).
# Results land in <data_root>/<experiment name>, logs in <data_root>/logs/<name>.
set -euo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck disable=SC1091
source "$HERE/load_paths.sh" hpc

YAML="$(realpath "$1")"
N_CHUNKS="${2:-20}"
NAME="$(grep -E '^name:' "$YAML" | head -n 1 | awk '{print $2}')"
if [[ -z "$NAME" ]]; then echo "no 'name:' in $YAML" >&2; exit 1; fi
LOG_DIR="$SEALSIM_DATA_ROOT/logs/$NAME"
mkdir -p "$LOG_DIR"

sbatch --account="$SBATCH_ACCOUNT" --partition="$SBATCH_PARTITION" \
    --job-name="sealsim-$NAME" --array="0-$((N_CHUNKS - 1))" \
    --output="$LOG_DIR/%A_%a.out" --error="$LOG_DIR/%A_%a.err" \
    "${@:3}" "$HERE/run_chunk.sbatch" "$YAML" "$N_CHUNKS"
echo "submitted $NAME as $N_CHUNKS array tasks; watch with: squeue --me --name=sealsim-$NAME"
