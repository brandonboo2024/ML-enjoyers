import argparse
import hashlib
import json
import os
import random
import shutil
import sys
import time
import urllib.request
from collections import deque
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

import numpy as np

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from edge.llm.config import LLMConfig
from edge.llm.features import extract_log_mel, normalize_log_mel, rms_normalize, rms_level


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _parse_iso_to_epoch(value: str) -> float:
    return datetime.fromisoformat(value).timestamp()


def _load_tflite_interpreter(model_path: str):
    try:
        from tflite_runtime.interpreter import Interpreter
    except ImportError:
        import tensorflow as tf

        Interpreter = tf.lite.Interpreter

    interpreter = Interpreter(model_path=model_path)
    interpreter.allocate_tensors()
    return interpreter


def _run_inference(interpreter, x: np.ndarray) -> float:
    input_details = interpreter.get_input_details()
    output_details = interpreter.get_output_details()
    input_index = input_details[0]["index"]
    output_index = output_details[0]["index"]

    if input_details[0]["dtype"] == np.int8:
        scale, zero_point = input_details[0]["quantization"]
        x = x / scale + zero_point
        x = np.clip(x, -128, 127).astype(np.int8)

    interpreter.set_tensor(input_index, x)
    interpreter.invoke()
    output = interpreter.get_tensor(output_index)

    if output_details[0]["dtype"] == np.int8:
        scale, zero_point = output_details[0]["quantization"]
        output = (output.astype(np.float32) - zero_point) * scale

    return float(output.squeeze())


def post_alert(
    url: str, payload: dict, idempotency_key: str, timeout_seconds: int = 5
) -> str:
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=data,
        headers={
            "Content-Type": "application/json",
            "X-Idempotency-Key": idempotency_key,
        },
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=timeout_seconds) as resp:
        body = resp.read().decode("utf-8")
    return body


