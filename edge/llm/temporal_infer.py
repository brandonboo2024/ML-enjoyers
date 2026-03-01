import argparse
import json
from pathlib import Path

import numpy as np

from .config import LLMConfig
from .features import load_audio, rms_normalize
from .temporal_features import extract_temporal_features
from .temporal_models import rule_score, score_markov


def _load_norm(norm_path: Path):
    if not norm_path.exists():
        return None
    data = np.load(norm_path, allow_pickle=True).item()
    return data["mean"], data["std"]


def main() -> int:
    parser = argparse.ArgumentParser(description="Temporal inference for fall detection.")
    parser.add_argument("--mode", choices=["rule", "markov", "gru"], required=True)
    parser.add_argument("--model", help="Path to model file (markov json or tflite).")
    parser.add_argument("--audio", required=True, help="Path to audio file")
    parser.add_argument("--threshold", type=float, default=0.6)
    parser.add_argument(
        "--use-tf",
        action="store_true",
        help="Force TensorFlow interpreter (required for Select TF ops).",
    )
    args = parser.parse_args()

    cfg = LLMConfig()
    y = load_audio(args.audio, cfg)
    if cfg.rms_normalize:
        y = rms_normalize(y, cfg)
    features = extract_temporal_features(y, cfg)

    if args.mode == "rule":
        score = rule_score(
            features,
            quiet_threshold=cfg.post_impact_rms_threshold,
            quiet_seconds=cfg.post_impact_quiet_seconds,
            stride_seconds=cfg.hop_length / cfg.sample_rate,
        )
    elif args.mode == "markov":
        if not args.model:
            raise SystemExit("--model is required for markov mode.")
        model = json.loads(Path(args.model).read_text())
        score = score_markov(model, features)
    else:
        if not args.model:
            raise SystemExit("--model is required for gru mode.")
        norm_path = Path(args.model).with_name("temporal_norm.npy")
        norm = _load_norm(norm_path)
        if norm:
            mean, std = norm
            features = (features - mean) / std
        from .infer import _load_tflite_interpreter, _run_inference

        interpreter = _load_tflite_interpreter(args.model, prefer_tf=args.use_tf)
        x = features[np.newaxis, ...].astype(np.float32)
        score = _run_inference(interpreter, x)

    label = "fall" if score >= args.threshold else "non-fall"
    print(f"score={score:.4f} label={label}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
