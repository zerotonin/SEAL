sealsim
=======

SEnsory Aquatic odometry simuLator: a particle cloud around a six-degree-of-freedom
harbour seal agent, and the optic flow those particles paint on the seal's retina.

The package is being rebuilt from the 2019 to 2022 research code behind
Oepen et al. (in preparation). The frozen original lives in ``_legacy/`` and is
covered by a regression test; the new modules arrive sprint by sprint.

.. toctree::
   :maxdepth: 2

   api

Configuration
-------------

Copy ``local_paths.template.json`` to ``local_paths.json`` next to the repo root and
fill in ``data_root`` (and the SLURM keys for the ``hpc`` profile). Every entry point
refuses to run without it; ``sealsim config`` shows what is resolved.
