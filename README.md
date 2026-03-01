# ML-enjoyers

LLM-based project that helps detect sound changes.

## Overview
Edge-first fall detection prototype with:
- Python edge (simulated now)
- Node backend API
- TypeScript/Vite frontend dashboard

## Start Here
- `WORKFLOW.md` — how to run the multi-agent process
- `SPEC.md` — API & ownership contract
- `TASKS.md` — assignments by role
- `CHANGELOG.md` — agent updates (use template in WORKFLOW)
- `PROTOTYPE.md` — how the demo pieces fit together
- `fall_detection_plan.md` — feasibility plan

## Run Prototype
- Backend: `cd backend && npm install && npm run dev` (http://localhost:4100)
- Frontend: `cd frontend && npm install && npm run dev` (http://localhost:5173)
- Edge detector: `python3 edge/edge_device.py --model edge/llm_artifacts/model.tflite`

## License
See `LICENSE`.
