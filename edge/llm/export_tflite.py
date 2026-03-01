import argparse
from pathlib import Path

import numpy as np
import tensorflow as tf


def representative_dataset(samples_path: Path):
    samples = np.load(samples_path)
    for i in range(min(len(samples), 100)):
        yield [samples[i : i + 1].astype(np.float32)]


def main() -> int:
    parser = argparse.ArgumentParser(description="Export Keras model to TFLite.")
    parser.add_argument("--model", required=True, help="Path to model.keras")
    parser.add_argument("--out", default="edge/llm_artifacts/model.tflite", help="Output .tflite path")
    parser.add_argument("--int8", action="store_true", help="Enable int8 quantization")
    parser.add_argument("--calib-samples", help="Path to .npy of sample inputs for calibration")
    args = parser.parse_args()

    model = tf.keras.models.load_model(args.model)
    converter = tf.lite.TFLiteConverter.from_keras_model(model)

    if args.int8:
        if not args.calib_samples:
            raise ValueError("--calib-samples is required when using --int8")
        converter.optimizations = [tf.lite.Optimize.DEFAULT]
        converter.representative_dataset = lambda: representative_dataset(Path(args.calib_samples))
        converter.target_spec.supported_ops = [tf.lite.OpsSet.TFLITE_BUILTINS_INT8]
        converter.inference_input_type = tf.int8
        converter.inference_output_type = tf.int8

    tflite_model = converter.convert()
    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_bytes(tflite_model)
    print(f"Saved TFLite model to {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
