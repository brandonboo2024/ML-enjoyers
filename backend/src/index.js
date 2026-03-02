import express from "express";
import cors from "cors";
import crypto from "crypto";

const app = express();
const port = process.env.PORT || 4100;

app.use(cors());
app.use(express.json());

const alerts = [];
// In-memory rate limiter keyed by deviceId.
const rateLimitWindowMs = Number(process.env.ALERT_RATE_WINDOW_MS ?? 60_000);
const rateLimitMax = Number(process.env.ALERT_RATE_MAX ?? 10);
const rateLimits = new Map();

function nowIso() {
  return new Date().toISOString();
}

function checkRateLimit(key) {
  // Simple fixed window rate limiter.
  const now = Date.now();
  const entry = rateLimits.get(key);

  if (!entry || now - entry.windowStart >= rateLimitWindowMs) {
    rateLimits.set(key, { windowStart: now, count: 1 });
    return { allowed: true, resetAt: now + rateLimitWindowMs };
  }

  if (entry.count >= rateLimitMax) {
    return { allowed: false, resetAt: entry.windowStart + rateLimitWindowMs };
  }

  entry.count += 1;
  return { allowed: true, resetAt: entry.windowStart + rateLimitWindowMs };
}

app.get("/health", (req, res) => {
  res.json({ status: "ok", time: nowIso() });
});

app.get("/metrics", (req, res) => {
  const total = alerts.length;
  const acknowledged = alerts.filter((alert) => alert.acknowledgedAt).length;
  res.json({
    totalAlerts: total,
    acknowledgedAlerts: acknowledged,
    unacknowledgedAlerts: total - acknowledged,
  });
});

app.get("/api/alerts", (req, res) => {
  res.json({ items: alerts.slice().reverse() });
});

app.post("/api/alerts", (req, res) => {
  const payload = req.body || {};
  const deviceId = payload.deviceId || "unknown-device";
  const limit = checkRateLimit(deviceId);
  if (!limit.allowed) {
    const retryAfterMs = Math.max(0, limit.resetAt - Date.now());
    return res.status(429).json({
      ok: false,
      error: "Rate limit exceeded",
      retryAfterMs,
    });
  }

  const alert = {
    id: crypto.randomUUID(),
    receivedAt: nowIso(),
    deviceId,
    eventType: payload.eventType || "fall_suspected",
    confidence: Number(payload.confidence ?? 0),
    location: payload.location || "unknown",
    notes: payload.notes || "",
    transport: payload.transport || "edge",
  };

  alerts.push(alert);

  res.status(201).json({ ok: true, alert });
});

app.post("/api/ack/:id", (req, res) => {
  const { id } = req.params;
  const alert = alerts.find((a) => a.id === id);
  if (!alert) {
    return res.status(404).json({ ok: false, error: "Not found" });
  }
  alert.acknowledgedAt = nowIso();
  alert.acknowledgedBy = req.body?.by || "caregiver";
  res.json({ ok: true, alert });
});

app.listen(port, () => {
  console.log(`Backend listening on http://localhost:${port}`);
});
