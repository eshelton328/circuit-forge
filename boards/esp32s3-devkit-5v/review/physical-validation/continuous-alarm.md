# Continuous alarm: speaker and load proposal

6 September 2026, PR #122. The user intends an alarm, probably continuous,
and wants loud output with good sound quality. **Speaker, listening distance,
alarm duration, enclosure and maximum environment are still unselected.**
For thermal screening we assume 100% audio duty during the alarm, without taking
credit for silence between alarms. See [recorded requirements](../../analysis/operating-requirements.json).

## Recommended starting point

Prototype an **efficient 8 ohm full-range speaker at 1 W continuous audio**,
with a 0.5 W reduced-output mode for comparison. These are proposed test levels,
not approved battery-life or temperature ratings. A concrete candidate is the
[Visaton FRS 5 X, 8 ohm, article 2235](https://www.visaton.de/en/products/drivers/fullrange-systems/frs-5-x-8-ohm):
5 cm nominal size, 86 dB mean sensitivity at 1 W/1 m, 5 W rated input, 46 mm
cutout and 140 g mass. Check the mounting drawing and enclosure depth before
selection. Its 5 W rating is power handling; the board would deliver about 1 W
in this proposal. It has not been added to the purchasing BOM or auditioned.

An 8 ohm impedance is not inherently better sounding than 4 ohm. The recommendation
sets a manageable output target for this battery architecture. Speaker sensitivity,
frequency response, mounting, distortion and the actual alarm waveform determine
the result. If mechanics require a much smaller driver, compare sensitivity using
the same input power, measurement distance and frequency band; large dB figures
measured at 10 cm are not comparable directly with 1 m specifications.

| MAX98357A output reference at 5 V | Audio power at 1% THD+N | Proposed use |
| --- | --- | --- |
| 8 ohm with datasheet's 68 uH test inductance | 1.4 W | Start qualification at 1 W, leaving some output headroom |
| 4 ohm with datasheet's 33 uH test inductance | 2.5 W | Higher-power comparison if the acoustic target needs it |

The advertised 3.2 W point uses 4 ohm at 10% THD+N. These are amplifier test-load
conditions, not guaranteed acoustic distortion of a real speaker. At equal
speaker sensitivity, 2.5 W versus 1.4 W buys only about 2.5 dB while increasing
power demand. Do not use speaker wattage as a proxy for loudness.
[Amplifier datasheet](https://www.analog.com/media/en/technical-documentation/data-sheets/max98357a-max98357b.pdf).

## Loudness and enclosure

Using the candidate's mean sensitivity, ideal far-field arithmetic gives about
86 dB at 1 m, 76.5 dB at 3 m and 72 dB at 5 m for 1 W. These are **rough
unweighted SPL estimates**, not measured dBA, alarm audibility, or predictions
through walls. The speaker response at the actual alarm frequencies, enclosure,
grille, orientation, room reflections and background noise all matter. The
calculation is L = sensitivity + 10 log10(P/1 W) - 20 log10(distance/1 m).
[Distance scaling reference](https://www.nti-audio.com/en/support/know-how/more-sound-level-calculations).

Mount the driver securely and seal its rim to a baffle so its front and rear
sound paths do not cancel. Provide adequate grille area and cone clearance;
avoid a rattling cover. Decide the acoustic rear volume before freezing the
overall enclosure, and keep the electronics' heat rejection separate from the
speaker chamber where practical. These installation details follow
[Visaton's mounting guidance](https://www.visaton.de/sites/default/files/downloads/Visaton_Basics-of-speaker-installation_2025-05_V1_1.pdf).
The driver's quoted low-frequency range does not promise useful bass in an
arbitrarily small box.

Use a smoothly enveloped alarm waveform and avoid clipping or excessive bass
boost. Choose any high-pass filtering after reviewing the actual sound and
mounted driver response. For a loud, clear tonal alarm, energy in the driver's
efficient midrange is a better starting point than trying to reproduce deep bass.
No final tone, loudness requirement or firmware limiter has been selected here.

## Electrical and thermal screening

[audio-load-proposals.json](../../analysis/audio-load-proposals.json) defines
160 static source cases: ten three-AA pack scenarios, two sustained 3.3 V loads,
four audio powers and two assumed amplifier efficiencies. The 2.5 W rows are
4-ohm comparisons; they do not imply the proposed 8-ohm driver can receive 2.5 W
from this amplifier. Lithium cases remain conditional on primary 1.5 V Li/FeS2.

The reference digital load is 0.25 A, with 0.5 A as a sustained stress case.
Neither is a measured firmware average. Audio current at 1 W is approximately
0.226 A from 5 V at the 90% incremental-efficiency assumption, or 0.253 A at
80%, including the assumed idle overhead. Battery current is higher after
conversion and sag; see the [source-case CSV](audio-battery-results.csv).

Six thermal cases use the actual saved copper, seven modeled heat sources
including Q1, and a nominal 4.5 V pack with 0.55 ohm external resistance
(three 0.15 ohm cells plus 0.10 ohm holder/wire). Q1 adds the separate assumed
0.13 ohm. Converter efficiency is 85% and incremental amplifier efficiency
80%, both assumptions. Local air is 50 C; h=5 and h=10 W/(m2 K) each face
are uncalibrated cooling sensitivities. They do not represent confirmed enclosure
performance. The same reduced PCB thermal model and limitations in the earlier
[operating-envelope report](operating-envelope-update.md) apply.

| Continuous-load scenario | Battery A | PCB heat W | Peak PCB C, h=5 | Peak PCB C, h=10 |
| --- | --- | --- | --- | --- |
| 1 W audio, 0.25 A digital | 0.602 | 1.508 | 96.8 | 75.6 |
| 1 W audio, 0.50 A digital | 0.879 | 2.532 | 130.5 | 94.9 |
| 0.5 W audio, 0.25 A digital | 0.409 | 1.247 | 89.8 | 72.2 |

These are board temperatures, not junction temperatures. The new cases are at
0.5 mm pitch; the existing moderate-load 0.25 mm convergence check does not
certify every new case. The runner enforces energy conservation. It does not
model battery heating inside the box, speaker heat returned to enclosure air,
package internals, electrochemical discharge or transient/RMS current effects.
Alkaline depletion still needs a reduced-audio/restart strategy; changing to an
8-ohm speaker alone cannot resolve that requirement.

## Gain setting and free measurements

At the board's nominal 12 dB gain, the datasheet transfer equation suggests
approximately **-5.07 dBFS for a 1 W sine into nominal 8 ohm**, or -8.08 dBFS
for 0.5 W. Start below these levels and calibrate on hardware. These are
pre-clipping sine calculations, not a validated software power limit. Gain
tolerance, actual speaker impedance, supply droop and waveform crest factor
change the result. A final limiter must control peak voltage and sustained
power appropriately; fixed peak amplitude does not give the same average power
for every waveform. [MAX98357A gain equation](https://www.analog.com/media/en/technical-documentation/data-sheets/max98357a-max98357b.pdf).

1. Fit the candidate in a representative enclosure and play the intended alarm
   using the board's firmware playback path. Start at reduced volume. Record the
   exact asset, digital level and duration. Exercise simultaneous radio traffic.
2. Use the **free edition of [Room EQ Wizard](https://www.roomeqwizard.com/)**
   with available microphone hardware to compare response, distortion and grille
   effects. A calibrated microphone or sound-level reference is needed for an
   absolute SPL claim; an uncalibrated phone/mic is only a relative screening tool.
   The board has not been configured as a USB audio interface in this PR.
3. Measure SPL at 1 m and at the required listening location, including orientation
   and background noise. Listen for buzz, rattling and harsh clipping. Record
   weighting, averaging and the actual tone spectrum; do not label the candidate's
   published sensitivity as measured alarm SPL.
4. Run the continuous alarm to thermal stability using the [bench plan](bench-plan.md).
   Record battery, local air, Q1, both converters, amplifier and module temperatures,
   pack sag and resets. Repeat with fresh and depleted examples of each intended
   AA chemistry. Measure audio voltage differentially: neither speaker wire is
   ground. No grounded scope clip or direct sound-card input belongs on a BTL output.

Free Python source and the new result hashes are in the qualification runbook.
The [full numerical results](audio-results.json), [source-case CSV](audio-battery-results.csv)
and [raw thermal fields/inputs](audio-raw.zip) accompany this review. Local
verification completed with **100 Python tests passed**, including seven new
acoustic-scaling and sine-level controls. These mathematical controls do not
assert a speaker's acoustic performance.
No physical audio or temperature measurement has been performed. Acoustic
reach, thermal margin and speaker choice remain open until the requirement and
measurements support them.
