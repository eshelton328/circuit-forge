# Spice simulation report

Each **scenario** matches a block in `sim.yml`. **Bounds** repeat those limits; **Baseline** and **Δ** appear only when `sim/spice_metrics_baseline.json` is loaded.

## Run metadata

| Field | Value |
| --- | --- |
| Config | `/Users/erik/Workspaces/the-forge-alec/boards/alec-main/sim.yml` |
| Netlist | `/Users/erik/Workspaces/the-forge-alec/boards/alec-main/sim/assembled.cir` |
| KiCad CLI | `10.0.1` |
| KiCad Docker image (CI) | `—` |
| ngspice | `******` |
| Simulator exit | 0 |

## Executive summary

| Metric | Value |
| --- | --- |
| Measures | 105 |
| Passed | 105 |
| Failed | 0 |

## Results by scenario

### `vbat_bias_op`

| Measure | Value | Bounds | Result |
| --- | --- | --- | --- |
| Protected battery rail DC bias (4.8 V pack at t=0) | 4.79997 | min 4.5, max 4.85 | **PASS** |

### `tran_fresh_4v8`

| Measure | Value | Bounds | Result |
| --- | --- | --- | --- |
| Vout steady, fresh pack (95 µs) | 3.30704 | min 3.28, max 3.33 | **PASS** |
| Vout ripple peak-peak, fresh pack idle | 4.44089e-16 | max 0.15 | **PASS** |
| Vout minimum during 0.5 A burst at 4.8 V | 3.30704 | min 3.1 | **PASS** |

### `tran_mid_3v6`

| Measure | Value | Bounds | Result |
| --- | --- | --- | --- |
| Vout steady at 3.6 V (buck-boost transition) | 3.30704 | min 3.28, max 3.33 | **PASS** |
| Vout minimum during 0.5 A burst at 3.6 V | 3.30704 | min 3.1 | **PASS** |

### `tran_low_3v0`

| Measure | Value | Bounds | Result |
| --- | --- | --- | --- |
| Vout steady on end-of-life pack (3.0 V) | 3.30704 | min 3.28, max 3.33 | **PASS** |
| Vout minimum during 0.5 A burst at 3.0 V (boost mode) | 3.30704 | min 3.0 | **PASS** |
| Protected battery rail present during worst burst (wiring check) | 3.00835 | min 2.5 | **PASS** |
| Battery-side passive drain at idle, post-settling (pull-ups + FB dividers; repository model is quasi-ideal and does not draw converter input current) | 2.21153e-05 | max 0.002 | **PASS** |

### `tran_recovery`

| Measure | Value | Bounds | Result |
| --- | --- | --- | --- |
| Vout recovered at idle on dead pack (800 µs) | 3.30704 | min 3.28, max 3.33 | **PASS** |

### `schematic_dual_rail`

| Measure | Value | Bounds | Result |
| --- | --- | --- | --- |
| Schematic U2 remains disabled before GPIO18 assertion | 0 | max 0.05 | **PASS** |
| Schematic U2 regulates with 0.6 A modeled audio load | 4.98516 | min 4.95, max 5.02 | **PASS** |
| Schematic U1 regulates while both modeled rails are loaded | 3.30704 | min 3.28, max 3.33 | **PASS** |

### `tran_startup_3v0`

| Measure | Value | Bounds | Result |
| --- | --- | --- | --- |
| Cold start at 3.0 V — Vout at 380 µs | 3.30704 | min 3.28, max 3.33 | **PASS** |
| Cold start at 3.0 V — Vout floor after settling | 3.30704 | min 3.2 | **PASS** |

### `espnow_fresh`

| Measure | Value | Bounds | Result |
| --- | --- | --- | --- |
| ESP-NOW bursts, fresh pack — VIN minimum (behavioral converter) | 4.27593 | min 4.1 | **PASS** |
| ESP-NOW bursts, fresh pack — 3V3 minimum | 3.2905 | min 3.25 | **PASS** |

### `espnow_tired`

| Measure | Value | Bounds | Result |
| --- | --- | --- | --- |
| ESP-NOW bursts, tired pack (3.6V/1.2R) — VIN sag stays above 2.0V UVLO | 2.62766 | min 2.3, max 3.0 | **PASS** |
| ESP-NOW bursts, tired pack — 3V3 holds | 3.2905 | min 3.25 | **PASS** |

### `espnow_dead`

| Measure | Value | Bounds | Result |
| --- | --- | --- | --- |
| ESP-NOW burst, dead pack (3.0V/3R) — brownout MUST occur (failure-boundary regression) | 1.59998 | max 2.5 | **PASS** |
| Dead-pack brownout — rail recovers after burst | 3.3052 | min 3.25, max 3.35 | **PASS** |

### `rev2_amp_preview`

