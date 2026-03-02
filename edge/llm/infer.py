import argparse
import time
from pathlib import Path

import numpy as np

from .config import LLMConfig
from .features import load_audio, extract_log_mel, normalize_log_mel, rms_normalize, rms_level


def _load_tflite_interpreter(model_path: str, prefer_tf: bool = False):
    try:
        if prefer_tf:
            raise ImportError("Prefer TensorFlow interpreter")
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


def main() -> int:
    parser = argparse.ArgumentParser(description="Run TFLite inference on a wav file.")
    parser.add_argument("--model", required=True, help="Path to TFLite model")
    parser.add_argument("--audio", required=True, help="Path to audio file")
    args = parser.parse_args()

    cfg = LLMConfig()
    y = load_audio(args.audio, cfg)
    if cfg.silence_gate and rms_level(y) < cfg.silence_rms_threshold:
        print("score=0.0000 label=non-fall (silence gate)")
        return 0
    if cfg.rms_normalize:
        y = rms_normalize(y, cfg)
    log_mel = extract_log_mel(y, cfg)
    log_mel = normalize_log_mel(log_mel)
    x = log_mel[np.newaxis, ..., np.newaxis]

    interpreter = _load_tflite_interpreter(args.model)
    score = _run_inference(interpreter, x.astype(np.float32))
    label = "fall" if score >= cfg.trigger_threshold else "non-fall"

    print(f"score={score:.4f} label={label}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
