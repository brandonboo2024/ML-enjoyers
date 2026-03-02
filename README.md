# ML-enjoyers

Edge-first public safety prototype with audio fall detection as the first event class.

## Overview
Edge-first fall detection prototype with:
- Python edge (mic inference + offline queue)
- Node backend API
- TypeScript/Vite frontend dashboard

## Hackathon Alignment
- **Safety-relevant signals**: on-device audio inference for fall-like events.
- **Actionable intervention**: structured alerts with confidence and metadata (no raw audio).
- **Reliability**: designed for low connectivity via local processing and queued delivery.

## Start Here
- `WORKFLOW.md` — how to run the multi-agent process
- `SPEC.md` — API & ownership contract
- `TASKS.md` — assignments by role
- `CHANGELOG.md` — agent updates (use template in WORKFLOW)
- `PROTOTYPE.md` — how the demo pieces fit together
- `fall_detection_plan.md` — feasibility plan

## Dependencies
- Node.js 18+
- Python 3.10+
- pip

## Run Prototype (Quick Start)
- Backend: `cd backend && npm install && npm run dev` (http://localhost:4100)
- Frontend: `cd frontend && npm install && npm run dev` (http://localhost:5173)
- Edge (cnn_small): `python3 edge/edge_device.py --model edge/llm_artifacts/cnn_small/model.tflite --model-mode mel_cnn`

## Demo Runbook
1) Backend: `cd backend && npm install && npm run dev`
2) Frontend: `cd frontend && npm install && npm run dev`
3) Edge deps: `pip install -r edge/requirements-llm.txt`
4) Train + export (cnn_small):
   - `python -m edge.llm.train --data-dir archive.zip --model-type cnn_small --out-dir edge/llm_artifacts/cnn_small`
   - `python -m edge.llm.export_tflite --model edge/llm_artifacts/cnn_small/model.keras --out edge/llm_artifacts/cnn_small/model.tflite`
5) Run edge (mic): `python3 edge/edge_device.py --model edge/llm_artifacts/cnn_small/model.tflite --model-mode mel_cnn`
6) Validate UI: alerts appear, acknowledge works, refresh updates

## Low-Connectivity Demo (Option C + D)
- **Offline demo mode**: run edge with `--dry-run` to show alerts without any network dependency.
  - Example: `python3 edge/edge_device.py --model edge/llm_artifacts/cnn_small/model.tflite --model-mode mel_cnn --dry-run`
- **Metadata-only proof**: confirm the printed payload includes only time/device/event metadata (no raw audio).

## Planned Enhancements (Hackathon-Ready)
- **Location detection**:
  - Option 1 (static): CLI/config default per device.
  - Option 2 (Wi‑Fi/BSSID map): map known access points to room/zone.
- **Transport category**:
  - Enumerate `edge`, `wifi`, `cell`, `lorawan`, `offline`.
  - Show transport as a UI badge and filter.
- **Queue visibility**:
  - Surface queued alerts and last flush time in the UI.

## Default Config (edge/llm/config.py)

| Setting | Default | Notes |
| --- | --- | --- |
| `sample_rate` | 8000 | Lower compute, aligns with SAFE findings |
| `clip_seconds` | 3.0 | Centered window length |
| `n_fft` | 200 | 25 ms @ 8 kHz |
| `hop_length` | 80 | 10 ms @ 8 kHz |
| `n_mels` | 64 | Log-mel bins |
| `fmax` | 4000 | Nyquist for 8 kHz |
| `center_on_peak` | true | Center window on peak energy |
| `rms_normalize` | false | Disabled for live mic stability |
| `silence_gate` | true | Gate low-energy windows |
| `silence_rms_threshold` | 0.03 | Tune per environment |
| `mix_noise_prob` | 0.7 | Noise mixing for falls in training |
| `post_impact_quiet_seconds` | 1.5 | Require quiet after impact |
| `post_impact_rms_threshold` | 0.015 | Quiet threshold for post-impact rule |
| `post_impact_max_wait_seconds` | 3.0 | Drop pending triggers after this window |
| `calibration_silence_multiplier` | 2.0 | Multiplier for calibrated silence gate |
| `calibration_post_impact_multiplier` | 1.6 | Multiplier for calibrated post-impact gate |
| `trigger_threshold` | 0.75 | Default alert threshold |

Optional calibration (live mic):
- `python3 edge/edge_device.py --model edge/llm_artifacts/cnn_small/model.tflite --model-mode mel_cnn --calibrate-seconds 20`

## Model Variants (optional)
- `edge/LLM_README.md` has full training + export instructions, including temporal baselines.

## License
See `LICENSE`.
