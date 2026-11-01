# Legacy SEAL code (2019 to 2022)

These are the original flat scripts, moved here unchanged on 2 November 2026 so that the
rewrite in `src/sealsim/` can be compared against them. Do not edit them; fix things in
the package instead.

| What | Files |
|---|---|
| Simulation classes | `SEAL_SIM.py`, `seal_agent.py`, `turbidity.py`, `environment.py`, `protoMov.py`, `runTimeData.py`, `opticFlowAna.py`, `utilities.py` |
| Run scripts | `RunAndSaveSealSimulation.py`, `RunSims4LappeLab.py`, `runStepSim.py`, `runTrajectories4Clustering.py`, `calculateRoationalConentofOF.py`, `OFcontentAna.py`, `plotOFFigure.py`, `PM_plotting.py`, `trigonometricLimits4SEAL.py`, `calculateZ.py` |
| REPL transcripts (not pytest) | `test*.py` |
| Outputs kept for reference | `outputs/OF_content.csv`, `outputs/TranslationalMovement*.csv` |
| Original environment and README | `seal.yaml`, `README_original.md` |

## Known state

- Single-step mode (`SEAL_SIM.runSimulationSingleStep`) runs on Python 3.11 after
  `pip install ai.cs`. It is pinned by `tests/test_legacy_regression.py` at cloud radius 0.1 m.
- Full-dive mode (`SEAL_SIM.runSimulation`) raises `AttributeError: relPartPosCart` since
  commit d476091 (June 2021).
- `protoMov.createThrustSlipYaw` reads `protoMov.csv` and friends from the working directory;
  those files now live in `data/prototypical_movements/`.
- The audit of this code (unit error in the visibility radius, hollow-core sampling, flow
  vector construction, rank metric, frame mixing) is documented in the lab-internal dev plan
  and reproduced by the new test suite as the rewrite proceeds.

Tags: `v0.1-thesis` marks the thesis-date state (22 January 2021), `v0.2-legacy` the last
flat-layout commit (14 September 2022).
