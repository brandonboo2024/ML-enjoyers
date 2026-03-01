import argparse
import json
import random
import time
import urllib.request


def post_alert(url, payload):
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=5) as resp:
        body = resp.read().decode("utf-8")
    return body


def simulate_event(confidence_floor):
    confidence = random.uniform(confidence_floor, 0.98)
    return {
        "deviceId": "edge-audio-001",
        "eventType": "fall_suspected",
        "confidence": confidence,
        "location": "living-room",
        "notes": "Simulated impact + silence pattern",
        "transport": "edge",
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--endpoint", default="http://localhost:4000/api/alerts")
    parser.add_argument("--interval", type=int, default=20)
    parser.add_argument("--confidence-floor", type=float, default=0.75)
    parser.add_argument("--once", action="store_true")
    args = parser.parse_args()

    while True:
        payload = simulate_event(args.confidence_floor)
        try:
            result = post_alert(args.endpoint, payload)
            print("Alert sent:", result)
        except Exception as exc:
            print("Failed to send alert:", exc)

        if args.once:
            break

        time.sleep(args.interval)


if __name__ == "__main__":
    main()
