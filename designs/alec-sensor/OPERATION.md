# Power, sleep and alarm behavior

## Working assumption

The user has not yet chosen all-day sensing versus sensing around alarm times. S0 supports both electrically. The recommended default is a scheduled detection window, with continuous sensing available for experiments. Detection duration, required battery replacement interval and recovery after an unexpectedly late wakeup still need product decisions.

## Battery reality

The LD2410C alone uses approximately 0.395 W at its specified average current. Putting the ESP32 into deep sleep while leaving the radar powered saves only the MCU share. Three AA cells in series add voltage; their amp-hour capacity does not triple. [Hi-Link product specifications](https://www.hlktech.com/en/Goods-239.html).

The following are **sensitivity estimates, not measured battery-life claims**. They assume 9 Wh usable pack energy, 85% conversion efficiency, 80 mA average ESP32 load at 3.3 V while awake, and 0.2 mA whole-board sleep current at a 4.5 V pack. Neither the cell model nor those board currents has been measured. Radio check-ins and setup time must be counted in awake time.

| Radar/MCU active time per day | Illustrative runtime |
|---|---:|
| 15 minutes | about 42 days |
| 30 minutes | about 22 days |
| 1 hour | about 11 days |
| Continuous | about 12 hours |

For 6–12 Wh usable energy, the radar alone would exhaust the energy budget in roughly 13–26 hours at 85% efficiency. Actual results depend on cell chemistry, load pulses, voltage cutoff, temperature and contact resistance. [Editable calculation](tools/power_budget.py), [all scenarios](review/power-budget.json).

Do not advertise weeks of continuous LD2410C presence sensing on three AA cells. If long life and all-day detection are both mandatory, revisit the sensor choice or power source before layout. S0 keeps the requested LD2410C.

## Power states

1. **Hard OFF:** SW1 disconnects the pack from the circuit. Clock time is lost; peer settings in ESP flash can persist. Time must be synchronized before the sensor claims it is ready for scheduled operation. Backup switchover/trickle charge stay disabled; unused RTC backup pin has the manufacturer's 10 kΩ termination.
2. **Scheduled sleep:** keep 3.3 V and the RTC alive; open U10, stop UART, then disable radar 5 V. Configure RTC/button wake and a bounded timer fallback. Disable unused RTC CLKOUT. Set the RGB outputs OFF and validate pad hold in the selected sleep mode. Release held button and clear RTC interrupt flags before sleeping to avoid immediate wake loops.
3. **Scheduled wake:** start before the alarm window; validate clock, battery and peer/session. Keep U10 open while starting 5 V. Confirm power-good, close U10, establish UART and wait for valid settled measurements. Startup duration must be measured after every power cycle; never accumulate dwell during initialization.
4. **Active alarm:** keep radar continuously operating throughout dwell measurement. Do not duty-cycle it through a claimed continuous presence interval. Send heartbeat/status and authenticated, session-specific completion messages with application acknowledgments and bounded retries.
5. **Powered-radar wake experiment:** retain 5 V and U10 ON, sleep the ESP32 and wake on OUT. Use RTC-capable GPIO4; level polarity differs from RTC/button. Configure a compatible combination of wake sources for the pinned ESP-IDF version. This mode still pays the radar's continuous power cost. Verify GPIO hold and reset behavior; pull-downs deliberately turn the radar and isolation off during an ordinary reset.

Wi-Fi is powered off during deep sleep; **an ESP-NOW packet cannot wake a deeply sleeping ESP32-S3**. The bedside alarm must distribute schedules while the sensor is awake, and the sensor needs timed rendezvous opportunities for changes. Include the clock uncertainty and missed check-ins in the wake guard time. Report “sensor not ready” at the bedside unit if the requested schedule has not been acknowledged. [Espressif sleep documentation](https://docs.espressif.com/projects/esp-idf/en/stable/esp32s3/api-reference/system/sleep_modes.html).

Do not bridge the three signal-isolation channels with zero-ohm links for convenience. There is no level translation needed during normal operation, but an unpowered radar can otherwise receive current from MCU I/O. U10's off state must be validated with UART high/low, pull-ups, firmware crashes and unequal supply ramps. A powered-off-protected switch does not automatically establish safe sequencing for the entire system.

## Presence contract

The required behavior is evidence of a person in the selected zone for X seconds. The radar does not prove identity, attention, getting washed or even that a target is inside the shower rather than beyond a glass door. Water-only motion, a curtain and adjacent-room presence are deliberate rejection tests.

- Consume fresh `MyLD2410` data frames continuously. Match the actual module firmware and pin a tested library version. Hardware UART defaults are 256000 baud, 8N1. [MyLD2410 upstream](https://github.com/iavorvel/MyLD2410).
- Use a monotonic dwell clock, not wall-clock subtraction. Reset the dwell accumulator on invalid/stale data, reset, out-of-zone targets or confirmed absence. Require a current alarm-session identifier before any completion message.
- The module's configured no-person delay holds the presence result after a departure. Characterize that delay and the firmware's reporting behavior; OUT high alone cannot prove continuous dwell. Set the shortest useful hold time, use engineering/per-gate evidence where available, and account for residual hold in the acceptance test. Fresh UART packets can still contain a held detection result.
- Derive data freshness timeout from the measured reporting interval. Start with a deliberately conservative timeout during bench testing, then record it in the firmware configuration. Unknown input must never be treated as successful dwell.
- Ordinary packet loss does not erase the persistent ESP-NOW peer. Retry/recover channel and schedule synchronization. Reserve long-press pairing for deliberate commissioning, replacement or recovery.
- Suggested UI: short press shows battery briefly; long press enters a timed pairing window; soft green indicates verified active presence; a distinct blink indicates a fault or pending pairing. LED brightness and duty cycle belong in the measured power budget.

No application firmware has been implemented or bench-tested in S0. These are the implementation and test requirements for the next firmware pass.
