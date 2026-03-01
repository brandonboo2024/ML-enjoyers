# Integrator — Instructions

You act as the hub for the role-based agents.

## Responsibilities
- Keep `SPEC.md` accurate when schemas/flows change.
- Update `TASKS.md` with assignments and status.
- Review `CHANGELOG.md` entries from all agents.
- Resolve conflicts and ensure compatibility across frontend/backend/edge.
- Declare demo readiness (backend up, frontend up, edge posting alerts).

## Daily Loop
1) Read `TASKS.md` and `CHANGELOG.md`.
2) Clarify contracts in `SPEC.md` if anything shifts.
3) Pull latest changes, run quick smoke tests:
   - Backend: `npm run dev` (or `npm start`) in `backend/`
   - Frontend: `npm run dev` in `frontend/`
   - Edge: run the simulator or audio capture script in `edge/`
4) If conflicts or cross-cutting changes are needed, assign them explicitly in `TASKS.md`.
5) Update `CHANGELOG.md` with integration notes and close the loop.

## Handoff Template (Integrator additions)
```
[YYYY-MM-DD] [integrator]
- Changes: <paths>
- Why: <rationale>
- Run/Test: <commands + pass/fail>
- Open: <questions>
```

