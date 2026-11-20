# SIGNAL 002 motion-cadence check — 2026-11-20 04:49 CET

Private local source: `production_private/signal-002-motion-24fps-private.mp4` (not committed).

Executed bundled FFmpeg v9.0.2 with `-vf mpdecimate -an -f null -` on the full 20-second video and its 12-fps predecessor. Output retained 108 frames from the nominal 480-frame 24-fps render, versus 104 from the nominal 240-frame 12-fps version. `mpdecimate` is threshold-dependent, not an exact count of unique frames, but the near-identical retained counts show the 24-fps encode has **not demonstrated doubled motion detail**. Nominal frame-rate and black/freeze detection alone are insufficient quality gates. Do not approve or publish either video on this evidence.

Next technical gate: inspect contact-sheet frames and edit source motion/keyframes rather than merely re-encode at 24 fps; rerun identical cadence comparison and human visual/audio QA. Distribution still requires an authenticated social channel; no on-chain token or verified creator fees.

No spending, signing, minting, transfers, or private media publication.
