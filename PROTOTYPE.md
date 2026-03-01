# Prototype: Fall Detection Hackathon Stack

This prototype implements a minimal end‑to‑end flow aligned with `fall_detection_plan.md`:
- **Edge device** (Python) simulates fall detections and posts alerts.
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

Backend runs at: `http://localhost:4000`

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

### Run once
```
python3 edge/edge_device.py --once
```

### Run continuous (every 20s)
```
python3 edge/edge_device.py --interval 20
```

## Notes
- This is a **prototype** for hackathon demo: alerts are simulated.
- Replace `edge_device.py` logic with real audio inference when ready.
- Backend uses in‑memory storage (no database) for speed.
