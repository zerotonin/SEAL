# ╔══════════════════════════════════════════════════════════════════╗
# ║  sealsim — tests.test_simulate_current                           ║
# ║  « a current counts as translation, never as rotation »          ║
# ╠══════════════════════════════════════════════════════════════════╣
# ║  The rotation-only run of the decomposition sees still water,    ║
# ║  so a head current cannot lower the translation-rotation index.  ║
# ╚══════════════════════════════════════════════════════════════════╝

from __future__ import annotations

import numpy as np

from sealsim.cloud import CloudSpec
from sealsim.environment import Environment, UniformCurrent
from sealsim.simulate import StepConfig, run_step, still_water


def _cfg(current, velocity):
    return StepConfig(velocity=velocity, cloud=CloudSpec(n_particles=3000), seed=5,
                      environment=Environment(current=UniformCurrent(current)))


def test_still_water_drops_the_current_only():
    env = Environment(floor_z=-50.0, current=UniformCurrent((1.0, 0.0, 0.0)))
    still = still_water(env)
    assert still.floor_z == -50.0
    assert still.current.speed == 0.0


def test_pure_rotation_in_a_current_has_translational_flow():
    rotating = (0.0, 0.0, 0.0, 2.0, 0.0, 0.0)
    res = run_step(_cfg((0.0, 0.1, 0.0), rotating))  # 0.1 m/s: no grain crosses the ball
    still = run_step(_cfg((0.0, 0.0, 0.0), rotating))
    trans = res.components["translation"].magnitude[res.components["translation"].in_fov]
    assert float(trans.sum()) > 0.0
    rot = res.components["rotation"].magnitude
    rot_still = still.components["rotation"].magnitude
    np.testing.assert_allclose(rot[np.isfinite(rot)], rot_still[np.isfinite(rot_still)],
                               rtol=1e-12)


def test_head_current_does_not_lower_the_index():
    fast = (3.7, 0.0, 0.0, 0.05, 0.0, 0.0)
    calm = run_step(_cfg((0.0, 0.0, 0.0), fast)).metrics.trans_rot_index
    head = run_step(_cfg((-1.0, 0.0, 0.0), fast)).metrics.trans_rot_index
    assert head >= calm - 1e-3
