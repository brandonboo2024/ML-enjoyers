import numpy as np
import librosa

from .config import LLMConfig


def load_audio_full(path: str, cfg: LLMConfig) -> np.ndarray:
    y, _ = librosa.load(path, sr=cfg.sample_rate, mono=True)
    return y.astype(np.float32)


def load_audio(path: str, cfg: LLMConfig, duration: float | None = None) -> np.ndarray:
    if duration is None:
        duration = cfg.clip_seconds
    y, sr = librosa.load(path, sr=cfg.sample_rate, mono=True, duration=duration)
    target_len = int(cfg.sample_rate * duration)
    if len(y) < target_len:
        y = np.pad(y, (0, target_len - len(y)))
    else:
        y = y[:target_len]
    return y.astype(np.float32)


def center_window(y: np.ndarray, cfg: LLMConfig) -> np.ndarray:
    target_len = int(cfg.sample_rate * cfg.clip_seconds)
    if len(y) <= target_len:
        return np.pad(y, (0, target_len - len(y))).astype(np.float32)

    rms = librosa.feature.rms(
        y=y,
        frame_length=cfg.n_fft,
        hop_length=cfg.hop_length,
        center=True,
    )[0]
    peak_frame = int(np.argmax(rms))
    peak_sample = peak_frame * cfg.hop_length
    start = max(0, peak_sample - target_len // 2)
    end = start + target_len
    if end > len(y):
        end = len(y)
        start = max(0, end - target_len)
    return y[start:end].astype(np.float32)


def rms_normalize(y: np.ndarray, cfg: LLMConfig) -> np.ndarray:
    rms = float(np.sqrt(np.mean(y ** 2)) + 1e-9)
    scale = cfg.rms_target / rms
    y = y * scale
    return np.clip(y, -1.0, 1.0).astype(np.float32)


def rms_level(y: np.ndarray) -> float:
    return float(np.sqrt(np.mean(y ** 2)) + 1e-9)


def apply_gain(y: np.ndarray, cfg: LLMConfig, rng: np.random.Generator) -> np.ndarray:
    gain_db = rng.uniform(cfg.gain_db_min, cfg.gain_db_max)
    gain = 10 ** (gain_db / 20)
    return y * gain


def add_noise(y: np.ndarray, cfg: LLMConfig, rng: np.random.Generator) -> np.ndarray:
    snr_db = rng.uniform(cfg.noise_snr_db_min, cfg.noise_snr_db_max)
    noise = rng.normal(0, 1, size=y.shape).astype(np.float32)
    signal_power = np.mean(y ** 2) + 1e-9
    noise_power = np.mean(noise ** 2) + 1e-9
    noise_scaler = np.sqrt(signal_power / (noise_power * (10 ** (snr_db / 10))))
    return y + noise * noise_scaler


def extract_log_mel(y: np.ndarray, cfg: LLMConfig) -> np.ndarray:
    mel = librosa.feature.melspectrogram(
        y=y,
        sr=cfg.sample_rate,
        n_fft=cfg.n_fft,
        hop_length=cfg.hop_length,
        n_mels=cfg.n_mels,
        fmin=cfg.fmin,
        fmax=cfg.fmax,
        power=2.0,
    )
    log_mel = librosa.power_to_db(mel, ref=np.max)
    return log_mel.astype(np.float32)


def normalize_log_mel(log_mel: np.ndarray) -> np.ndarray:
    if not np.isfinite(log_mel).all():
        finite = log_mel[np.isfinite(log_mel)]
        if finite.size == 0:
            return np.zeros_like(log_mel, dtype=np.float32)
        min_val = float(finite.min())
        log_mel = np.where(np.isfinite(log_mel), log_mel, min_val)
    mean = log_mel.mean()
    std = log_mel.std() + 1e-6
    return (log_mel - mean) / std
