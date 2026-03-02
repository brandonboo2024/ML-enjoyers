import argparse
from pathlib import Path

import numpy as np
import tensorflow as tf

from .config import LLMConfig
from .data import (
    resolve_data_dir,
    scan_dataset,
    split_dataset,
    build_dataset,
    build_temporal_dataset,
)
from .model import build_model
from .temporal_models import train_markov


def main() -> int:
    parser = argparse.ArgumentParser(description="Train fall audio classifier.")
    parser.add_argument("--data-dir", required=True, help="Path to dataset root directory or .zip archive.")
    parser.add_argument("--out-dir", default="edge/llm_artifacts", help="Output directory.")
    parser.add_argument(
        "--model-type",
        default="cnn_small",
        choices=["cnn_small", "cnn_tiny", "linear", "temporal_gru", "temporal_markov"],
    )
    args = parser.parse_args()

    cfg = LLMConfig(model_dir=args.out_dir)
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    data_dir = resolve_data_dir(args.data_dir)
    items = scan_dataset(data_dir)
    train_items, val_items, test_items = split_dataset(items, cfg)

    if args.model_type == "temporal_markov":
        x_train, y_train = build_temporal_dataset(train_items, cfg, augment=True)
        x_val, y_val = build_temporal_dataset(val_items, cfg, augment=False)
        x_test, y_test = build_temporal_dataset(test_items, cfg, augment=False)
        train_markov(
            np.concatenate([x_train, x_val], axis=0),
            np.concatenate([y_train, y_val], axis=0),
            out_dir,
            cfg.seed,
        )
        print("Saved temporal Markov model to", out_dir / "markov_model.json")
        return 0

    if args.model_type == "temporal_gru":
        x_train, y_train = build_temporal_dataset(train_items, cfg, augment=True)
        x_val, y_val = build_temporal_dataset(val_items, cfg, augment=False)
        x_test, y_test = build_temporal_dataset(test_items, cfg, augment=False)
        mean = x_train.reshape(-1, x_train.shape[-1]).mean(axis=0)
        std = x_train.reshape(-1, x_train.shape[-1]).std(axis=0) + 1e-6
        x_train = (x_train - mean) / std
        x_val = (x_val - mean) / std
        x_test = (x_test - mean) / std
        np.save(out_dir / "temporal_norm.npy", {"mean": mean, "std": std})
    else:
        x_train, y_train = build_dataset(train_items, cfg, augment=True)
        x_val, y_val = build_dataset(val_items, cfg, augment=False)
        x_test, y_test = build_dataset(test_items, cfg, augment=False)

    model = build_model(input_shape=x_train.shape[1:], model_type=args.model_type)

    callbacks = [
        tf.keras.callbacks.EarlyStopping(monitor="val_loss", patience=5, restore_best_weights=True),
        tf.keras.callbacks.ModelCheckpoint(out_dir / "model.keras", save_best_only=True),
    ]

    model.fit(
        x_train,
        y_train,
        validation_data=(x_val, y_val),
        epochs=cfg.epochs,
        batch_size=cfg.batch_size,
        callbacks=callbacks,
        verbose=1,
    )

    results = model.evaluate(x_test, y_test, verbose=0)
    metrics = dict(zip(model.metrics_names, results))
    np.save(out_dir / "metrics.npy", metrics)

    # Save a small calibration set for optional int8 quantization
    calib_samples = x_train[: min(len(x_train), 200)].astype(np.float32)
    np.save(out_dir / "calib_samples.npy", calib_samples)

    print("Test metrics:")
    for key, value in metrics.items():
        print(f"{key}: {value:.4f}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
