# Task Board — Multi‑Agent Workflow

Each agent owns a lane and reports status in this file.
Format: `[owner] [status] task` where status is TODO | DOING | DONE.
Keep tasks minimal; mark DOING when in progress and DONE when validated.

## Frontend Agent (frontend/)
- [frontend] TODO Improve alert card layout and status indicator
- [frontend] TODO Add simple filters (all / unacknowledged)

## Backend Agent (backend/)
- [backend] TODO Add in‑memory rate‑limit to prevent alert spam
- [backend] TODO Add simple /metrics endpoint (counts)

## Edge/LLM Agent (edge/)
- [edge] TODO Replace simulator with laptop audio capture plan (no code yet)
- [edge] TODO Add local buffering plan for offline send
- [edge] TODO Decide model path: (A) OpenAI API inference vs (B) on-device lightweight model (TFLite); document API key needs and privacy/bandwidth trade-offs
- [edge] TODO Define feature pipeline (windowing + mel-spec params) and a minimal dataset/augmentation plan for falls vs non-falls
- [edge] TODO Draft training/inference plan outline (no code): how to train locally and how to export to TFLite or call API

## Integrator
- [integrator] TODO Keep SPEC.md updated
- [integrator] TODO Verify compatibility and run demo
