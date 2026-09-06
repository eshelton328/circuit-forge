# Frozen pre-compaction comparison PCB

`pre-compaction.kicad_pcb.gz` contains the exact PCB used as the reference in
the published physical-screening report, compressed with a zero timestamp.

- Source commit: `f11e64e67c3d4472d788ae74326400449ac3b944`
- Source path: `boards/esp32s3-devkit-5v/esp32s3-devkit-5v.kicad_pcb`
- Decompressed SHA-256: `b352395f28b7f507c354b84f957709dab3f2d78d12038861ad5866c3b6ce6595`

PR #122 was squash-merged, so its intermediate commits are not part of main's
history. Keep this snapshot in the repository so a fresh or shallow checkout
can reproduce the comparison without fetching a retired branch or PR ref.

`scripts/ci/extract-physical-reference.py` decompresses the snapshot and checks
its bytes against `manifest.reference_pcb_sha256` in the published report before
writing the output. The original and current PCBs are then exported with the
same KiCad version in CI. This archive preserves the existing reference; it is
not a replacement baseline or a new simulation result.
