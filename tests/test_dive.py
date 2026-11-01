# ╔══════════════════════════════════════════════════════════════════╗
# ║  sealsim — tests.test_dive                                       ║
# ║  « dives stay in the water and the phases come in order »        ║
# ╠══════════════════════════════════════════════════════════════════╣
# ║  The legacy state machine indexed phases of a deleted version    ║
# ║  and the FFT resampler assumed a periodic depth profile.         ║
# ╚══════════════════════════════════════════════════════════════════╝

from __future__ import annotations

import numpy as np
import pytest

from sealsim import dive
from sealsim.constants import U_SHAPE_PHASES, V_SHAPE_PHASES
from sealsim.geometry import body_to_world


@pytest.fixture(scope="module")
def tables():
    return dive.load_pm_tables()


def test_pm_tables_shapes_and_units(tables):
    assert tables.movements.shape == (50, 3)
    assert tables.start_cdf.shape == (50,)
    assert tables.transition_cdf.shape == (50, 50)
    assert np.abs(tables.movements[:, 2]).max() < 2 * np.pi * 2
    np.testing.assert_allclose(tables.transition_cdf[:, -1], 1.0)


def test_pm_sequence_is_reproducible_and_in_range(tables):
    a = dive.sample_pm_sequence(tables, 500, np.random.default_rng(7))
    b = dive.sample_pm_sequence(tables, 500, np.random.default_rng(7))
    np.testing.assert_array_equal(a, b)
    assert a.min() >= 0 and a.max() < 50


@pytest.mark.parametrize("phases", [U_SHAPE_PHASES, V_SHAPE_PHASES])
def test_depth_profile_stays_in_the_water_column(phases):
    depth, pitch, phase = dive.generate_depth_pitch(phases, 240.0, 50.0,
                                                    np.random.default_rng(0))
    assert depth.max() < 0.0 and depth.min() > -70.0
    assert np.all(np.diff(phase) >= 0)
    assert pitch.shape == depth.shape == phase.shape


def test_u_dive_descends_during_the_down_phase():
    depth, _, phase = dive.generate_depth_pitch(U_SHAPE_PHASES, 240.0, 50.0,
                                                np.random.default_rng(1))
    down = phase == 1
    assert depth[down].min() < -8.0
    assert np.mean(np.diff(depth[down]) < 0) > 0.9


def test_generated_dive_is_self_consistent(tables):
    traj = dive.generate_dive("u", 60.0, 50.0, np.random.default_rng(2), tables)
    assert traj.position.shape == (3001, 3)
    assert traj.velocity_body.shape == (3000, 6)
    step = body_to_world(traj.euler[:-1]).apply(traj.velocity_body[:, :3]) / traj.sample_rate
    np.testing.assert_allclose(traj.position[1:], traj.position[:-1] + step, atol=1e-9)
    frame = traj.to_frame()
    assert len(frame) == 3001 and "thrust" in frame.columns


def test_unknown_shape_raises(tables):
    with pytest.raises(ValueError):
        dive.generate_dive("w", 10.0, 10.0, np.random.default_rng(0), tables)


def test_pm5d_table_has_thirteen_movements():
    table = dive.load_pm5d()
    assert len(table) == 13
    v = dive.pm5d_velocity(table, 10)
    assert v[3] == pytest.approx(2.1617)
    with pytest.raises(KeyError):
        dive.pm5d_velocity(table, 99)


def test_package_ships_the_input_tables():
    from sealsim.dive import PACKAGE_DATA_DIR, default_data_dir

    assert default_data_dir() == PACKAGE_DATA_DIR
    names = {p.name for p in PACKAGE_DATA_DIR.rglob("*.csv")}
    assert names == {"protoMov.csv", "distributionCS.csv", "transProbCS.csv", "pm5d_k13.csv",
                     "uShapeDiveDepthPitch.csv", "vShapeDiveDepthPitch.csv"}
    assert (PACKAGE_DATA_DIR / "PROVENANCE.md").is_file()
