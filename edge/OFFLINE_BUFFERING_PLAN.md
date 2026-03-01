# Offline Buffering + Retry Plan (No Code)

## Goal

Guarantee that edge alerts are not lost during temporary network/backend outages while avoiding duplicate alert spam.

## Buffer Model

- Use local append-only queue file (JSON Lines) under `edge/data/queue/alerts.jsonl`.
- Each queued record includes:
  - `idempotencyKey` (stable hash of deviceId + eventType + timestamp bucket + confidence)
  - full alert payload
  - `createdAt`
  - `attemptCount`
  - `nextRetryAt`

## Send Policy

- Online path:
  - Try direct POST to backend.
  - On success, do not enqueue.
  - On failure/timeout, enqueue record.
- Offline flush path:
  - Background retry loop scans due records (`now >= nextRetryAt`).
  - Send one-by-one to preserve ordering.
  - Remove on success.

## Backoff Strategy

- Exponential backoff with jitter:
  - `delay = min(base * 2^attemptCount, maxDelay) + jitter`
  - base = 2s, maxDelay = 5m, jitter = 0–1s
- Persist updated `attemptCount` and `nextRetryAt` after each failed attempt.

## De-duplication

- Prevent duplicate local records by checking `idempotencyKey` before append.
- Include `idempotencyKey` in outgoing request (header or payload note) so backend can later adopt dedupe support.

## Retention Rules

- Keep max queue size (e.g., 10k records) with warning logs when near limit.
- Keep max age (e.g., 7 days) and expire oldest entries first after export/log.

## Failure Handling

- Corrupt queue file handling:
  - move corrupt file to `alerts.corrupt.<timestamp>.jsonl`
  - start fresh queue file
  - keep process alive
- Crash safety: fsync after append/update checkpoints when practical.

## Validation Checklist

- Simulate backend down -> alerts are enqueued.
- Restore backend -> queued alerts flush successfully.
- Confirm no duplicate sends for same event.
- Confirm queue survives process restart.
- Confirm backoff timing increases as expected.
