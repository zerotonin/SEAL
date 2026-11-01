# ╔══════════════════════════════════════════════════════════════════╗
# ║  sealsim — docs.conf                                             ║
# ║  « Sphinx configuration: Napoleon, autodoc, Furo »               ║
# ╚══════════════════════════════════════════════════════════════════╝

from __future__ import annotations

from importlib import metadata

project = "sealsim"
author = "Anne S. Oepen, Bart R. H. Geurten"
copyright = "2019-2026, Anne S. Oepen and Bart R. H. Geurten"
try:
    release = metadata.version("sealsim")
except metadata.PackageNotFoundError:
    release = "0.0.0"
version = release

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",
    "sphinx.ext.viewcode",
    "sphinx.ext.mathjax",
]
autodoc_mock_imports = ["cupy"]
napoleon_google_docstring = True
napoleon_numpy_docstring = False

templates_path = ["_templates"]
exclude_patterns = ["_build"]

html_theme = "furo"
html_title = "sealsim"
