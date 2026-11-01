# ╔══════════════════════════════════════════════════════════════════╗
# ║  sealsim — constants                                             ║
# ║  « every number with a unit, a source and a plausible range »    ║
# ╠══════════════════════════════════════════════════════════════════╣
# ║  Physical and biological parameters of the model. Import from    ║
# ║  here; never retype a value in a function body. Ranges are for   ║
# ║  sensitivity sweeps, not hard limits. Legacy values are kept,    ║
# ║  labelled, so the thesis configuration can still be reproduced.  ║
# ╚══════════════════════════════════════════════════════════════════╝

from __future__ import annotations

from dataclasses import dataclass
from typing import TypeAlias

import numpy as np
from numpy.typing import NDArray

FloatArray: TypeAlias = NDArray[np.floating]
BoolArray: TypeAlias = NDArray[np.bool_]
IntArray: TypeAlias = NDArray[np.integer]
Vec3: TypeAlias = tuple[float, float, float]
Vec6: TypeAlias = tuple[float, float, float, float, float, float]


@dataclass(frozen=True)
class Quantity:
    """A parameter with provenance."""

    value: float
    unit: str
    source: str
    plausible_range: tuple[float, float] | None = None


# ┌────────────────────────────────────────────────────────────┐
# │ Vision  « what the seal can resolve and where it looks »   │
# └────────────────────────────────────────────────────────────┘
ACUITY_SINGLE_TARGET = Quantity(
    0.27, "deg",
    "Sandow, Miersch & Hanke (2026) J Comp Physiol A, underwater single-target acuity",
    (0.2, 0.4),
)
ACUITY_GRATING = Quantity(
    5.5 / 60, "deg",
    "Weiffen et al. (2006) Vision Res 46:1777, stripe acuity in clear water; thesis value",
    (5.5 / 60, 9.0 / 60),
)
AZIMUTH_LIMIT_DEG = Quantity(104.0, "deg", "monocular field, Oepen (2021) MSc thesis Methods")
ELEVATION_MIN_DEG = Quantity(-12.0, "deg", "lower field limit, Oepen (2021) MSc thesis Methods")
ELEVATION_MAX_DEG = Quantity(69.0, "deg", "upper field limit, Oepen (2021) MSc thesis Methods")

# ┌────────────────────────────────────────────────────────────┐
# │ Particles  « suspended sediment the seal can see »         │
# └────────────────────────────────────────────────────────────┘
PARTICLE_DIAMETER_RANGE_M: tuple[float, float] = (0.5e-3, 2.0e-3)
PARTICLE_DIAMETER_SOURCE = (
    "sand fraction of North Sea suspended matter; lab decision D1 of 2 Nov 2026"
)
LEGACY_PARTICLE_DIAMETER_RANGE_M: tuple[float, float] = (20e-6, 160e-6)
LEGACY_PARTICLE_DIAMETER_SOURCE = "Bunke et al. (2019) Front Mar Sci, SW Baltic silt; thesis value"
GRAIN_DENSITY = Quantity(2650.0, "kg m^-3", "quartz", (2400.0, 2700.0))
SPM_MASS_CONCENTRATION_G_PER_M3: dict[str, tuple[float, float]] = {
    "southern_north_sea": (1.0, 200.0),
    "skagerrak": (2.0, 22.0),
}
SPM_SOURCE = "lab data note on North Sea suspended particulate matter (Kiarra), 2026"

# ┌────────────────────────────────────────────────────────────┐
# │ Water  « currents and the water column »                   │
# └────────────────────────────────────────────────────────────┘
CURRENT_SPEEDS_M_PER_S: dict[str, Quantity] = {
    "skagerrak": Quantity(0.01, "m s^-1", "Vindenes et al. (2018), Skagerrak residual"),
    "m2_mean_max": Quantity(0.153, "m s^-1", "Davies & Furnes (1980), mean M2 tidal maximum"),
    "channel_mean": Quantity(0.6, "m s^-1", "Davies & Furnes (1980), southern North Sea"),
    "channel_peak": Quantity(1.0, "m s^-1", "Davies & Furnes (1980), channel peak"),
}
LEGACY_CURRENT_RANGE_M_PER_S: tuple[float, float] = (0.0, 3.0)
OCEAN_SURFACE_Z_M = 0.0
OCEAN_FLOOR_Z_M = Quantity(
    -70.0, "m", "MINOSplus TP6 report, harbour seal dive depths in the German Bight",
    (-100.0, -20.0),
)
DEFAULT_SEAL_DEPTH_M = -30.0

