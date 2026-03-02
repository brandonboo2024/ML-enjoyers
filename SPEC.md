# Public Safety Prototype — Shared Contract

This file is the **single source of truth** for the multi‑agent workflow.
All agents must follow these contracts and file ownership rules.

## 1) Architecture Contract
- Edge device (Python) runs local detection and sends **metadata-only** alerts to backend.
- Backend (Node/Express) receives alerts and serves them to frontend.
- Frontend (TypeScript/Vite) displays alerts and allows acknowledgement.

## 1a) Model / Inference Decision Note
- Primary goal: edge-first inference. Two allowable paths:
  - (A) **OpenAI API**: use API key; only send lightweight audio features or text summaries (no raw audio) if privacy allows. Must document key handling and rate limits.
  - (B) **On-device lightweight model**: train locally, export to TFLite; no API key needed; best for privacy/offline use.
- For hackathon, default to (B) if feasible; (A) allowed as a fallback/benchmark.

## 2) API Contract
Base: `http://localhost:4100`

### POST /api/alerts
**Request body (JSON)**
- `deviceId` (string)
- `eventType` (string) e.g. `fall_suspected`
- `confidence` (number, 0–1)
- `location` (string)
- `notes` (string)
- `transport` (string) e.g. `edge`, `lorawan`

**Response**
- `{ ok: true, alert: AlertItem }`

### GET /api/alerts
**Response**
- `{ items: AlertItem[] }`

### POST /api/ack/:id
**Request body**
- `by` (string)

**Response**
- `{ ok: true, alert: AlertItem }`

### AlertItem fields (returned by backend)
- `id` (string)
- `receivedAt` (ISO string)
- `deviceId`
- `eventType`
- `confidence`
- `location`
- `notes`
- `transport`
- `acknowledgedAt` (optional ISO string)
- `acknowledgedBy` (optional string)

### Location & Transport Conventions (planned)
- `location`: static device label (default) with optional Wi‑Fi/BSSID mapping.
- `transport`: use a constrained set: `edge`, `wifi`, `cell`, `lorawan`, `offline`.

## 2a) Reliability & Privacy Constraints
- Edge should operate without continuous connectivity (local inference + queue).
- Alerts are metadata-only; no raw audio is transmitted.

## 3) File Ownership Rules
- Frontend Agent: `frontend/` only
- Backend Agent: `backend/` only
- Edge/LLM Agent: `edge/` only
- Integrator: `SPEC.md`, `TASKS.md`, `INTEGRATION.md`, `CHANGELOG.md`

## 4) Non‑Goals (for hackathon prototype)
- No production auth
- No long‑term storage requirement
- No cloud deployment requirement
