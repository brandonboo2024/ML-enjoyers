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

If you have a zip archive (for example `archive.zip` at repo root), training now accepts it directly and auto-extracts to `edge/data/extracted/`.
=======
For the Kaggle archive, labels are inferred from filenames of the form `AA-BBB-CC-DDD-EE.wav`:
- `CC == 00` is treated as non-fall
- `CC != 00` is treated as fall

### External negative clips (hard negatives)
To reduce false positives, add loud non-fall sounds (door slam, chair scrape, book drop).
Suggested sources: UrbanSound8K, Freesound.

Prepare external negatives (splits into 3s `-02.wav` clips):
```bash
python -m edge.llm.prepare_external_negatives --input-dir /path/to/external/audio --output-dir edge/data/external_negatives
```

Then copy the generated clips into your training folder (e.g. `edge/data/extracted/archive/`).

## Train

```bash
python -m edge.llm.train --data-dir edge/data
```

Or train directly from your downloaded archive:

```bash
python -m edge.llm.train --data-dir archive.zip
```

Artifacts are saved to `edge/llm_artifacts/`.

### Model variants (lightweight)

```bash
python -m edge.llm.train --data-dir archive.zip --model-type cnn_small --out-dir edge/llm_artifacts/cnn_small
python -m edge.llm.train --data-dir archive.zip --model-type cnn_tiny --out-dir edge/llm_artifacts/cnn_tiny
python -m edge.llm.train --data-dir archive.zip --model-type linear --out-dir edge/llm_artifacts/linear
```

### Temporal variants (sequence-based)

```bash
python -m edge.llm.train --data-dir archive.zip --model-type temporal_gru --out-dir edge/llm_artifacts/temporal_gru
python -m edge.llm.train --data-dir archive.zip --model-type temporal_markov --out-dir edge/llm_artifacts/temporal_markov
```

## Export TFLite

```bash
python -m edge.llm.export_tflite --model edge/llm_artifacts/cnn_small/model.keras --out edge/llm_artifacts/cnn_small/model.tflite
python -m edge.llm.export_tflite --model edge/llm_artifacts/cnn_tiny/model.keras --out edge/llm_artifacts/cnn_tiny/model.tflite
python -m edge.llm.export_tflite --model edge/llm_artifacts/linear/model.keras --out edge/llm_artifacts/linear/model.tflite
python -m edge.llm.export_tflite --model edge/llm_artifacts/temporal_gru/model.keras --out edge/llm_artifacts/temporal_gru/model.tflite
```

For int8 quantization (uses `calib_samples.npy` generated during training):

```bash
python -m edge.llm.export_tflite --model edge/llm_artifacts/model.keras --out edge/llm_artifacts/model_int8.tflite --int8 --calib-samples edge/llm_artifacts/calib_samples.npy
```

## Inference

```bash
python -m edge.llm.infer --model edge/llm_artifacts/model.tflite --audio path/to/sample.wav
```

Temporal inference:

```bash
python -m edge.llm.temporal_infer --mode gru --model edge/llm_artifacts/temporal_gru/model.tflite --audio path/to/sample.wav
python -m edge.llm.temporal_infer --mode markov --model edge/llm_artifacts/temporal_markov/markov_model.json --audio path/to/sample.wav
python -m edge.llm.temporal_infer --mode rule --audio path/to/sample.wav
```

## Edge runtime modes

```bash
python3 edge/edge_device.py --model edge/llm_artifacts/cnn_small/model.tflite --model-mode mel_cnn
python3 edge/edge_device.py --model edge/llm_artifacts/temporal_gru/model.tflite --model-mode temporal_gru
python3 edge/edge_device.py --model edge/llm_artifacts/temporal_markov/markov_model.json --model-mode temporal_markov
python3 edge/edge_device.py --model edge/llm_artifacts/temporal_rule --model-mode temporal_rule
```

Note: temporal GRU inference loads normalization stats from `temporal_norm.npy` in the same output directory.

## Notes

- The dataset loader infers labels from filenames/paths containing "fall"/"nonfall", and also supports SAFE-style suffix labels (`...-01.wav` = fall, `...-02.wav` = non-fall).
- Adjust `edge/llm/config.py` to tweak features or thresholds.
- Training centers each clip on its peak energy with 3-second windows by default.
- Training mixes fall samples with random non-fall clips to add background noise, and defaults to 8 kHz sampling for lower compute.
- Edge runtime supports optional calibration (`--calibrate-seconds`) and a post-impact quiet rule to reduce loud non-fall false positives.

## Edge planning docs

- `edge/LAPTOP_AUDIO_CAPTURE_PLAN.md`
- `edge/OFFLINE_BUFFERING_PLAN.md`
