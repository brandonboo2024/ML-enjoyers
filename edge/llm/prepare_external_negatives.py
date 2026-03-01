import argparse
import os
from pathlib import Path

import librosa
import numpy as np
import soundfile as sf

from .config import LLMConfig


AUDIO_EXTS = {".wav", ".flac", ".mp3", ".ogg"}


def _iter_audio_files(root: Path):
    for path in root.rglob("*"):
        if path.suffix.lower() in AUDIO_EXTS and path.is_file():
            yield path


def _split_and_save(
    path: Path,
    out_dir: Path,
    cfg: LLMConfig,
    seconds: float,
    label_suffix: str,
    max_segments: int | None,
):
    y, _ = librosa.load(path, sr=cfg.sample_rate, mono=True)
    seg_len = int(cfg.sample_rate * seconds)
    if seg_len <= 0:
        return 0
    total = len(y) // seg_len
    if total == 0:
        return 0
    if max_segments is not None:
        total = min(total, max_segments)
    base = path.stem
    count = 0
    for i in range(total):
        start = i * seg_len
        end = start + seg_len
        segment = y[start:end]
        if len(segment) < seg_len:
            segment = np.pad(segment, (0, seg_len - len(segment)))
        out_name = f"{base}_{i:03d}{label_suffix}.wav"
        sf.write(out_dir / out_name, segment, cfg.sample_rate)
        count += 1
    return count


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Split external audio into 3s non-fall clips."
    )
    parser.add_argument("--input-dir", required=True, help="Path to external audio root.")
    parser.add_argument(
        "--output-dir",
        default="edge/data/external_negatives",
        help="Where to save labeled non-fall clips.",
    )
    parser.add_argument("--seconds", type=float, default=3.0, help="Segment length.")
    parser.add_argument("--label-suffix", default="-02", help="Suffix for non-fall.")
    parser.add_argument("--max-per-file", type=int, default=5, help="Limit per file.")
    args = parser.parse_args()

    cfg = LLMConfig()
    out_dir = Path(args.output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    total = 0
    for path in _iter_audio_files(Path(args.input_dir)):
        total += _split_and_save(
            path,
            out_dir,
            cfg,
            args.seconds,
            args.label_suffix,
            args.max_per_file,
        )

    print(f"Saved {total} clips to {out_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
