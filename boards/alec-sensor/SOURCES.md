# Source register — checked 2026-09-07

Manufacturer data and upstream documentation inform S1. Simulation and future test requirements are engineering proposals, not vendor qualification results.

| Source | Use / qualification |
|---|---|
| [User's LD2410C English PDF](https://naylampmechatronics.com/img/cms/001080/HLK-LD2410C_datasheet.pdf) | Original reference. C outline drawing and generic parameter table conflict; do not copy the 7 × 35 mm entry. |
| [Hi-Link LD2410C product/downloads](https://www.hlktech.com/en/Goods-239.html) | Primary product page, 5 V, approximately 79 mA; downloads for model and latest manual. Product page itself also has some generic inherited text. |
| [Hi-Link C manual V1.09](https://r0.hlktech.com/download/HLK-LD2410C-24G/1/HLK%20LD2410C%E7%94%9F%E5%91%BD%E5%AD%98%E5%9C%A8%E6%84%9F%E5%BA%94%E6%A8%A1%E7%BB%84%E8%AF%B4%E6%98%8E%E4%B9%A6V1.09.pdf) | Download links should be resolved through the product page if this URL changes. Actual downloaded title V1.09, 2024-10-08, 21 pages; pages 7/8: C outline and pins, 9: power/UART, 18: current and C dimensions, 19: radome. See local retrieval hashes below. |
| [Hi-Link radome guide, 2023-04-28](https://r0.hlktech.com/download/HLK-LD2410C-24G/1/%E6%AF%AB%E7%B1%B3%E6%B3%A2%E4%BC%A0%E6%84%9F%E5%99%A8%E5%A4%A9%E7%BA%BF%E7%BD%A9%E8%AE%BE%E8%AE%A1%E6%8C%87%E5%8D%97_%E6%B5%B7%E5%87%8C%E7%A7%91.pdf) | Material wavelength, uniformity, spacing; separate generic installation guidance is not identical to the 12.4/18.6 mm recommendation. |
| [MyLD2410 upstream](https://github.com/iavorvel/MyLD2410) | B/C support; ESP32-S3 hardware UART example uses RX18/TX17. Firmware/library version not pinned or compiled yet. |
| [ESP32-S3 sleep](https://docs.espressif.com/projects/esp-idf/en/stable/esp32s3/api-reference/system/sleep_modes.html) | Deep-sleep radio off, RTC wake, GPIO hold and wake polarity constraints. Pin firmware to a tested IDF release. |
| [ESP32-S3 module placement](https://docs.espressif.com/projects/esp-hardware-design-guidelines/en/latest/esp32s3/pcb-layout-design.html#general-principles-of-pcb-layout-for-modules-positioning-a-module-on-a-base-board) | Antenna at board edge, manufacturer keepout and final-enclosure RF verification. |
| [ESP32-S3 native USB](https://docs.espressif.com/projects/esp-idf/en/latest/esp32s3/api-guides/jtag-debugging/configure-builtin-jtag.html) | GPIO19 D− and GPIO20 D+. |
| [TPS63070 datasheet](https://www.ti.com/lit/ds/symlink/tps63070.pdf) | Reused topology, output feedback, power-save polarity, shutdown and startup constraints. |
| [TMUX1511 datasheet rev B](https://www.ti.com/lit/ds/symlink/tmux1511.pdf) | TSSOP/PW 14-pin table, HIGH closes switch, powered-off protection; QFN pin tables differ. |
| [RV-3028 application manual](https://www.microcrystal.com/fileadmin/Media/Products/RTC/App.Manual/RV-3028-C7_App-Manual.pdf) | Same RTC as main; page 103 no-backup circuit; disable unused CLKOUT and backup/trickle-charge behavior. |
| [Gore jet/immersion case study](https://www.gore.com/resources/gore-protective-vents-ensure-rf-system-reliability-right-ip-rating-heavy-rain-conditions) | Separate water-jet and immersion requirements; assembly-dependent ratings. |
| [Gore pressure vents](https://www.gore.com/products/pressure-vents-portable-electronics) | Membrane integration, pressure/condensation considerations; no whole-product rating inferred. |
| [MPD BH3AAW drawing](https://www.batteryholders.com/uploads/parts/BH3AAW/datasheets/BH3AAW-datasheet.pdf) | Existing ALEC holder candidate; source already retained under enclosures/alec/sources. |

Additional selected-part primary sources:

- [C&K/Littelfuse 1000 series](https://www.littelfuse.com/assetdocs/littelfuse-c-k-slide-1000-series-datasheet?assetguid=68a2b41e-19a4-4cf4-821b-aca78a430f00): 1101M2S3CQE2 SPDT common pin 2, 6 A at 28 VDC, 65°C operating maximum. Custom footprint/model follow the drawing; capacitive-inrush endurance remains untested.
- [Littelfuse 467 fuse](https://www.littelfuse.com/assetdocs/fuse-467-datasheet?assetguid=4a59f034-1cca-460e-a5ba-e1e66247c76d): 046701.5NRHF nominal resistance 0.0385 Ω, melting I²t 0.0766 A²s. Apply continuous and temperature derating.
- [Samtec SSW drawing](https://suddendocs.samtec.com/prints/ssw-1xx-xx-xxx-x-xx-xxx-xx-mkt.pdf): SSW-105-01-F-S, 13.21 × 2.41 × 8.51 mm housing, 2.54 mm pitch, 2.64 mm tail. Verify module insertion and retention on real samples.
- [Samsung CL31A107MQHNNN](https://product.samsungsem.com/mlcc/CL31A107MQHNNN.do): C21 100 µF / 6.3 V / 1206 candidate. Other capacitor/resistor sources and complete ordering codes are recorded in [parts.py](tools/parts.py) and [BOM](review/bom.csv). Effective capacitance under bias remains a validation gate.

Third-party PDFs and the radar STEP were inspected locally. Original retrieval hashes are in [reference-retrieval-hashes.json](review/reference-retrieval-hashes.json). The enclosure now includes a GLB converted from the vendor radar STEP, together with the actual PCB and existing MPD holder geometry. Its [source provenance](../../enclosures/alec-sensor/sources/provenance.json) records the conversion; colors and custom retention/harness geometry are illustrative. Native source/evidence hashes for this revision are separate in [source-hashes.json](review/source-hashes.json).
