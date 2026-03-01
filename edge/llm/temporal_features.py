import numpy as np
import librosa

from .config import LLMConfig


def expected_frames(cfg: LLMConfig) -> int:
    target_len = int(cfg.sample_rate * cfg.clip_seconds)
    if target_len <= cfg.n_fft:
        return 1
    return 1 + (target_len - cfg.n_fft) // cfg.hop_length


def _fix_length(vec: np.ndarray, length: int) -> np.ndarray:
    if vec.shape[0] == length:
        return vec
    if vec.shape[0] < length:
        return np.pad(vec, (0, length - vec.shape[0]))
    return vec[:length]


def extract_temporal_features(y: np.ndarray, cfg: LLMConfig) -> np.ndarray:
    """Extract lightweight temporal features for sequence models."""
    S = np.abs(
        librosa.stft(y, n_fft=cfg.n_fft, hop_length=cfg.hop_length, center=True)
    ) ** 2
    rms = librosa.feature.rms(S=S, frame_length=cfg.n_fft, hop_length=cfg.hop_length)[0]
    centroid = librosa.feature.spectral_centroid(S=S, sr=cfg.sample_rate)[0]
    bandwidth = librosa.feature.spectral_bandwidth(S=S, sr=cfg.sample_rate)[0]
    rolloff = librosa.feature.spectral_rolloff(S=S, sr=cfg.sample_rate, roll_percent=0.85)[
        0
    ]
    flatness = librosa.feature.spectral_flatness(S=S)[0]

    S_norm = S / (np.sum(S, axis=0, keepdims=True) + 1e-9)
    flux = np.sqrt(
        np.sum(
            np.diff(S_norm, axis=1, prepend=S_norm[:, :1]) ** 2,
            axis=0,
        )
    )
    entropy = -np.sum(S_norm * np.log(S_norm + 1e-9), axis=0)

    freqs = librosa.fft_frequencies(sr=cfg.sample_rate, n_fft=cfg.n_fft)
    low_mask = freqs < 1000
    high_mask = ~low_mask
    low_energy = np.sum(S[low_mask, :], axis=0)
    high_energy = np.sum(S[high_mask, :], axis=0)
    band_ratio = low_energy / (high_energy + 1e-9)

    T = expected_frames(cfg)
    features = np.stack(
        [
            _fix_length(rms, T),
            _fix_length(centroid, T),
            _fix_length(bandwidth, T),
            _fix_length(rolloff, T),
            _fix_length(flatness, T),
            _fix_length(flux, T),
            _fix_length(entropy, T),
            _fix_length(band_ratio, T),
        ],
        axis=1,
    )
    return features.astype(np.float32)
