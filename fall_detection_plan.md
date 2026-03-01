# Fall‑Detection for Elderly at Home — Feasibility‑First Plan

## 0) Executive Summary
An edge‑first fall‑detection system that uses **audio** (and optionally minimal extra sensors) to detect fall‑like events locally, then sends **low‑bandwidth alerts** via **LoRaWAN** with fallback to **SMS/Wi‑Fi**. The system prioritizes **privacy, reliability, and on‑device inference** to work in low‑connectivity environments.

**Core hypothesis:** A lightweight on‑device audio model with conservative thresholds and context rules can detect fall‑like events with acceptable reliability in home environments, and low‑bandwidth alerting can work consistently even under poor network conditions.

---

## 1) Feasibility & Research Rationale

### 1.1 Why audio‑first?
- Low‑cost ambient sensing with minimal hardware.
- Lower privacy risk if raw audio never leaves the device.
- Small models can recognize impact + silence + distress patterns.

### 1.2 Known limitations
- Audio ambiguity: dropped objects can mimic falls.
- Room acoustics: carpeted rooms or distance from mic degrade signal.
- Background noise: TV, kitchen, or street noise can add false triggers.

### 1.3 Mitigation strategy
- Multi‑stage detection:
  - Stage A: impact‑like event detection.
  - Stage B: fall vs non‑fall classification.
- Add contextual cues:
  - Optional PIR motion sensor or wearable IMU.
  - “Impact + silence” rule + time‑of‑day logic.
- Use conservative alert thresholds with escalation logic.

---

## 2) System Architecture Overview

### 2.1 High‑level flow
1. Audio capture (continuous, local)
2. Preprocess (feature extraction)
3. Model inference (lightweight classifier)
4. Decision layer (rules + confidence)
5. Alert transmission (LoRaWAN primary; fallback to SMS/Wi‑Fi)
6. Acknowledgement & escalation (caregiver → emergency)

### 2.2 Components
**Edge device**
- Mic input (I2S MEMS).
- Low‑power compute.
- Local queue for retries.

**Inference layer**
- Log‑mel spectrogram extraction.
- Lightweight CNN/CRNN.
- TFLite runtime.

**Alert transport**
- Primary: LoRaWAN.
- Secondary: Wi‑Fi/Cell.
- Tertiary: SMS fallback.
- Store‑and‑forward queue.

**Backend**
- Minimal ingestion endpoint.
- Event log storage.
- Notification service.
- Simple dashboard with acknowledgements.

---

## 3) Detailed Implementation Plan

### Phase 1 — Scope and success criteria (Day 0–1)
**Deliverables**
- Define “fall event” criteria (impact + inactivity + confidence ≥ X).
- Precision/recall targets.
- Alert latency requirements.
- Privacy and data handling rules.

**Decisions**
- Audio‑only vs audio + PIR/IMU.
- Target hardware for demo.
- Escalation policy.

### Phase 2 — Data strategy and research (Day 1–2)
**Tasks**
- Identify audio datasets (impact, household noise, anomalies).
- Collect/simulate fall‑like audio clips.
- Define class labels.

**Rationale**
- Fall datasets are sparse; synthetic augmentation improves feasibility.

### Phase 3 — Baseline inference (Day 2–3)
**Tasks**
- Feature extraction: log‑mel spectrogram.
- Model: small CNN.
- Validate on curated dataset.

**Metrics**
- Precision for fall‑like events.
- False positives from common household sounds.
- Inference latency.

### Phase 4 — Edge deployment (Day 3–4)
**Tasks**
- Convert to TFLite.
- Run on device; measure latency and CPU.
- Implement sliding window detection.

**Feasibility criteria**
- < 1s per window.
- CPU usage < ~40%.

### Phase 5 — Alert pipeline & reliability (Day 4–5)
**Tasks**
- Define alert packet format: timestamp, device ID, type, confidence.
- Integrate LoRaWAN.
- Add store‑and‑forward retry queue.
- Implement SMS fallback.

### Phase 6 — Decision logic & escalation (Day 5–6)
**Tasks**
- Combine model confidence + rules (silence duration, time of day, motion).
- Implement acknowledgement + escalation if no response.

### Phase 7 — Minimal dashboard & demo (Day 6–7)
**Features**
- Event feed with confidence scores.
- Alert status tracking.
- Simple timeline view.

---

## 4) Evaluation Plan

### 4.1 Accuracy evaluation
- Test against simulated falls, dropped objects, background noise.
- Track precision/recall and false alarms per hour.

### 4.2 Reliability evaluation
- Simulate weak connectivity; verify LoRaWAN + SMS fallback.
- Confirm store‑and‑forward under network loss.

### 4.3 User acceptance
- Minimize false alarms.
- Provide confidence + clear alert details.

---

## 5) Risk Matrix & Mitigation

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| False positives (dropped objects) | High | Medium | Add silence + motion cue; conservative threshold |
| Missed soft falls | Medium | High | Sensitivity tuning + multi‑sensor |
| LoRaWAN payload limits | Medium | Low | Send metadata only |
| Background noise | High | Medium | Noise profiling + calibration |
| Privacy concerns | Medium | High | No raw audio leaves device |

---

## 6) Recommended Languages & Tech Stack

### Edge device
- **Language**: Python (rapid prototyping) or C++ (performance)
- **Inference**: TensorFlow Lite (TFLite)
- **Audio processing**: Python + NumPy/Librosa (prototype), then optimize

### Microcontroller (if used)
- **Language**: C/C++
- **Inference**: TFLite Micro

### Backend
- **Language**: Python (FastAPI) or Node.js (Express)
- **Database**: SQLite (demo) or PostgreSQL
- **Messaging**: MQTT for event ingestion
- **SMS**: Twilio or GSM module

### Frontend/dashboard
- **Language**: TypeScript
- **Framework**: React or Vue
- **Charts**: lightweight chart library

### Connectivity
- **LoRaWAN**: RFM95 + gateway
- **Fallback**: Wi‑Fi/Cell + SMS

---

## 7) Codex & Agent Workflow Suggestions

### Ways to use Codex effectively
- Summarize fall‑detection research and dataset availability.
- Draft architecture diagrams and alert schemas.
- Critique detection logic and false‑alarm risks.
- Produce demo scripts and evaluation checklists.
- Generate backlog and acceptance criteria.

### Suggested agent roles
- **Research Agent**: datasets and related work survey
- **Systems Agent**: architecture, data flow, alert pipeline
- **ML Agent**: model size and latency estimates
- **Demo Agent**: demo script + evaluation checklist
- **Risk Agent**: privacy and ethics assessment

---

## 8) Hackathon Timeline (7‑day example)

**Day 1**: scope, success metrics, hardware target

**Day 2**: datasets + synthetic augmentation

**Day 3**: baseline model + evaluation

**Day 4**: edge deployment + latency tests

**Day 5**: LoRaWAN + alert pipeline

**Day 6**: decision logic + escalation

**Day 7**: demo + dashboard

---

## 9) Feasible Success Criteria
- Precision ≥ 80% in controlled tests.
- Alerts delivered within 30–60 seconds.
- Works without continuous internet.
- No raw audio transmission.
