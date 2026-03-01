# Workflow Guide (Codex Multi-Agent Setup)

This guide keeps the repo tidy and clarifies how to run role-based agents.

## Quick Start
1) Read `SPEC.md` (contract) and `TASKS.md` (assignments).
2) Open separate Codex sessions per role:
   - Frontend Agent: `cd frontend`
   - Backend Agent: `cd backend`
   - Edge/LLM Agent: `cd edge`
   - Integrator: stay at repo root
3) Each agent edits **only its folder** and logs updates to `CHANGELOG.md` using the template below.
4) Integrator reconciles changes, updates `SPEC.md` if needed, and keeps `TASKS.md` current.

## Running the Prototype (for demos)
- Backend: `cd backend && npm install && npm run dev` (http://localhost:4000)
- Frontend: `cd frontend && npm install && npm run dev` (http://localhost:5173)
- Edge simulator: `python3 edge/edge_device.py --once` (or `--interval 20`)

## Files That Matter
- `SPEC.md` — API & ownership contract
- `TASKS.md` — current assignments
- `CHANGELOG.md` — agent updates (see template below)
- `PROTOTYPE.md` — how the demo pieces fit together
- `fall_detection_plan.md` — feasibility & system plan

## Ground Rules
- Don’t edit outside your folder unless you’re the Integrator.
- Use the shared payload schema; don’t silently change it.
- If you need a cross-cutting change, note it in `CHANGELOG.md` for the Integrator.
- Keep instructions concise—this file is the navigation map.

## Handoff Template (add to CHANGELOG.md)
```
[YYYY-MM-DD] [agent-name]
- Changes: <paths touched>
- Why: <short rationale>
- Run/Test: <commands run or not run>
- Open: <questions or follow-ups>
```

## Conflict Policy
- If changes overlap, Integrator decides.
- Agents should not edit files they don’t own.
- Cross-cutting changes must be flagged in `CHANGELOG.md`.
