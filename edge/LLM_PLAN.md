# Edge/LLM Plan (No Code)

## Model Path Decision
- Primary: **On-device lightweight model (TFLite)** for privacy, offline support, lower latency, and predictable cost.
- Fallback/benchmark: **OpenAI API** using only lightweight audio features (no raw audio). Requires API key handling, rate limits, and explicit user opt-in.

## Feature Pipeline (Audio)
- Input: mono audio, 16 kHz, 16-bit PCM.
- Preprocess: optional pre-emphasis (0.97), DC offset removal, amplitude normalization.
- Framing: 25 ms window, 10 ms hop, Hann window.
- Features: 64-bin log-mel spectrogram over 0–8 kHz; optional delta + delta-delta.
- Normalization: per-clip mean/variance (or global stats from training set).
- Inference windows: 1.5–2.0 s context with 0.5 s stride; keep a rolling buffer.
- Postprocess: temporal smoothing (e.g., moving average over 3–5 windows) and hysteresis threshold to reduce false triggers.

## Minimal Dataset + Augmentation Plan
- Classes: fall vs non-fall (daily ambient sounds, speech, music, object drops, footsteps).
- Data sources: internal recordings plus the Kaggle fall audio detection dataset (antonygarciag); keep device-matched capture when possible.
- Split: subject- or session-wise train/val/test to prevent leakage.
- Augmentations (train only):
  - Additive noise (home ambience, TV, kitchen), SNR 0–20 dB.
  - Reverb/room impulse responses.
  - Time stretch (0.8–1.2), pitch shift (±2 semitones).
  - Random gain, random crop, mixup of background.

## Training Plan (Local)
- Baseline model: compact CNN over log-mel (e.g., 3–5 conv blocks + global pooling + dense).
- Loss/metrics: binary cross-entropy; track precision/recall, F1, and false-alarm rate per hour.
- Calibration: choose operating threshold to keep false positives low while maintaining recall.
- Export: convert to TFLite; apply post-training int8 quantization with a small calibration set.

## Inference Plan (Edge)
- Run streaming feature extraction + model inference on rolling windows.
- Use smoothing + cooldown (e.g., 10–20 s) after a detection to prevent alert spam.
- Emit `fall_suspected` alerts with confidence and notes about model/version.
- Buffer alerts locally when offline; retry with exponential backoff and de-duplication once connected.

## Risks / Follow-ups
- Validate that audio-only detection is sufficient; consider adding IMU later.
- Collect more true fall examples to improve recall without elevating false positives.
