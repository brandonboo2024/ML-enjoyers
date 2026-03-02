# Task Board — Multi‑Agent Workflow

Each agent owns a lane and reports status in this file.
Format: `[owner] [status] task` where status is TODO | DOING | DONE.
Keep tasks minimal; mark DOING when in progress and DONE when validated.

## Frontend Agent (frontend/)

- [frontend] DONE Improve alert card layout and status indicator
- [frontend] DONE Add simple filters (all / unacknowledged)
- [frontend] TODO Add transport and location badges + filters
- [frontend] TODO Surface queued alerts + last flush time indicator

## Backend Agent (backend/)

- [backend] DONE Add in‑memory rate‑limit to prevent alert spam
- [backend] DONE Add simple /metrics endpoint (counts)
- [backend] TODO Standardize transport values (`edge`, `wifi`, `cell`, `lorawan`, `offline`)

## Edge/LLM Agent (edge/)

- [edge] DONE Replace simulator with laptop audio capture plan (no code yet)
- [edge] DONE Add local buffering plan for offline send
- [edge] DONE Decide model path: (A) OpenAI API inference vs (B) on-device lightweight model (TFLite); document API key needs and privacy/bandwidth trade-offs
- [edge] DONE Define feature pipeline (windowing + mel-spec params) and a minimal dataset/augmentation plan for falls vs non-falls
- [edge] DONE Draft training/inference plan outline (no code): how to train locally and how to export to TFLite or call API
- [edge] TODO Document low-connectivity demo flow (dry-run + metadata-only)
- [edge] TODO Add static location config and optional Wi‑Fi/BSSID mapping

## Integrator

- [integrator] TODO Align docs with current defaults (ports, edge mode, model defaults)
- [integrator] TODO Verify compatibility and run demo
- [integrator] TODO Decide on backend idempotency handling for edge retries
- [integrator] TODO Align narrative with public safety hackathon brief
