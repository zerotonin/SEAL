# ╔══════════════════════════════════════════════════════════════════╗
# ║  sealsim — tests.test_environment_agent                          ║
# ║  « water column masks, currents and the seal's step »            ║
# ╠══════════════════════════════════════════════════════════════════╣
# ║  The agent and the cloud must share one frame: a yawed seal      ║
# ║  moves sideways in the world and the particles stream past       ║
# ║  accordingly.                                                    ║
# ╚══════════════════════════════════════════════════════════════════╝

from __future__ import annotations

import numpy as np

from sealsim import agent
from sealsim.environment import CornerCurrent, Environment, UniformCurrent


def test_in_water_excludes_surface_and_floor():
    env = Environment(floor_z=-70.0)
    z = np.array([0.5, 0.0, -0.1, -69.9, -70.0, -80.0])
    np.testing.assert_array_equal(env.in_water(z), [False, False, True, True, False, False])


def test_uniform_current_broadcasts():
    current = UniformCurrent((0.1, 0.0, 0.0))
    out = current(np.zeros((5, 3)))
    assert out.shape == (5, 3)
    np.testing.assert_allclose(out[:, 0], 0.1)
    assert current.speed == 0.1


def test_corner_current_interpolates_linearly():
    corners = np.zeros((2, 2, 2, 3))
    corners[1, :, :, 0] = 1.0
    current = CornerCurrent(corners, xy_limits=(-10.0, 10.0), z_limits=(-70.0, 0.0))
    out = current(np.array([[-10.0, 0.0, -5.0], [0.0, 0.0, -5.0], [10.0, 0.0, -5.0]]))
    np.testing.assert_allclose(out[:, 0], [0.0, 0.5, 1.0])


def test_forward_step_of_a_right_yawed_seal_goes_to_minus_y():
    state = agent.SealState.at(euler=(np.pi / 2, 0.0, 0.0))
    after = agent.advance(state, [1.0, 0, 0, 0, 0, 0], 0.5)
    np.testing.assert_allclose(after.position - state.position, [0.0, -0.5, 0.0], atol=1e-12)
    np.testing.assert_allclose(after.euler, state.euler)


def test_yaw_rate_accumulates():
    state = agent.SealState.at()
    after = agent.advance(state, [0, 0, 0, 0.2, 0, 0], 0.5)
    np.testing.assert_allclose(after.euler, [0.1, 0.0, 0.0], atol=1e-12)


def test_translation_and_rotation_parts_split_the_velocity():
    v = np.arange(6, dtype=float)
    np.testing.assert_array_equal(agent.translation_part(v), [0, 1, 2, 0, 0, 0])
    np.testing.assert_array_equal(agent.rotation_part(v), [0, 0, 0, 3, 4, 5])
