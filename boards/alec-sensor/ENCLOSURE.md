# Circular enclosure interface

The preferred shape is **circular**, following the user's choice. The earlier 100 × 40 mm sketch was not dimensioned around the complete stack. S1.1 remains **116 mm diameter × 54 mm deep**, plus the external mounting cradle. The diameter includes battery removal clearance, the rear seal and screws outside the main seal.

See the [editable assembly, STEP parts and mechanical checks](../../enclosures/alec-sensor/). [interface.json](../../enclosures/alec-sensor/interface.json) defines the mechanical coordinate frame. KiCad (132, 102) maps to the enclosure's XY origin; +Z points from the rear cover toward the radar/front face.

| Interface | S1 nominal geometry |
|---|---|
| PCB | 64 × 56 × 1.6 mm; F.Cu at Z=26 mm |
| Mount holes | KiCad (104,74), (160,74), (104,113), (160,115), M3 |
| Lower-right support | Short post and side rib below radar; no full-height post through radar |
| BH3AAW holder | 57.15 × 46.61 × 17.39 mm; rear-facing cell opening; fixed internal carrier independent of cover |
| Radar socket | SSW-105-01-F-S, 8.51 mm nominal housing; PCB connector pin1 at (145,108) |
| LD2410C | Manufacturer STEP body 22 × 16 mm; existing 2.54 mm header retained |
| Radar/front | Front copper plane Z=38; nominal air gap 12.4 mm; PC face 3.6 mm |
| Button | SW7 at (114,121); guided plastic plunger and clamped silicone membrane |
| Presence LED | D2 at (130,121); light pipe behind an unbroken PC optical window |
| Rear seal | Candidate 100 × 2 mm EPDM O-ring; 2.8 × 1.5 mm groove; 25% nominal squeeze |
| Rear screws | Six M2 positions on 110 mm pitch circle, outside main seal; blind insert pockets |
| Service controls | SW1 POWER at (153,86.5), SW2 RESET at (115,85), SW3 BOOT at (130,85); all B.Cu, reached with holder/cells installed |
| Battery carrier | Three M2 mounts at enclosure (−36,−5), (36,−5), (0,−44); 1 mm plate, 1 mm ribs and four nominal edge hooks |

Removing the six rear-cover screws exposes the cell openings and all three service controls without moving the PCB or unplugging the holder. The external battery/pair button remains on F.Cu under its membrane. USB cable service can still require carrier/PCB removal. The CAD checks 19 selected solid/approach intersections, including rectangular finger-access envelopes with the holder and carrier installed; hand size, clip deflection, material creep and tolerances need samples.

The proposed 3.6 mm PC wall and 12.4 mm gap follow the manufacturer's radome guidance as starting values. They do not prove RF transmission. Test the actual polymer grade, pigments, surface finish, wet films and installed mounting angle. Keep metal, carbon-filled plastic and conductive coating out of the radar face and ESP antenna region.

An external cradle provides screw slots and an interface for adhesive or suction adapters. The suction cup, adhesive grade, locking detail, load retention and seal/insert tolerances are not released. Do not describe the render as IP-rated. The geometry includes internal undercuts and needs a prototype manufacturing review; a CNC supplier may split internal supports into separate parts.
