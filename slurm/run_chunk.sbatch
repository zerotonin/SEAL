#!/usr/bin/env bash
# One array task = one chunk of an experiment grid. Submit through submit_sweep.sh,
# which passes account, partition, array range and log paths from local_paths.json.
#SBATCH --time=02:00:00
#SBATCH --cpus-per-task=4
#SBATCH --mem=16G
#SBATCH --gres=gpu:1
set -euo pipefail

YAML="$1"
N_CHUNKS="$2"
: "${SEALSIM_CONDA_SETUP:?source slurm/load_paths.sh before sbatch}"
: "${SEALSIM_CONDA_ENV:?conda_env missing in local_paths.json}"
: "${SEALSIM_CODE_ROOT:?code_root missing in local_paths.json}"

# shellcheck disable=SC1090
source "$SEALSIM_CONDA_SETUP"
conda activate "$SEALSIM_CONDA_ENV"
cd "$SEALSIM_CODE_ROOT"

BACKEND="${SEALSIM_BACKEND:-auto}"
echo "$(date -Is) host=$(hostname) task=${SLURM_ARRAY_TASK_ID}/${N_CHUNKS} backend=${BACKEND}"
nvidia-smi --query-gpu=name,memory.total --format=csv,noheader 2>/dev/null || echo "no GPU visible"

sealsim sweep "$YAML" --chunk "$SLURM_ARRAY_TASK_ID" --n-chunks "$N_CHUNKS" \
    --backend "$BACKEND" --quiet
echo "$(date -Is) done"
