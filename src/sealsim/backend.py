# ╔══════════════════════════════════════════════════════════════════╗
# ║  sealsim — backend                                               ║
# ║  « numpy or cupy behind one name »                               ║
# ╠══════════════════════════════════════════════════════════════════╣
# ║  Array code in cloud, geometry, opticflow and simulate asks      ║
# ║  array_module_of(x) which library owns its inputs and uses that  ║
# ║  for everything else, so the same functions run on CPU arrays    ║
# ║  and on CUDA arrays. The cloud is sampled with a numpy           ║
# ║  generator and moved to the device afterwards, which keeps a     ║
# ║  seed meaning the same particles on both backends. Small         ║
# ║  3-vectors and the scipy Rotation stay on the CPU.               ║
# ╚══════════════════════════════════════════════════════════════════╝

from __future__ import annotations

import os
from functools import lru_cache
from types import ModuleType
from typing import Any

import numpy as np

ENV_BACKEND = "SEALSIM_BACKEND"
BACKENDS = ("numpy", "cupy", "auto")


class BackendError(RuntimeError):
    """Requested array backend is not usable on this machine."""


@lru_cache(maxsize=1)
def _cupy() -> ModuleType | None:
    try:
        import cupy
    except ImportError:
        return None
    return cupy


def cupy_available() -> bool:
    """cupy imports and at least one CUDA device answers."""
    cp = _cupy()
    if cp is None:
        return False
    try:
        return int(cp.cuda.runtime.getDeviceCount()) > 0
    except Exception:  # noqa: BLE001  (driver missing, no device, wrong CUDA)
        return False


def default_backend() -> str:
    return os.environ.get(ENV_BACKEND, "numpy")


def get_array_module(name: str | None = None) -> ModuleType:
    """Resolve 'numpy', 'cupy' or 'auto' (cupy if a device answers, else numpy)."""
    name = name or default_backend()
    if name not in BACKENDS:
        raise BackendError(f"backend must be one of {BACKENDS}, got {name!r}")
    if name == "numpy":
        return np
    if name == "auto":
        return _cupy() if cupy_available() else np
    if not cupy_available():
        raise BackendError(
            "backend 'cupy' requested but cupy is missing or sees no CUDA device; "
            "install with pip install -e '.[gpu]' on a machine with an NVIDIA driver"
        )
    return _cupy()


def array_module_of(*arrays: Any) -> ModuleType:
    """cupy if any argument is a cupy array, numpy otherwise."""
    cp = _cupy()
    if cp is not None and any(isinstance(a, cp.ndarray) for a in arrays):
        return cp
    return np


def to_numpy(array: Any) -> np.ndarray:
    cp = _cupy()
    if cp is not None and isinstance(array, cp.ndarray):
        return array.get()
    return np.asarray(array)


def to_backend(array: Any, xp: ModuleType) -> Any:
    """Move an array to the given module; a no-op when it is already there."""
    if xp is np:
        return to_numpy(array)
    return xp.asarray(to_numpy(array) if not isinstance(array, xp.ndarray) else array)


def backend_name(xp: ModuleType) -> str:
    return "numpy" if xp is np else "cupy"
