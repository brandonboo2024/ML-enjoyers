# Integration Guide — Hub‑and‑Spoke Workflow

This project uses a **manual agent hub** (Integrator) that coordinates updates across role‑focused sessions.
Agents do **not** communicate automatically; they coordinate through files in this repo.

## 1) Workflow Overview
1. Integrator updates `SPEC.md` and `TASKS.md`.
2. Each agent works only in its owned folder.
3. Agents report changes + notes back in `CHANGELOG.md`.
4. Integrator verifies compatibility and updates tasks.

## 2) Agent Handoff Format (required)
Each agent appends a block to `CHANGELOG.md` using this template:

```
[YYYY-MM-DD] [agent-name]
- Changes: <paths touched>
- Why: <short rationale>
- Run/Test: <commands run or not run>
- Open: <questions or follow-ups>
```

## 3) Conflict Rules
- If changes overlap across lanes, Integrator decides.
- Agents should not edit files they don’t own.
- If a cross‑cutting change is needed, raise it in `CHANGELOG.md` for Integrator.

## 4) Demo Readiness
Integrator confirms:
- Backend running
- Frontend running
- Edge device posting alerts
- UI acknowledges alerts

