# ╔══════════════════════════════════════════════════════════════════╗
# ║  sealsim — tests.fixtures.make_legacy_fixture                    ║
# ║  « pin the 2022 single-step behaviour »                          ║
# ╠══════════════════════════════════════════════════════════════════╣
# ║  Runs the frozen legacy code once with a fixed seed and stores   ║
# ║  particle positions and flow magnitudes. Regenerate only on purpose: ║
# ║                                                                  ║
# ║      python tests/fixtures/make_legacy_fixture.py                ║
# ╚══════════════════════════════════════════════════════════════════╝

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
LEGACY_DIR = HERE.parents[1] / "_legacy"
OUT = HERE / "legacy_step_R0p1_seed0.npz"

SEED = 0
CLOUD_RADIUS_M = 0.1          # legacy hollow-core rule is sane at this radius
N_PARTICLES = 200
SPS = 100
STEP = np.array([3.0, 0.0, 0.0, 0.0, 0.0, 0.0])      # 3 m/s thrust
POSITION = np.array([0.0, 0.0, -30.0])
ORIENTATION = np.zeros(3)


def run_legacy_step() -> dict[str, np.ndarray]:
    sys.path.insert(0, str(LEGACY_DIR))
    import SEAL_SIM  # noqa: E402

    np.random.seed(SEED)
    sim = SEAL_SIM.SEAL_SIM("headless", spsInt=SPS, maxParticlesInt=N_PARTICLES,
                            durSecFloat=2 / SPS, currentStaticVelTuple=(0.0, 0.0, 0.0),
                            diveTypeStr="uShape", cloudRadiusFloat=CLOUD_RADIUS_M)
    sim.runSimulationSingleStep(STEP, POSITION.copy(), ORIENTATION.copy())
    particles = sim.pCloud.partclObjList
    start = np.array([p.trajectory[0][0] for p in particles])
    end = np.array([p.trajectory[0][1] for p in particles])
    visible = np.array([p.trajectory[0][2] for p in particles], dtype=bool)
    flow_mag = np.array(sim.opticFlowAna.anaDataList[0][1], dtype=float)
    return dict(start=start, end=end, visible=visible, flow_mag=flow_mag,
                seal_end=np.asarray(sim.seal.sealPosition), step=STEP,
                position=POSITION, cloud_radius=np.array(CLOUD_RADIUS_M), seed=np.array(SEED))


if __name__ == "__main__":
    np.savez_compressed(OUT, **run_legacy_step())
    print("wrote", OUT)
