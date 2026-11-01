# Vision presets used by the experiment files

| key | acuity | grain diameters | cloud radius | source |
|---|---|---|---|---|
| north_sea | 0.27 deg | 0.5 to 2 mm | 0.42 m | Sandow, Miersch & Hanke (2026); lab decision D1 |
| thesis | 5.5 arcmin | 20 to 160 um | 0.10 m | Weiffen et al. (2006); Bunke et al. (2019); thesis configuration with the deg/rad slip removed |

Every YAML repeats both presets under `vision:` so a file is self-contained.
Grid keys recognised by `sealsim.sweep.build_step_config`: `pm_id` or `velocity` or
(`thrust_mps`, `yaw_rate_degps`, `pitch_rate_degps`); `vision`; `number_density_per_m3`
or `n_particles`; `current_speed_mps` + `current_direction` (head, follow, cross, up, down)
or `current`; `depth_m`; `euler`; `dt`; `replicate` (only changes the seed); `floor_z`.
Seed = `base_seed` + job index, so every job is reproducible from the YAML alone.