| Measure | Value | Bounds | Result |
| --- | --- | --- | --- |
| Rev-2 preview: WiFi + 3W amp on fresh pack — VIN minimum | 3.83804 | min 3.5 | **PASS** |
| Rev-2 preview — 3V3 holds under combined load | 3.2905 | min 3.25 | **PASS** |
| Rev-2 preview — 5V amp rail holds | 4.982 | min 4.9 | **PASS** |

### `remote_button_rlc_01`

| Measure | Value | Bounds | Result |
| --- | --- | --- | --- |
| Unclamped GPIO minimum, assumed harness corner | 0.0311035 | min -0.1 | **PASS** |
| Unclamped GPIO maximum | 3.3 | max 3.4 | **PASS** |
| Peak current through remote switch | 0.0346602 | max 0.05 | **PASS** |
| Held LOW level | 0.0311035 | max 0.825 | **PASS** |
| Released HIGH after 1.9 ms | 2.99594 | min 2.475 | **PASS** |

### `remote_button_rlc_02`

| Measure | Value | Bounds | Result |
| --- | --- | --- | --- |
| Unclamped GPIO minimum, assumed harness corner | 0.031395 | min -0.1 | **PASS** |
| Unclamped GPIO maximum | 3.3 | max 3.4 | **PASS** |
| Peak current through remote switch | 0.0343355 | max 0.05 | **PASS** |
| Held LOW level | 0.031395 | max 0.825 | **PASS** |
| Released HIGH after 1.9 ms | 2.99597 | min 2.475 | **PASS** |

### `remote_button_rlc_03`

| Measure | Value | Bounds | Result |
| --- | --- | --- | --- |
| Unclamped GPIO minimum, assumed harness corner | 0.0311035 | min -0.1 | **PASS** |
| Unclamped GPIO maximum | 3.3 | max 3.4 | **PASS** |
| Peak current through remote switch | 0.0346691 | max 0.05 | **PASS** |
| Held LOW level | 0.0311035 | max 0.825 | **PASS** |
| Released HIGH after 1.9 ms | 2.62893 | min 2.475 | **PASS** |

### `remote_button_rlc_04`

| Measure | Value | Bounds | Result |
| --- | --- | --- | --- |
| Unclamped GPIO minimum, assumed harness corner | 0.031395 | min -0.1 | **PASS** |
| Unclamped GPIO maximum | 3.3 | max 3.4 | **PASS** |
| Peak current through remote switch | 0.0343443 | max 0.05 | **PASS** |
| Held LOW level | 0.031395 | max 0.825 | **PASS** |
| Released HIGH after 1.9 ms | 2.62899 | min 2.475 | **PASS** |

### `remote_button_rlc_05`

| Measure | Value | Bounds | Result |
| --- | --- | --- | --- |
| Unclamped GPIO minimum, assumed harness corner | 0.0311035 | min -0.1 | **PASS** |
| Unclamped GPIO maximum | 3.3 | max 3.4 | **PASS** |
| Peak current through remote switch | 0.0344729 | max 0.05 | **PASS** |
| Held LOW level | 0.0311035 | max 0.825 | **PASS** |
| Released HIGH after 1.9 ms | 2.99594 | min 2.475 | **PASS** |

### `remote_button_rlc_06`

| Measure | Value | Bounds | Result |
| --- | --- | --- | --- |
| Unclamped GPIO minimum, assumed harness corner | 0.031395 | min -0.1 | **PASS** |
| Unclamped GPIO maximum | 3.3 | max 3.4 | **PASS** |
| Peak current through remote switch | 0.0341535 | max 0.05 | **PASS** |
| Held LOW level | 0.031395 | max 0.825 | **PASS** |
| Released HIGH after 1.9 ms | 2.99597 | min 2.475 | **PASS** |

### `remote_button_rlc_07`

| Measure | Value | Bounds | Result |
| --- | --- | --- | --- |
| Unclamped GPIO minimum, assumed harness corner | 0.0311035 | min -0.1 | **PASS** |
| Unclamped GPIO maximum | 3.3 | max 3.4 | **PASS** |
| Peak current through remote switch | 0.0345302 | max 0.05 | **PASS** |
| Held LOW level | 0.0311035 | max 0.825 | **PASS** |
| Released HIGH after 1.9 ms | 2.62893 | min 2.475 | **PASS** |

### `remote_button_rlc_08`

| Measure | Value | Bounds | Result |
| --- | --- | --- | --- |
| Unclamped GPIO minimum, assumed harness corner | 0.031395 | min -0.1 | **PASS** |
| Unclamped GPIO maximum | 3.3 | max 3.4 | **PASS** |
| Peak current through remote switch | 0.0342097 | max 0.05 | **PASS** |
| Held LOW level | 0.031395 | max 0.825 | **PASS** |
| Released HIGH after 1.9 ms | 2.62899 | min 2.475 | **PASS** |

