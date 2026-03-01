import os
import random
import zipfile
from dataclasses import dataclass
from pathlib import Path
from typing import List, Tuple

import numpy as np

from .config import LLMConfig
from .features import load_audio, extract_log_mel, normalize_log_mel, apply_gain, add_noise


AUDIO_EXTS = {".wav", ".flac", ".mp3", ".ogg"}


@dataclass
class LabeledFile:
    path: str
    label: int


def _contains_audio_files(path: Path) -> bool:
    if not path.exists() or not path.is_dir():
        return False
    for root, _, files in os.walk(path):
        for fname in files:
            if Path(fname).suffix.lower() in AUDIO_EXTS:
                return True
    return False


def resolve_data_dir(data_path: str) -> str:
    path = Path(data_path)
    if path.is_dir():
        return str(path)

    if path.is_file() and path.suffix.lower() == ".zip":
        extract_root = Path("edge/data/extracted")
        extract_dir = extract_root / path.stem
        if not _contains_audio_files(extract_dir):
            extract_dir.mkdir(parents=True, exist_ok=True)
            with zipfile.ZipFile(path, "r") as archive:
                archive.extractall(extract_dir)
        return str(extract_dir)

    raise ValueError(f"Unsupported dataset path: {data_path}. Provide a directory or .zip file.")


def _infer_label(path: Path) -> int | None:
    name = path.stem.lower()
    # Kaggle fall audio dataset naming: AA-BBB-CC-DDD-EE
    # CC == "00" appears to indicate non-fall, others are fall types.
    parts = name.split("-")
    if len(parts) == 5 and all(part.isdigit() for part in parts):
        if parts[2] == "00":
            return 0
        return 1

    if "nonfall" in name or "no_fall" in name or "non-fall" in name:
        return 0
    if "fall" in name:
        return 1

    # SAFE naming convention: AA-BBB-CC-DDD-FF.wav where FF is class
    # 01 => fall, 02 => non-fall
    stem_parts = path.stem.split("-")
    if stem_parts:
        class_token = stem_parts[-1]
        if class_token == "01":
            return 1
        if class_token == "02":
            return 0

    return None


def scan_dataset(data_dir: str) -> List[LabeledFile]:
    items: List[LabeledFile] = []
    for root, _, files in os.walk(data_dir):
        for fname in files:
            ext = Path(fname).suffix.lower()
            if ext not in AUDIO_EXTS:
                continue
            path = Path(root) / fname
            label = _infer_label(path)
            if label is None:
                continue
            items.append(LabeledFile(str(path), label))
    if not items:
        raise ValueError("No labeled audio files found; verify dataset layout and labels.")
    return items


def split_dataset(items: List[LabeledFile], cfg: LLMConfig) -> Tuple[List[LabeledFile], List[LabeledFile], List[LabeledFile]]:
    rng = random.Random(cfg.seed)
    rng.shuffle(items)
    n_total = len(items)
    n_test = int(n_total * cfg.test_split)
    n_val = int(n_total * cfg.val_split)
    test_items = items[:n_test]
    val_items = items[n_test:n_test + n_val]
    train_items = items[n_test + n_val:]
    return train_items, val_items, test_items


def _featurize_item(item: LabeledFile, cfg: LLMConfig, rng: np.random.Generator | None, augment: bool) -> Tuple[np.ndarray, int]:
    y = load_audio(item.path, cfg)
    if augment and rng is not None:
        y = apply_gain(y, cfg, rng)
        if rng.random() < cfg.add_noise_prob:
            y = add_noise(y, cfg, rng)
    log_mel = extract_log_mel(y, cfg)
    log_mel = normalize_log_mel(log_mel)
    # (n_mels, time) -> (n_mels, time, 1)
    log_mel = log_mel[..., np.newaxis]
    return log_mel, item.label


def build_dataset(items: List[LabeledFile], cfg: LLMConfig, augment: bool) -> Tuple[np.ndarray, np.ndarray]:
    rng = np.random.default_rng(cfg.seed) if augment else None
    features: List[np.ndarray] = []
    labels: List[int] = []
    for item in items:
        feat, label = _featurize_item(item, cfg, rng, augment)
        features.append(feat)
        labels.append(label)
    x = np.stack(features, axis=0)
    y = np.array(labels, dtype=np.int32)
    return x, y
