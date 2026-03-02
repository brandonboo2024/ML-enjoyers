#set page(margin: (top: 1in, bottom: 1in, left: 1in, right: 1in))
#set text(font: "IBM Plex Sans", size: 11pt)
#set heading(numbering: "1.")

= ML-enjoyers: Edge-First Public Safety Alerts

*Submission Summary (Hackathon 2026)*

== Executive Summary
ML-enjoyers is a lightweight, edge-first public safety system focused on fast, privacy‑preserving alerts. We start with fall detection—one of the most urgent home safety incidents—and deliver low‑bandwidth, metadata‑only alerts to a simple dashboard. The system runs locally, queues alerts when connectivity is poor, and supports acknowledgement so responders can act quickly and confidently.

== The Opportunity
Many communities rely on delayed reporting or fragmented safety infrastructure. The result is slow intervention for preventable incidents. Our goal is to show that high‑quality safety alerts can be delivered without cloud dependency, heavy hardware, or invasive surveillance.

== What We Built
The prototype connects three lightweight pieces:
- **Edge device**: microphone capture, on‑device inference, and local alert queue.
- **Backend API**: minimal ingestion + acknowledgement flow.
- **Dashboard**: clear alert feed with confidence, status, and rapid acknowledge tools.

Alerts contain only metadata (time, location label, confidence, transport). No raw audio leaves the device.

== How It Works (At a Glance)
We use a compact CNN over log‑mel spectrograms with a post‑impact quiet rule. The model runs at 8 kHz with 3‑second windows to stay fast and small. A local queue ensures alerts still move once connectivity returns.

== Demo Highlights
- Real‑time detection → alert appears on the dashboard.
- One‑click acknowledge moves alerts into a resolved pool.
- Low‑connectivity mode shows queued alerts without sending raw data.

== Data & Model Notes
We use the SAFE fall dataset as a baseline and plan to add “hard negatives” (door slams, chair scrapes, book drops) to reduce false positives. We also record ambient audio for domain alignment to real microphones.

== Why This Matters
This project focuses on **practical deployment**: small models, low bandwidth, offline resilience, and privacy by design. It provides a realistic path for communities that can’t rely on constant connectivity or expensive infrastructure.

== Roadmap
Short‑term:
- Add location labeling (static + Wi‑Fi/BSSID map).
- Standardize transport tagging (edge/wifi/cell/lorawan/offline).
- Surface queue status in the UI.

Long‑term:
- Extend to other safety events (glass break, distress sounds).
- Multi‑sensor fusion for better precision.

== Repository Pointers
- README.md (quick start + demo runbook)
- SPEC.md (API contract + privacy constraints)
- PROTOTYPE.md (system flow + demo details)
- edge/LLM_README.md (training + variants)
