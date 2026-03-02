# Edge LLM Audio Classifier (TFLite)

## Overview

This is a minimal fall-vs-non-fall audio classifier pipeline. It follows the plan in `LLM_PLAN.md` and is designed for quick iteration, not production.

## Setup

Install dependencies:

```bash
pip install -r edge/requirements-llm.txt
```

## Dataset

Download the Kaggle dataset (requires Kaggle CLI + credentials):

```bash
python -m edge.llm.download_dataset
```

If you already have the dataset locally, pass its path directly to training.
If you have a zip archive (for example `archive.zip` at repo root), training now accepts it directly and auto-extracts to `edge/data/extracted/`.

## Train

```bash
python -m edge.llm.train --data-dir edge/data
```

Or train directly from your downloaded archive:

```bash
python -m edge.llm.train --data-dir archive.zip
```

Artifacts are saved to `edge/llm_artifacts/`.

## Export TFLite

```bash
python -m edge.llm.export_tflite --model edge/llm_artifacts/model.keras --out edge/llm_artifacts/model.tflite
```

For int8 quantization (uses `calib_samples.npy` generated during training):

```bash
python -m edge.llm.export_tflite --model edge/llm_artifacts/model.keras --out edge/llm_artifacts/model_int8.tflite --int8 --calib-samples edge/llm_artifacts/calib_samples.npy
```

## Inference

```bash
python -m edge.llm.infer --model edge/llm_artifacts/model.tflite --audio path/to/sample.wav
```

## Notes

- The dataset loader infers labels from filenames/paths containing "fall"/"nonfall", and also supports SAFE-style suffix labels (`...-01.wav` = fall, `...-02.wav` = non-fall).
- Adjust `edge/llm/config.py` to tweak features or thresholds.
- Training now centers each clip on its peak energy and applies RMS normalization by default; you can disable these in `edge/llm/config.py`.

## Edge planning docs

- `edge/LAPTOP_AUDIO_CAPTURE_PLAN.md`
- `edge/OFFLINE_BUFFERING_PLAN.md`
