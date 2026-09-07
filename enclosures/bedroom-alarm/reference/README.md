# Accepted v4 comparison scene

`bedroom-cube-v4.blend` is the original accepted v4 packaging scene, before the 1.3-inch display update. It is retained as an immutable comparison input, with its SHA-256 recorded in `../source-manifest.json`.

The verifier opens both complete scenes and compares 223 preserved objects using evaluated world-space vertices (rounded to 0.0001 mm) and face indices: exterior, main PCB, holder/cells, speaker/pod, control PCB and selected supports. The display, its mounts/harness and the small front UI board adjustment are intentionally outside that preservation comparison and have their own geometry checks.

The current editable model and generator are one directory above. This historical scene is a packaging reference, not a released design or evidence of physical qualification. Its embedded model geometry needs no prior task, ignored output directory or Git ancestor to be recovered.
