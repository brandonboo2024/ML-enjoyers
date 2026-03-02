# Prototype: Fall Detection Hackathon Stack

This prototype implements a minimal end‑to‑end flow aligned with `fall_detection_plan.md`:
- **Edge device** (Python) runs mic inference (with optional simulation) and posts metadata-only alerts.
- **Backend** (JavaScript/Node) receives alerts and stores them in memory.
- **Frontend** (TypeScript/Vite) displays alerts and supports acknowledgements.

## 1) Backend (JavaScript)
Location: `backend/`

### Run
```
cd backend
npm install
npm run dev
```

Backend runs at: `http://localhost:4100`

### Endpoints
- `GET /health`
- `GET /api/alerts`
- `POST /api/alerts`
- `POST /api/ack/:id`

## 2) Frontend (TypeScript)
Location: `frontend/`

### Run
```
cd frontend
npm install
npm run dev
```

Frontend runs at: `http://localhost:5173`

## 3) Edge Device (Python)
Location: `edge/`

### Run once (mic)
```
python3 edge/edge_device.py --model edge/llm_artifacts/model.tflite --once
```

### Run continuous (mic)
```
python3 edge/edge_device.py --model edge/llm_artifacts/model.tflite
```

### Run simulated (no mic)
```
python3 edge/edge_device.py --simulate --once --model edge/llm_artifacts/model.tflite
```

## Notes
- This is a **prototype** for hackathon demo and a foundation for broader public safety events.
- Backend uses in‑memory storage (no database) for speed.

## Low-Connectivity Demo (Option C + D)
Run edge in offline demo mode (prints alerts without sending):
```
python3 edge/edge_device.py --model edge/llm_artifacts/model.tflite --dry-run
```

Confirm the payload only includes metadata (no raw audio).

## Planned Demo Extensions
- **Location**: start with static labels; optional Wi‑Fi/BSSID mapping for room-level labels.
- **Transport**: standardize values (`edge`, `wifi`, `cell`, `lorawan`, `offline`) and display in UI.
- **Queue status**: show queued count and last flush time for low-connectivity awareness.
