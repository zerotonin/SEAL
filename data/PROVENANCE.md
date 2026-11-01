# Data provenance

Every file under `data/` with where it came from, who produced it, and what the package
uses it for. Simulation outputs never live here; they go to `data_root` from
`local_paths.json`.

## prototypical_movements/

| File | Shape | Content | Origin |
|---|---|---|---|
| `protoMov.csv` | 50 × 3 | k-means centroids: thrust (m/s), slip (m/s), yaw (°/s) | Surface-swimming videos of four harbour seals (Luca, Nick, Moe, Henry) at the Marine Science Center Rostock, provided by Frederike D. Hanke; 96 videos at 25 fps, stabilised with vidstab, tracked with DeepLabCut (snout, back of head, body centre); velocities and k-means (k = 50, z-scored, Euclidean) in MATLAB by Bart R. H. Geurten, 2020. Thesis §3.2.1 and Appendix A.1 |
| `distributionCS.csv` | 50 | cumulative start distribution of the 50 PMs | same run |
| `transProbCS.csv` | 50 × 50 | cumulative transition matrix (row = current PM) | same run |
| `pm5d_k13.csv` | 13 × 7 | the five-dimensional PMs used in every thesis and manuscript figure: thrust, slip, lift (m/s), yaw, pitch (rad/s), roll fixed at 0, plus a group label | z-scored k-means on 200 simulated dives (100 U, 100 V) at 1000 Hz; the original file `combi_C.csv` is not in the repo, so this table was reconstructed on 2 Nov 2026 from the vectors hard-coded in `_legacy/RunSims4LappeLab.py`, `_legacy/plotOFFigure.py` and `_legacy/calculateRoationalConentofOF.py` (identical in all three). Thesis Figs 5.1 to 5.3. Ask A. S. Oepen for the original |
| `exampleC.csv` | 9 × 5 | centroids from an earlier k = 9 run | thesis p. 41 mentions k = 9; not used by any figure; kept for completeness |

## dive_profiles/

| File | Content | Origin |
|---|---|---|
| `uShapeDiveDepthPitch.csv` | time of day, depth (m), pitch (°) at 0.2 Hz, one U-shaped dive (77 samples) | digitised from Fig. 16 of the MINOSplus TP6 report "Seehunde in See" (G. Müller, N. S. Liebsch; Nationalpark Wattenmeer); logger data of a free-ranging North Sea harbour seal |
| `vShapeDiveDepthPitch.csv` | same for one V-shaped dive (36 samples) | same |

The per-phase means and standard deviations hard-coded in `_legacy/protoMov.py`
(`diveShapeU`, `diveShapeV`) were derived from these two files; the rewrite recomputes
them from the CSVs.

## Literature constants (live in `src/sealsim/constants.py` from Sprint 1)

| Quantity | Value | Source |
|---|---|---|
| Visual acuity, single target, underwater | 0.27° | Sandow, Miersch, Hanke (2026) J Comp Physiol A, doi 10.1007/s00359-026-01837-x |
| Visual acuity, stripes (sensitivity case) | 5.5 arcmin | Weiffen, Möller, Mauck, Dehnhardt (2006) Vision Res 46:1777 |
| Field of view | −104° to +104° azimuth, −12° to +69° elevation | Hanke, Römer, Dehnhardt (2006) Vision Res 46:2804 |
| Particle diameters (main case) | 0.5 to 2 mm | lab decision D1, 2 Nov 2026; North Sea SPM size reference still to be added |
| Particle diameters (thesis case) | 20 to 160 µm | Bunke et al. (2019) Front Mar Sci (SW Baltic) |
| Suspended matter | 1 to 200 g/m³ southern North Sea; 2 to 22 g/m³ Skagerrak/Kattegat | Dogliotti et al. (2015) Remote Sens Environ 156:157; Lund-Hansen & Christiansen (2008) Geogr Tidsskr 108:37 |
| Tidal currents | M2 mean maximum 0.153 m/s; channel average 0.6 m/s; peaks > 1 m/s; Skagerrak 0.01 m/s | Vindenes et al. (2018) Cont Shelf Res 162:1; Davies & Furnes (1980) J Phys Oceanogr 10:237 |
| Water column | 70 m | Placke et al. (2018) Front Mar Sci 5:287 (kept from the thesis) |
| Saccade duration | 1.0 ± 0.3 s | Geurten, Niesterok, Dehnhardt, Hanke (2017) J Exp Biol 220:1503 |
