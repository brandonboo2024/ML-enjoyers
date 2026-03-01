# Laptop Audio Capture Plan (No Code)

## Goal

Replace simulator-first testing with a laptop microphone capture workflow that feeds the same feature pipeline used by the TFLite classifier.

## Scope

- Plan only (no implementation in this step).
- Keep payload contract unchanged from `SPEC.md`.
- Work from local microphone input on macOS/Linux/Windows.

## Capture Strategy

- Capture mono audio at 16 kHz to match model training settings.
- Use a rolling buffer of 2.0 seconds with 0.5 second stride.
- For each window:
  - apply normalization/preprocessing
  - compute log-mel features
  - run model inference
  - apply smoothing + threshold + cooldown

## Runtime Flow

1. Initialize microphone stream (single input device selected by CLI arg).
2. Continuously append incoming frames to ring buffer.
3. Every 0.5 seconds, materialize latest 2.0-second window.
4. Run inference and temporal smoothing.
5. If trigger threshold and cooldown conditions are met, emit `fall_suspected` alert payload.
6. Send payload immediately if backend reachable, otherwise pass to local buffer queue.

## Configuration Surface

- `--device-id`: aligns with backend alert payload.
- `--location`: room label included in notes/location.
- `--model`: TFLite model path.
- `--threshold`: inference trigger threshold.
- `--cooldown-seconds`: anti-spam delay between alerts.
- `--input-device` (optional): microphone selection index/name.

## Safety / UX Notes

- Start with conservative threshold to reduce false positives in noisy environments.
- Expose a dry-run mode that logs scores without sending alerts.
- Include model version in `notes` for traceability during demos.

## Validation Checklist

- Confirm microphone capture works at 16 kHz.
- Confirm rolling window cadence (2.0s context / 0.5s stride).
- Confirm payload fields match `SPEC.md`.
- Confirm cooldown suppresses repeat alerts.
- Confirm offline buffering path activates when backend is unavailable.
