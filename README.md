# ML-enjoyers

Edge-first audio fall detection prototype.

## Overview
Edge-first fall detection prototype with:
- Python edge (mic inference + offline queue)
- Node backend API
- TypeScript/Vite frontend dashboard

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

## Run Prototype
- Backend: `cd backend && npm install && npm run dev` (http://localhost:4100)
- Frontend: `cd frontend && npm install && npm run dev` (http://localhost:5173)
- Edge detector: `python3 edge/edge_device.py --model edge/llm_artifacts/model.tflite`

## Demo Runbook
1) Install backend deps: `cd backend && npm install`
2) Start backend: `cd backend && npm run dev` (keep running)
3) Install frontend deps: `cd frontend && npm install`
4) Start frontend: `cd frontend && npm run dev` (open http://localhost:5173)
5) Install edge deps: `pip install -r edge/requirements-llm.txt`
6) Run edge (mic): `python3 edge/edge_device.py --model edge/llm_artifacts/model.tflite`
7) Validate UI: alerts appear, acknowledge works, refresh updates

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
| `silence_rms_threshold` | 0.05 | Tune per environment |
| `mix_noise_prob` | 0.5 | Noise mixing for falls in training |

## License
See `LICENSE`.