### `remote_button_rlc_09`

| Measure | Value | Bounds | Result |
| --- | --- | --- | --- |
| Unclamped GPIO minimum, assumed harness corner | 0.0343384 | min -0.1 | **PASS** |
| Unclamped GPIO maximum | 3.3 | max 3.4 | **PASS** |
| Peak current through remote switch | 0.0313647 | max 0.05 | **PASS** |
| Held LOW level | 0.0343384 | max 0.825 | **PASS** |
| Released HIGH after 1.9 ms | 2.99625 | min 2.475 | **PASS** |

### `remote_button_rlc_10`

| Measure | Value | Bounds | Result |
| --- | --- | --- | --- |
| Unclamped GPIO minimum, assumed harness corner | 0.0346293 | min -0.1 | **PASS** |
| Unclamped GPIO maximum | 3.3 | max 3.4 | **PASS** |
| Peak current through remote switch | 0.0310985 | max 0.05 | **PASS** |
| Held LOW level | 0.0346293 | max 0.825 | **PASS** |
| Released HIGH after 1.9 ms | 2.99627 | min 2.475 | **PASS** |

### `remote_button_rlc_11`

| Measure | Value | Bounds | Result |
| --- | --- | --- | --- |
| Unclamped GPIO minimum, assumed harness corner | 0.0343384 | min -0.1 | **PASS** |
| Unclamped GPIO maximum | 3.3 | max 3.4 | **PASS** |
| Peak current through remote switch | 0.0313719 | max 0.05 | **PASS** |
| Held LOW level | 0.0343384 | max 0.825 | **PASS** |
| Released HIGH after 1.9 ms | 2.62959 | min 2.475 | **PASS** |

### `remote_button_rlc_12`

| Measure | Value | Bounds | Result |
| --- | --- | --- | --- |
| Unclamped GPIO minimum, assumed harness corner | 0.0346293 | min -0.1 | **PASS** |
| Unclamped GPIO maximum | 3.3 | max 3.4 | **PASS** |
| Peak current through remote switch | 0.0311057 | max 0.05 | **PASS** |
| Held LOW level | 0.0346293 | max 0.825 | **PASS** |
| Released HIGH after 1.9 ms | 2.62965 | min 2.475 | **PASS** |

### `remote_button_rlc_13`

| Measure | Value | Bounds | Result |
| --- | --- | --- | --- |
| Unclamped GPIO minimum, assumed harness corner | 0.0343384 | min -0.1 | **PASS** |
| Unclamped GPIO maximum | 3.3 | max 3.4 | **PASS** |
| Peak current through remote switch | 0.0312264 | max 0.05 | **PASS** |
| Held LOW level | 0.0343384 | max 0.825 | **PASS** |
| Released HIGH after 1.9 ms | 2.99625 | min 2.475 | **PASS** |

### `remote_button_rlc_14`

| Measure | Value | Bounds | Result |
| --- | --- | --- | --- |
| Unclamped GPIO minimum, assumed harness corner | 0.0346293 | min -0.1 | **PASS** |
| Unclamped GPIO maximum | 3.3 | max 3.4 | **PASS** |
| Peak current through remote switch | 0.0309638 | max 0.05 | **PASS** |
| Held LOW level | 0.0346293 | max 0.825 | **PASS** |
| Released HIGH after 1.9 ms | 2.99627 | min 2.475 | **PASS** |

### `remote_button_rlc_15`

| Measure | Value | Bounds | Result |
| --- | --- | --- | --- |
| Unclamped GPIO minimum, assumed harness corner | 0.0343384 | min -0.1 | **PASS** |
| Unclamped GPIO maximum | 3.3 | max 3.4 | **PASS** |
| Peak current through remote switch | 0.0312724 | max 0.05 | **PASS** |
| Held LOW level | 0.0343384 | max 0.825 | **PASS** |
| Released HIGH after 1.9 ms | 2.62959 | min 2.475 | **PASS** |

### `remote_button_rlc_16`

| Measure | Value | Bounds | Result |
| --- | --- | --- | --- |
| Unclamped GPIO minimum, assumed harness corner | 0.0346293 | min -0.1 | **PASS** |
| Unclamped GPIO maximum | 3.3 | max 3.4 | **PASS** |
| Peak current through remote switch | 0.0310089 | max 0.05 | **PASS** |
| Held LOW level | 0.0346293 | max 0.825 | **PASS** |
| Released HIGH after 1.9 ms | 2.62965 | min 2.475 | **PASS** |

## Summary

**Overall:** PASS

---

```text
SIM_REPORT_VERSION=1
PASS=true
EXIT_CODE=0
SIM_BASELINE_COMPARE=false
```


## Waveform plots

PNG files (committed path relative to board root):

- `sim/plots/tran-vout-battery.png`
- `sim/plots/tran-vbat-sw.png`
