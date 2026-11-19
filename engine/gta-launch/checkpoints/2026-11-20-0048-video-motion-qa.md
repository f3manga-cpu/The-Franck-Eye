# GTA video motion QA — 2026-11-20 00:48 CET

Source: private local `production_private/` files; no private video, credentials, or wallet address published.

Executed bundled FFmpeg v9.0.2 via the project `.venv` with full decode, `blackdetect=d=0.4:pix_th=0.10`, and `freezedetect=n=-50dB:d=1` on both SIGNAL 002 prototypes. All six FFmpeg commands returned exit 0; no qualifying black intervals reported.

| Private prototype | Length | Dimensions | FPS | Video bitrate | Audio | Motion QA |
|---|---|---|---|---|---|---|
| `signal-002-motion-review.mp4` | 20 s | 1080x1920 | 12 | ~288 kbps | AAC mono 22050 Hz | No >=1s freeze detected |
| `signal-002-review.mp4` | 20 s | 1080x1920 | 12 | ~92 kbps | AAC mono 22050 Hz | Repeated freezes: 0–5s, 5–10s, 10–15s, and 15s onward |

**Decision:** Both are technically decodable but neither is approved as an exceptional-quality final. The static review version fails motion QA; the motion variant has no detected long freezes but only 12fps and a low video bitrate. Objective compression/motion checks cannot establish legible typography, visual continuity, sound rights or creative quality. Keep both private. Next executable step: create a materially improved motion edit with original/rights-cleared elements and review frames/audio before any external distribution.

Other gates checked: Metricool brand 7726700 returned no connected social network; private Codex scout latest file absent. systemd GTA wallet/audience/editorial service last results `success` (not a fresh restart test). No token issuance or financial action authorized or performed.
