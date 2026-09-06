# Closing the load, cooling and parasitic questions

6 September 2026. Applies to the corrected PR #122 copper, PCB SHA-256
`0e17f9ad0cf0508d8a53ed51c0b1e6af4423311598bbb03fe811c556e8b1e7d8`.
This is an executable test plan and a requirements worksheet, not a record of
hardware tests. **No hardware measurements have been supplied.**

## 1. Select the operating envelope

Record the answers in [operating-requirements.json](../../analysis/operating-requirements.json).
The user has specified **three AA cells, alkaline or lithium**. The series
connection is the working interpretation; the precise lithium chemistry is
awaiting clarification. L91 analysis below is conditional on primary 1.5 V cells.
Null means unknown, never zero or accepted. The earlier
[operating-envelope.json](../../analysis/operating-envelope.json) is a frozen
proposal snapshot from before this clarification, not the product specification.

| Required input | What is needed | Why it changes the decision |
| --- | --- | --- |
| Battery | Chemistry, cells, maximum fresh voltage, minimum loaded voltage, capacity, protection and pack/cable resistance | Cold start, current, Q1 loss and battery sag |
| Audio | Speaker MPN/impedance, continuous audio watts, maximum burst watts and duration, longest cable | 5 V demand, enclosure heat and speaker-cable EMI |
| Digital | Firmware/workload, average current and burst current/duration on 3.3 V, OLED/LED use | A 500 mA-capable supply does not imply 500 mA continuous heat |
| Mechanics | Enclosure material/dimensions, vents, board orientation/clearance, battery and speaker positions | Determines heat rejection and RF/cable geometry |
| Environment | Maximum external air temperature and local air temperature beside the powered PCB | These temperatures can differ substantially inside a box |
| Production | Actual stackup and copper thickness, via plating/fill, capacitor MPNs and bias curves | Fixes the electrical and thermal model geometry/materials |
| Test access | Assembled hardware, multimeter, scope/probes, fine temperature probe | Determines which claims can be measured now |

