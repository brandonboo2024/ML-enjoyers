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
- Changes: edge/LLM_README.md, edge/requirements-llm.txt, edge/llm/__init__.py, edge/llm/config.py, edge/llm/features.py, edge/llm/data.py, edge/llm/model.py, edge/llm/train.py, edge/llm/export_tflite.py, edge/llm/infer.py, edge/llm/download_dataset.py
- Why: Implemented minimal audio fall classifier pipeline (features, training, TFLite export, inference) and docs/deps.
- Run/Test: Not run (code only).
- Open: Need Kaggle credentials and dataset download to train.

[2026-03-01] [edge]
- Changes: edge/shell.nix
- Why: Provide Nix shell with Python 3.11 + ML deps to avoid large pip downloads on NixOS.
- Run/Test: Not run (config only).
- Open: None.
