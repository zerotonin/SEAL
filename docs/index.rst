sealsim
=======

SEnsory Aquatic odometry simuLator: a particle cloud around a six-degree-of-freedom
harbour seal agent, and the optic flow those particles paint on the seal's retina.

The package is the 2026 rewrite of the research code behind Oepen et al.
(in preparation) and the 2021 MSc thesis of A. S. Oepen. The frozen original lives
in ``_legacy/`` and is pinned by a regression test.

.. toctree::
   :maxdepth: 2

   methods
   provenance
   api

Configuration
-------------

Copy ``local_paths.template.json`` to ``local_paths.json`` next to the repo root and
fill in ``data_root`` (and the SLURM keys for the ``hpc`` profile). Every entry point
refuses to run without it; ``sealsim config`` shows what is resolved. The input tables
(prototypical movements, dive profiles) ship inside the package and need no setup.
