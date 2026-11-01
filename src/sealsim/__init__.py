# ╔══════════════════════════════════════════════════════════════════╗
# ║  sealsim — package                                               ║
# ║  « optic flow in turbid water for a swimming seal »              ║
# ╠══════════════════════════════════════════════════════════════════╣
# ║  SEnsory Aquatic odometry simuLator.                             ║
# ║  Particle cloud + 6-DoF seal agent + optic flow on the retina.   ║
# ║                                                                  ║
# ║  Public API grows per sprint; see the dev plan for the layout.   ║
# ╚══════════════════════════════════════════════════════════════════╝

from __future__ import annotations

from importlib.metadata import PackageNotFoundError, version

try:
    __version__ = version("sealsim")
except PackageNotFoundError:  # editable checkout without metadata
    __version__ = "0.0.0"

from sealsim.cloud import CloudSpec  # noqa: E402
from sealsim.environment import Environment, UniformCurrent  # noqa: E402
from sealsim.simulate import StepConfig, StepResult, run_step  # noqa: E402

__all__ = [
    "CloudSpec", "Environment", "StepConfig", "StepResult", "UniformCurrent",
    "__version__", "run_step",
]
