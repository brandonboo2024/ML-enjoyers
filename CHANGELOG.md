# Changelog — Agent Updates

Use this file for agent handoffs and status updates.

[2026-03-01] integrator

- Changes: CHANGELOG.md
- Why: Log smoke test results and integration status check.
- Run/Test: backend `npm install`; frontend `npm install`; backend `npm run dev` (timed out after start); frontend `npm run dev` (timed out after start); edge `python3 edge/edge_device.py --once` (connection refused because backend not running).
- Open: None.

[2026-03-01] [frontend]

- Changes: frontend/index.html, frontend/src/main.ts, frontend/src/styles.css
- Why: improve alert card layout/status indicator and add all/unacknowledged filters with summary counts
- Run/Test: not run (UI changes only)
- Open: none
  [2026-03-01] [backend]
- Changes: backend/src/index.js
- Why: add in-memory alert rate limiting and a /metrics counts endpoint
- Run/Test: not run (not requested)
- Open: confirm desired rate-limit thresholds and any extra metrics fields

[2026-03-01] [backend]

- Changes: backend/src/index.js
- Why: change default backend port to 4100 to avoid 4000 conflicts; still respects PORT env var
- Run/Test: not run (requested port change only)
- Open: confirm if other components should be updated to point at 4100

[2026-03-01] [edge]

- Changes: edge/LLM_PLAN.md
- Why: Documented model path decision, feature pipeline, and training/inference plan (no code).
- Run/Test: Not run (documentation only).
- Open: Confirm if OpenAI API fallback should remain allowed for benchmark only.

[2026-03-01] [edge]

- Changes: edge/LLM_PLAN.md
- Why: Added Kaggle dataset source; confirmed OpenAI API fallback scope.
- Run/Test: Not run (documentation only).
- Open: None.

[2026-03-01] [edge]

- Changes: edge/LLM_README.md, edge/requirements-llm.txt, edge/llm/**init**.py, edge/llm/config.py, edge/llm/features.py, edge/llm/data.py, edge/llm/model.py, edge/llm/train.py, edge/llm/export_tflite.py, edge/llm/infer.py, edge/llm/download_dataset.py
- Why: Implemented minimal audio fall classifier pipeline (features, training, TFLite export, inference) and docs/deps.
- Run/Test: Not run (code only).
- Open: Need Kaggle credentials and dataset download to train.

[2026-03-01] [edge]

- Changes: edge/shell.nix
- Why: Provide Nix shell with Python 3.11 + ML deps to avoid large pip downloads on NixOS.
- Run/Test: Not run (config only).
- Open: None.

[2026-03-01] [edge]

- Changes: edge/LAPTOP_AUDIO_CAPTURE_PLAN.md, edge/OFFLINE_BUFFERING_PLAN.md, edge/LLM_README.md, edge/llm/data.py, edge/llm/train.py, edge/llm/infer.py
- Why: Completed remaining Edge planning deliverables (laptop capture and offline buffering plans), added direct `archive.zip` dataset support, added SAFE filename label mapping (`-01` fall / `-02` non-fall), and fixed TensorFlow Lite fallback import for inference.
- Run/Test: `configure_python_environment`; installed `numpy scipy librosa soundfile tensorflow`; `/usr/local/bin/python3 -m edge.llm.train --data-dir archive.zip`; `/usr/local/bin/python3 -m edge.llm.export_tflite --model edge/llm_artifacts/model.keras --out edge/llm_artifacts/model.tflite`; `/usr/local/bin/python3 -m edge.llm.export_tflite --model edge/llm_artifacts/model.keras --out edge/llm_artifacts/model_int8.tflite --int8 --calib-samples edge/llm_artifacts/calib_samples.npy`; `/usr/local/bin/python3 -m edge.llm.infer --model edge/llm_artifacts/model.tflite --audio edge/data/extracted/archive/01-020-02-073-01.wav`.
- Open: Consider adding a CLI flag to `train.py` for quick smoke training (fewer epochs) to speed iterative testing.

[2026-03-01] [edge]

- Changes: edge/edge_device.py, edge/requirements-llm.txt, TASKS.md
- Why: Replaced simulator-only edge runtime with microphone inference loop + smoothing/cooldown and persistent offline queue retry/de-duplication; added `sounddevice` dependency; audited frontend/backend completion and updated task statuses requested by user.
- Run/Test: `configure_python_environment`; installed `sounddevice`; `"/Users/alloychan/Documents/School/DLW Project/ML-enjoyers/.venv/bin/python" edge/edge_device.py --simulate --once --dry-run --model edge/llm_artifacts/model.tflite`.
- Open: Backend default port in code is `4100` while edge/frontend defaults still target `4000`; decide single default for integration.

[2026-03-01] [edge]

- Changes: edge/edge_device.py, frontend/src/main.ts
- Why: Aligned edge + frontend defaults to backend port `4100` to remove integration mismatch.
- Run/Test: `cd backend && npm run dev`; `"/Users/alloychan/Documents/School/DLW Project/ML-enjoyers/.venv/bin/python" edge/edge_device.py --simulate --once --model edge/llm_artifacts/model.tflite`; `curl -s http://localhost:4100/api/alerts`; `cd frontend && npm run dev -- --host`.
- Open: None.

[2026-03-01] [edge]

- Changes: .gitignore, README.md
- Why: Prepared repository for upload by ignoring large local dataset/artifact folders and updating run instructions to match current integrated defaults.
- Run/Test: `git status --short` (confirmed large data/artifact paths not listed).
- Open: If `archive.zip` or `edge/data` were ever committed previously, run untrack commands before pushing.
