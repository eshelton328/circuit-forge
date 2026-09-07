# Dimensional sources

Manufacturer documents/CAD are retained as engineering reference material with their original attribution. Inclusion here does not assign them a new license or imply endorsement. Source URLs and SHA-256 hashes are in [source-manifest.json](source-manifest.json).

- **EastRising ER-OLEDM013-1W-I2C:** datasheet page 6 is the four-pin I2C-only outline; page 8 gives pin order and page 9 gives supply/current limits. `display-drawing.png` is page 6 rendered for review. The seven-pin SPI/I2C variant and bare production panel are different parts.
- **MPD BH3AAW:** original manufacturer STEP and drawing. `BH3AAW.glb` is the KiCad-converted source; the Blender generator trims the long straight wire overhang and models the routed lead separately. Loaded contacts, actual cells and removal force remain untested.
- **Visaton FRS 5 X, 8 ohm:** manufacturer datasheet. The envelope also uses the manufacturer's [mechanical drawing](https://www.visaton.de/sites/default/files/dd_product/frs5x_tz.gif); basket and terminal profiles remain simplified.
- **E-Switch EG1218:** manufacturer drawing and its rendered review image. The proposed switch carries an enable signal, not the alarm's battery load.
- **Current PCB GLB:** KiCad 10 export of `boards/esp32s3-devkit-5v/esp32s3-devkit-5v.kicad_pcb`. Its native-board SHA-256 is recorded. These existing package models do not establish every ordered component's maximum envelope.

Blender files embed the imported meshes. The original source files are retained to make future dimension checks and conversions reviewable.
