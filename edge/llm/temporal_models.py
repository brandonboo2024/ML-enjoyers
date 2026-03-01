import json
from pathlib import Path

import numpy as np


def _kmeans(x: np.ndarray, k: int, seed: int, iters: int = 25) -> np.ndarray:
    """Lightweight k-means for discretizing temporal features."""
    rng = np.random.default_rng(seed)
    indices = rng.choice(len(x), size=k, replace=False)
    centers = x[indices].copy()
    for _ in range(iters):
        dists = np.sum((x[:, None, :] - centers[None, :, :]) ** 2, axis=2)
        labels = np.argmin(dists, axis=1)
        for idx in range(k):
            mask = labels == idx
            if np.any(mask):
                centers[idx] = x[mask].mean(axis=0)
    return centers


def _quantize(features: np.ndarray, centers: np.ndarray) -> np.ndarray:
    """Assign each feature vector to its nearest cluster center."""
    dists = np.sum((features[:, None, :] - centers[None, :, :]) ** 2, axis=2)
    return np.argmin(dists, axis=1)


def train_markov(
    sequences: np.ndarray,
    labels: np.ndarray,
    out_dir: Path,
    seed: int,
    k: int = 8,
    smoothing: float = 1.0,
) -> None:
    """Train a class-conditional Markov model over discretized feature sequences."""
    out_dir.mkdir(parents=True, exist_ok=True)
    all_frames = sequences.reshape(-1, sequences.shape[-1])
    mean = all_frames.mean(axis=0)
    std = all_frames.std(axis=0) + 1e-6
    norm_sequences = (sequences - mean) / std

    centers = _kmeans(norm_sequences.reshape(-1, norm_sequences.shape[-1]), k, seed)
    class_models = {}

    for cls in (0, 1):
        cls_indices = np.where(labels == cls)[0]
        start_counts = np.full(k, smoothing, dtype=np.float64)
        trans_counts = np.full((k, k), smoothing, dtype=np.float64)
        for idx in cls_indices:
            seq = _quantize(norm_sequences[idx], centers)
            start_counts[seq[0]] += 1
            for i in range(len(seq) - 1):
                trans_counts[seq[i], seq[i + 1]] += 1
        start_probs = start_counts / start_counts.sum()
        trans_probs = trans_counts / trans_counts.sum(axis=1, keepdims=True)
        class_models[str(cls)] = {
            "start_probs": start_probs.tolist(),
            "trans_probs": trans_probs.tolist(),
        }

    model = {
        "centers": centers.tolist(),
        "mean": mean.tolist(),
        "std": std.tolist(),
        "k": k,
        "classes": class_models,
    }
    (out_dir / "markov_model.json").write_text(json.dumps(model))


def score_markov(model: dict, features: np.ndarray) -> float:
    """Compute fall probability from class-conditional sequence likelihoods."""
    centers = np.array(model["centers"], dtype=np.float32)
    mean = np.array(model["mean"], dtype=np.float32)
    std = np.array(model["std"], dtype=np.float32)
    features = (features - mean) / std
    seq = _quantize(features, centers)

    def loglik(cls_key: str) -> float:
        start_probs = np.array(model["classes"][cls_key]["start_probs"])
        trans_probs = np.array(model["classes"][cls_key]["trans_probs"])
        logp = np.log(start_probs[seq[0]] + 1e-12)
        for i in range(len(seq) - 1):
            logp += np.log(trans_probs[seq[i], seq[i + 1]] + 1e-12)
        return float(logp)

    ll_fall = loglik("1")
    ll_non = loglik("0")
    exp_fall = np.exp(ll_fall - max(ll_fall, ll_non))
    exp_non = np.exp(ll_non - max(ll_fall, ll_non))
    return float(exp_fall / (exp_fall + exp_non))


def rule_score(
    features: np.ndarray,
    quiet_threshold: float,
    quiet_seconds: float,
    stride_seconds: float,
    impact_ratio_target: float = 3.0,
) -> float:
    """Heuristic score based on impact ratio and post-impact quiet window."""
    rms = features[:, 0]
    peak_idx = int(np.argmax(rms))
    peak = float(rms[peak_idx])
    median = float(np.median(rms))
    impact_ratio = peak / (median + 1e-9)

    quiet_frames = max(1, int(quiet_seconds / stride_seconds))
    start = min(len(rms), peak_idx + 1)
    end = min(len(rms), start + quiet_frames)
    if end <= start:
        quiet_ok = False
    else:
        quiet_ok = float(np.mean(rms[start:end])) < quiet_threshold

    impact_score = min(1.0, impact_ratio / impact_ratio_target)
    return float(impact_score) if quiet_ok else 0.0