The [Espressif module datasheet](https://www.espressif.com/sites/default/files/documentation/esp32-s3-wroom-1_wroom-1u_datasheet_en.pdf)
specifies at least 0.5 A external supply capability, while its listed Wi-Fi TX
current reaches 355 mA under stated RF conditions. Neither value is an application
average or a complete peripheral budget. Measure the intended firmware.

The [MAX98357A datasheet](https://www.analog.com/media/en/technical-documentation/data-sheets/max98357a-max98357b.pdf)
lists 2.5 W into its specified 4 ohm test load at 1% THD+N and 3.2 W at 10% THD+N,
at 5 V. The advertised 3.2 W is not a low-distortion continuous requirement.
Choose the sound requirement before sizing the thermal load.

## 2. Use a complete power balance

The new [free calculator](../../../../scripts/qualification/power_budget.py)
keeps speaker power separate from PCB heat and includes Q1 loss:

```text
P3 = 3.3 * I3
P5 = Paudio / eta_audio_incremental + P_amplifier_idle
Pconverter_input = P3 / eta3 + P5 / eta5
Pconverter_input = Ibat * (Vopen - Ibat * Rtotal)
Q1 heat = Ibat^2 * RQ1
Board heat = converter losses + retained 3.3 V power + amplifier loss + Q1 heat
```

The calculator uses the high-voltage solution of the supply equation and rejects
the maximum-power nose or a negative discriminant. This is a steady-state source
calculation, not startup or converter stability validation. External series
resistance represents battery, contacts and cable; its heat is outside the PCB
model. Actual board trace/other component losses and source dynamics still need
measurement. The 0.13 ohm Q1 scenario includes an assumed temperature allowance;
the [AO3401A data](https://www.aosmd.com/sites/default/files/res/datasheets/AO3401A.pdf)
specify 85 milliohm maximum at -2.5 V gate drive and 25 C, with resistance rising
with temperature. The scenario is not a guaranteed hot maximum.

For the three-AA requirement, use the separate
[battery scenarios](../../analysis/aa-battery-scenarios.json). The earlier 0.20 ohm
external-source assumption is optimistic: [E91 alkaline data](https://data.energizer.com/pdfs/e91.pdf)
list 0.15-0.30 ohm fresh nominal IR **per cell**; three series cells sum to
0.45-0.90 ohm before the holder. [L91 primary-lithium data](https://data.energizer.com/pdfs/l91.pdf)
list 0.12-0.24 ohm typical IR per cell, depending on method. Neither is a complete
dynamic battery model. Test both chemistries with actual holder contacts and
at the longest burst and steady-load durations. Resistance changes with state,
temperature and measurement timescale; do not use one value to predict runtime.

Test restart separately from continued operation: TPS63070 needs at least 3 V
at its input when starting with output below 3 V. Its ability to keep running
at lower input does not guarantee a restart from depleted AAs. A proposed
firmware policy is staged enable, load-aware low-battery indication, audio
reduction before brownout, and hysteresis/retry limits. Select thresholds from
measured loaded voltage and worst-case measurement error; they are not yet set.
Pack voltage alone cannot detect a weak/reversed individual cell. Confirm the
cell manufacturer's end-of-discharge guidance and avoid mixed cells.

The example E91 operating range stops at 55 C; L91 at 60 C. At 50 C local air,
battery self-heating and proximity to the PCB therefore matter even if PCB
temperatures pass their own limits. Measure the batteries in their actual holder.

For sustained load, measure average electrical power. For bursts, record current,
duration and repetition separately. Do not square average current to estimate
resistive heat when current fluctuates: use mean(I^2)*R. Do not multiply a
steady-state peak temperature by an audio duty factor without a thermal transient
model. The current calculator deliberately evaluates constant cases only.

Speaker power is off the PCB but mostly remains as heat in a shared enclosure.
Battery/contact loss and a powered display can also heat that enclosure. The
thermal solver's air boundary must therefore use **local internal air**, not the
external environment. An assumed h=5/10/20 W/(m2 K) is a sensitivity parameter;
it is not proof of the cooling provided by a sealed, vented or fan-cooled box.

## 3. Hardware load and thermal sequence

Use existing or borrowed instruments; all analysis can use Python and CSV files.
No paid simulator is required. A multimeter can establish average power but
cannot capture Wi-Fi current bursts or switch-node ringing. Temperature and fast
waveform claims remain open until suitable measurements exist.

1. Record board revision, fitted part numbers, firmware commit, enclosure,
   orientation, battery state, wires and instruments. Check polarity and shorts.
   Bring up from a current-limited source within the selected battery envelope;
   start with audio disabled and increase the limit only to the planned load.
2. Measure at idle, Wi-Fi traffic with audio disabled, audio with minimal radio,
   and simultaneous worst intended radio/audio/OLED/LED operation. Include
   sustained audio and the longest specified burst. Use the actual speaker/load.
3. For each mode record voltage at J1, battery input current, TP2 protected input,
   both rails, PG signals, reset/brownout events and audio clipping. Record
   short-window peak/RMS current and long-window average current separately.
   Test fresh, nominal and minimum battery states, including startup and restart.
4. Measure Q1 voltage drop directly across its power terminals under a stable
   load; P_Q1 = mean(Vdrop*I). For converter efficiency, measure simultaneous
   per-stage input/output power only if calibrated current access is available.
   Existing voltage test pads alone do not measure branch current. Do not infer
   individual converter efficiencies from one total battery-current reading.
5. Start at room temperature in the final enclosure. Log local air, external air,
   U1, U2, L1, L2, Q1, U6, ESP module and nearby board temperatures. Run at least
   30 minutes and continue until temperature rise above local air changes by
   less than 1 C over the final 10 minutes. This is a proposed stability criterion,
   not a fixed promise that 30 minutes is sufficient. Repeat at the declared
   maximum environment only after room-temperature behavior is understood.
6. Repeat the highest sustained load at the lowest loaded battery voltage and
   at any buck/boost transition within the selected range. Record airflow and
   orientation. Stop escalation of load if regulation fails, temperatures keep
   climbing, or an agreed component/temperature limit is reached.

| Test pad | Function | Measurement purpose |
| --- | --- | --- |
| TP1 | GND | DC reference; switch probing needs a much closer ground |
| TP2 | Protected battery / PFET | Battery sag after Q1 |
| TP3 / TP4 | 3.3 V / 5 V | DC levels; ripple should be probed at local ceramics |
| TP5 / TP6 | GPIO15 / GPIO13 | 3.3 V / 5 V power-good |
| TP7 / TP8 | EN_3V3 / GPIO18 | Enable timing |

Use the blank [measurement CSV](bench-measurements.csv); leave unmeasured values
blank. The sample-rate, instrument settings and actual waveform files belong in
the evidence directory. Never put simulated values in the measurement table.

For the TPS63070, estimate junction temperature from a measured package-top
temperature and the applicable characterization parameter: Tj approximately
Ttop + psiJT*P_IC. Its datasheet gives psiJT=2.4 C/W. Add documented sensor,
power-estimation and model uncertainty. A proposed target is **Tj estimate plus
uncertainty <=105 C**, retaining 20 C below its 125 C recommended operating
maximum. This is our proposed design margin, not a manufacturer rule. Determine
separate limits/methods for Q1, amplifier, inductor and the selected ESP module.

Do not add datasheet thetaJA to this PCB simulation or treat simulated board
temperature as measured package-top temperature. Follow
[TI's thermal measurement guidance](https://www.ti.com/lit/an/spra953c/spra953c.pdf?ts=1693387981055):
use a fine thermocouple at the package top and account for heat removed by the
probe. Package-top psiJT is not a universal thermal resistance, particularly if
a heatsink changes the top heat path. A large IR thermometer spot cannot isolate
a 2.5 x 3 mm regulator. ESP's internal sensor is not a PCB thermometer.

Compare several measured temperatures and power levels against the model. Fit
cooling using one mode, then validate against an independent mode and the closed
enclosure. Do not choose h merely to make one measurement match. Enclosure air
rise and package heat paths need separate treatment if residuals remain large.

## 4. Parasitic, ringing and EMI closure

The existing failed mesh gate is uncertainty in the extraction, not proof that
the board has failed. Keep the same physical ports, return window, materials and
geometry while refining. Require less than 5% change in R and L across two
successive refinements at the frequencies used by the circuit fixtures, followed
by independent grid-origin, port/contact, return-window, via and thickness checks.
Vary one setting at a time. A single finer result is not convergence.

Finalize the stackup before accepting absolute inductance. Select capacitors by
effective capacitance over bias, tolerance, temperature and aging, using the
manufacturer's data. For the present nominal 1.5 uH inductors, the TPS63070 lists
15 uF minimum effective output capacitance and 4.7 uF input capacitance; check
inductance-dependent requirements too. Nominal bank totals and arbitrary 25%
derating are not substitutes for part selection.

On hardware, test both converters in the selected buck, boost, transition,
startup, shutdown, light-load and maximum-load conditions, individually and
together. Measure L1 and L2 switch nodes relative to **local PGND**, input ripple
at C3/C11 and output ripple at C5/C13. Use a short ground spring or suitable
differential probe; long ground leads can create apparent ringing. Save full
bandwidth captures and probe settings. A limited-bandwidth ripple capture is
useful separately but cannot rule out fast spikes. Verify probe/scope rise time
and sample rate are adequate for the transient duration being assessed.

The [TPS63070 absolute limits](https://www.ti.com/lit/ds/symlink/tps63070.pdf)
are L1 -0.3 to 20 V and L2 -0.3 to 12 V, with distinct -3 to 25 V / -3 to 15 V
transient allowances only for t<10 ns while switching. These are stress limits,
not operating targets. Compare amplitude **and duration**, plus measurement
uncertainty; an unresolved sub-10 ns spike cannot be declared safe. Set design
margin after actual waveform/source conditions are known.

For the bridged Class-D output, neither speaker wire is ground. Never attach a
grounded scope clip to either speaker output. Use a suitable differential method
for audio voltage/power and separate audio-band content from the switching carrier.

Only after identifying a real resonance should a snubber experiment be made.
Save before/after ringing, rail ripple, efficiency and temperature, including
the resistor's dissipation. Apply the [TI measurement-based method](https://www.ti.com/document-viewer/lit/html/SSZTBC7).
Do not add a snubber just to make a hypothetical RLC fixture look better.

For EMI, keep cable length, speaker, battery, enclosure, workload and instrument
settings fixed. Relative near-field/FFT comparisons can locate sources, but a
free FFT does not supply calibrated emissions data, a LISN or a compliance
detector. Obtain conducted/common-mode and cable measurements with available
equipment before choosing filters. Compliance remains separate from these
engineering checks.

## 5. What closes each question

| Question | Required evidence | Current status |
| --- | --- | --- |
| Loads confirmed | Selected battery/speaker/workload plus measured average, RMS and burst current | Waiting for product inputs and hardware |
| Cooling confirmed | Final enclosure, stable temperatures, internal/external air and power readings at maximum intended use | Waiting for mechanics and hardware |
| Thermal margin resolved | Correlated model and valid component temperature estimates with uncertainty inside agreed margins | Open; scenario results alone cannot close it |
| Parasitic model resolved | Final stackup/parts and consistent mesh/contact/window/thickness convergence | Open; a finer diagnostic is recorded separately |
| Actual ringing acceptable | Adequately resolved local waveforms over the real operating envelope | No measurements |
| EMI acceptable | Defined target and appropriate conducted/radiated evidence in the final configuration | No measurements |

If the intended sustained load exceeds the demonstrated thermal or input-current
budget, reduce audio/digital demand, improve the heat path or increase board area.
Select among those changes using measured losses and hotspot locations. Further
cosmetic rearrangement cannot substitute for the missing operating specification.
