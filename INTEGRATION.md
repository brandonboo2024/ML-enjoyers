# Integration Guide — Hub‑and‑Spoke Workflow

This project uses a **manual agent hub** (Integrator) that coordinates updates across role‑focused sessions.
For full Integrator responsibilities and the daily loop, see `INTEGRATOR.md`.

## Quick Rules
- Each agent works only in its owned folder.
- Agents log updates in `CHANGELOG.md` using the standard template.
- If changes overlap across lanes, Integrator decides.

## Demo Readiness Checklist
- Backend running
- Frontend running
- Edge device posting alerts
- UI acknowledges alerts