def _build_idempotency_key(
    payload: dict, event_time_epoch: float, bucket_seconds: int = 5
) -> str:
    bucket = int(event_time_epoch // bucket_seconds)
    key_payload = {
        "deviceId": payload.get("deviceId"),
        "eventType": payload.get("eventType"),
        "location": payload.get("location"),
        "bucket": bucket,
        "confidence": round(float(payload.get("confidence", 0.0)), 3),
    }
    raw = json.dumps(key_payload, sort_keys=True)
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


@dataclass
class QueueRecord:
    idempotencyKey: str
    payload: dict
    createdAt: str
    attemptCount: int
    nextRetryAt: str


class AlertQueue:
    def __init__(self, queue_path: str, max_items: int = 10_000):
        self.queue_path = Path(queue_path)
        self.max_items = max_items
        self.queue_path.parent.mkdir(parents=True, exist_ok=True)
        self.records = self._load_records()

    def _load_records(self) -> list[QueueRecord]:
        if not self.queue_path.exists():
            return []

        records: list[QueueRecord] = []
        try:
            with self.queue_path.open("r", encoding="utf-8") as handle:
                for line in handle:
                    line = line.strip()
                    if not line:
                        continue
                    obj = json.loads(line)
                    records.append(
                        QueueRecord(
                            idempotencyKey=obj["idempotencyKey"],
                            payload=obj["payload"],
                            createdAt=obj["createdAt"],
                            attemptCount=int(obj.get("attemptCount", 0)),
                            nextRetryAt=obj.get("nextRetryAt", obj["createdAt"]),
                        )
                    )
        except Exception:
            stamp = datetime.now().strftime("%Y%m%d%H%M%S")
            corrupt_path = self.queue_path.with_suffix(
                self.queue_path.suffix + f".corrupt.{stamp}"
            )
            shutil.move(self.queue_path, corrupt_path)
            return []

        return records

    def _persist(self) -> None:
        tmp_path = self.queue_path.with_suffix(self.queue_path.suffix + ".tmp")
        with tmp_path.open("w", encoding="utf-8") as handle:
            for item in self.records:
                handle.write(
                    json.dumps(
                        {
                            "idempotencyKey": item.idempotencyKey,
                            "payload": item.payload,
                            "createdAt": item.createdAt,
                            "attemptCount": item.attemptCount,
                            "nextRetryAt": item.nextRetryAt,
                        }
                    )
                    + "\n"
                )
        os.replace(tmp_path, self.queue_path)

    def enqueue(self, idempotency_key: str, payload: dict) -> None:
        if any(item.idempotencyKey == idempotency_key for item in self.records):
            return

        now_iso = _utc_now_iso()
        self.records.append(
            QueueRecord(
                idempotencyKey=idempotency_key,
                payload=payload,
                createdAt=now_iso,
                attemptCount=0,
                nextRetryAt=now_iso,
            )
        )

        if len(self.records) > self.max_items:
            self.records = self.records[-self.max_items :]

        self._persist()

    def flush_due(self, endpoint: str, timeout_seconds: int = 5) -> tuple[int, int]:
        now_epoch = time.time()
        sent_count = 0
        failed_count = 0
        kept: list[QueueRecord] = []

        for record in self.records:
            next_retry_epoch = _parse_iso_to_epoch(record.nextRetryAt)
            if now_epoch < next_retry_epoch:
                kept.append(record)
                continue

            try:
                post_alert(
                    endpoint,
                    record.payload,
                    idempotency_key=record.idempotencyKey,
                    timeout_seconds=timeout_seconds,
                )
                sent_count += 1
            except Exception:
                record.attemptCount += 1
                base_delay = 2.0
                max_delay = 300.0
                jitter = random.uniform(0.0, 1.0)
                delay = min(base_delay * (2**record.attemptCount), max_delay) + jitter
                record.nextRetryAt = datetime.fromtimestamp(
                    now_epoch + delay, tz=timezone.utc
                ).isoformat()
                kept.append(record)
                failed_count += 1

        if sent_count or failed_count:
            self.records = kept
            self._persist()

        return sent_count, failed_count


def simulate_chunk(cfg: LLMConfig, confidence_floor: float) -> tuple[np.ndarray, float]:
    confidence = random.uniform(confidence_floor, 0.98)
    # Creates a synthetic "impact" shape for dry-run fallback.
    y = np.random.normal(0.0, 0.01, int(cfg.sample_rate * cfg.clip_seconds)).astype(
        np.float32
    )
    impact_index = random.randint(int(0.4 * len(y)), int(0.7 * len(y)))
    y[impact_index : impact_index + 200] += np.random.normal(0.2, 0.05, 200).astype(
        np.float32
    )
    y = np.clip(y, -1.0, 1.0)
    return y, confidence


def _build_alert_payload(
    device_id: str, location: str, confidence: float, model_path: str
) -> dict:
    return {
        "deviceId": device_id,
        "eventType": "fall_suspected",
        "confidence": float(confidence),
        "location": location,
        "notes": f"audio_model={Path(model_path).name}",
        "transport": "edge",
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Edge audio fall detection loop with offline queue."
    )
    parser.add_argument("--endpoint", default="http://localhost:4100/api/alerts")
    parser.add_argument("--model", default="edge/llm_artifacts/model.tflite")
    parser.add_argument("--queue-path", default="edge/data/queue/alerts.jsonl")
    parser.add_argument("--device-id", default="edge-audio-001")
    parser.add_argument("--location", default="living-room")
    parser.add_argument("--input-device", default=None)
    parser.add_argument("--threshold", type=float, default=None)
    parser.add_argument("--cooldown-seconds", type=float, default=None)
    parser.add_argument("--window-stride-seconds", type=float, default=0.5)
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Do not send alerts; print detections only.",
    )
    parser.add_argument(
        "--simulate",
        action="store_true",
        help="Use synthetic audio instead of microphone input.",
    )
    parser.add_argument("--confidence-floor", type=float, default=0.75)
    parser.add_argument("--once", action="store_true")
    args = parser.parse_args()

    cfg = LLMConfig()
    trigger_threshold = (
        cfg.trigger_threshold if args.threshold is None else args.threshold
    )
    cooldown_seconds = (
        cfg.cooldown_seconds if args.cooldown_seconds is None else args.cooldown_seconds
    )

    queue = AlertQueue(args.queue_path)
    interpreter = _load_tflite_interpreter(args.model)

    target_samples = int(cfg.sample_rate * cfg.clip_seconds)
    stride_samples = max(1, int(cfg.sample_rate * args.window_stride_seconds))
    sample_buffer = np.zeros(target_samples, dtype=np.float32)
    filled_samples = 0
    score_window: deque[float] = deque(maxlen=cfg.smooth_window)
    last_trigger_epoch = 0.0

    if not args.simulate:
        try:
            import sounddevice as sd
        except ImportError as exc:
            raise SystemExit(
                "sounddevice is required for microphone mode. Install it or run with --simulate."
            ) from exc

        stream = sd.InputStream(
            samplerate=cfg.sample_rate,
            channels=1,
            dtype="float32",
            blocksize=stride_samples,
            device=args.input_device,
        )
        stream.start()
    else:
        stream = None

    print(
        f"Edge detector started | endpoint={args.endpoint} | threshold={trigger_threshold:.2f} | "
        f"cooldown={cooldown_seconds:.1f}s | simulate={args.simulate}"
    )

    try:
        while True:
            sent, failed = queue.flush_due(args.endpoint)
            if sent:
                print(f"Flushed queued alerts: sent={sent}")
            if failed:
                print(f"Queued alerts retry deferred: failed={failed}")

            if args.simulate:
                chunk, simulated_confidence = simulate_chunk(cfg, args.confidence_floor)
                # Simulated mode feeds full windows directly.
                sample_buffer = chunk
                filled_samples = target_samples
            else:
                chunk, _ = stream.read(stride_samples)
                chunk = np.asarray(chunk, dtype=np.float32).reshape(-1)
                if len(chunk) >= target_samples:
                    sample_buffer = chunk[-target_samples:]
                    filled_samples = target_samples
                else:
                    shift = len(chunk)
                    sample_buffer = np.roll(sample_buffer, -shift)
                    sample_buffer[-shift:] = chunk
                    filled_samples = min(target_samples, filled_samples + shift)

            if filled_samples < target_samples:
                continue

            if args.simulate:
                score = simulated_confidence
            else:
                if cfg.silence_gate:
                    level = rms_level(sample_buffer)
                    if level < cfg.silence_rms_threshold:
                        score = 0.0
                        score_window.append(score)
                        smooth_score = float(np.mean(score_window))
                        now_epoch = time.time()
                        cooldown_ok = (now_epoch - last_trigger_epoch) >= cooldown_seconds
                        print(f"score={score:.4f} smooth={smooth_score:.4f} (silence gate)")
                        time.sleep(args.window_stride_seconds)
                        if args.once:
                            break
                        continue
                if cfg.rms_normalize:
                    sample_buffer = rms_normalize(sample_buffer, cfg)
                log_mel = extract_log_mel(sample_buffer, cfg)
                log_mel = normalize_log_mel(log_mel)
                x = log_mel[np.newaxis, ..., np.newaxis].astype(np.float32)
                score = _run_inference(interpreter, x)

            score_window.append(score)
            smooth_score = float(np.mean(score_window))
            now_epoch = time.time()
            cooldown_ok = (now_epoch - last_trigger_epoch) >= cooldown_seconds

            print(f"score={score:.4f} smooth={smooth_score:.4f}")

            if smooth_score >= trigger_threshold and cooldown_ok:
                payload = _build_alert_payload(
                    args.device_id, args.location, smooth_score, args.model
                )
                idempotency_key = _build_idempotency_key(payload, now_epoch)

                if args.dry_run:
                    print("Dry-run detection:", json.dumps(payload))
                else:
                    try:
                        result = post_alert(
                            args.endpoint, payload, idempotency_key=idempotency_key
                        )
                        print("Alert sent:", result)
                    except Exception as exc:
                        queue.enqueue(idempotency_key, payload)
                        print("Send failed; queued locally:", exc)

                last_trigger_epoch = now_epoch

                if args.once:
                    break

            if args.simulate:
                time.sleep(args.window_stride_seconds)

    finally:
        if stream is not None:
            stream.stop()
            stream.close()

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