# ┌────────────────────────────────────────────────────────────┐
# │ Time  « sampling of the simulation and of the source data » │
# └────────────────────────────────────────────────────────────┘
DEFAULT_SAMPLE_RATE_HZ = 100.0
LEGACY_DIVE_SAMPLE_RATE_HZ = 20.0
VIDEO_FRAME_RATE_HZ = 25.0
DIVE_LOGGER_RATE_HZ = 0.2
MAX_STEP_FRACTION_OF_RADIUS = 0.5
MAX_STEP_ROTATION_RAD = np.pi

# ┌────────────────────────────────────────────────────────────┐
# │ Dive phases  « MINOSplus Fig. 16, digitised in data/dive_profiles » │
# └────────────────────────────────────────────────────────────┘
FLOOR_MARGIN_M = 0.5
PHASE_TRANSITION_SIGMA_S = 0.4


@dataclass(frozen=True)
class DivePhase:
    """One phase of a dive: when it ends and how the logger saw it.

    end_fraction is the cumulative end time as a fraction of dive duration.
    Pitch is positive nose-up; vertical speed is positive upward.
    """

    name: str
    end_fraction: float
    pitch_mean_deg: float
    pitch_sd_deg: float
    vertical_speed_mean_mps: float
    vertical_speed_sd_mps: float


U_SHAPE_PHASES: tuple[DivePhase, ...] = (
    DivePhase("surface", 10 / 77, 79.639515, 12.78034071, 0.0034928571, 0.0034928571),
    DivePhase("down", 14 / 77, -63.9146825, 8.36629103, -0.9988013333, 0.0532187164),
    DivePhase("straight", 65 / 77, -8.36629103, 5.5529812, 0.0024724706, 0.0293242916),
    DivePhase("up", 1.0, 68.64291923, 15.63982373, 0.2461216364, 0.4071143314),
    DivePhase("surface2", 1.0, 79.639515, 12.78034071, 0.0034928571, 0.0123944843),
)
V_SHAPE_PHASES: tuple[DivePhase, ...] = (
    DivePhase("surface", 11 / 36, 74.53024727, 7.65994214, -0.0050396364, 0.0280961935),
    DivePhase("down", 25 / 36, -17.04128714, 25.74478444, -0.235164, 0.1763858353),
    DivePhase("straight", 25 / 36, 0.0, 0.0, 0.0, 0.0),
    DivePhase("up", 1.0, 49.06783, 28.94055575, 0.301, 0.285139593),
    DivePhase("surface2", 1.0, 74.53024727, 7.65994214, -0.0050396364, 0.0280961935),
)
DIVE_SHAPES: dict[str, tuple[DivePhase, ...]] = {"u": U_SHAPE_PHASES, "v": V_SHAPE_PHASES}

# ┌────────────────────────────────────────────────────────────┐
# │ Prototypical movements  « column names shared by data and code » │
# └────────────────────────────────────────────────────────────┘
VELOCITY_COLUMNS: tuple[str, ...] = (
    "thrust", "slip", "lift", "yaw_rate", "pitch_rate", "roll_rate",
)
PM5D_FILE = "pm5d_k13.csv"
PM2D_FILE = "protoMov.csv"
PM_START_CDF_FILE = "distributionCS.csv"
PM_TRANSITION_CDF_FILE = "transProbCS.csv"

# ┌────────────────────────────────────────────────────────────┐
# │ Palette  « Wong (2011) colourblind-safe colours »          │
# └────────────────────────────────────────────────────────────┘
WONG: dict[str, str] = {
    "black": "#000000",
    "orange": "#E69F00",
    "sky_blue": "#56B4E9",
    "bluish_green": "#009E73",
    "yellow": "#F0E442",
    "blue": "#0072B2",
    "vermilion": "#D55E00",
    "reddish_purple": "#CC79A7",
}
