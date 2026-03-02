from dataclasses import dataclass


@dataclass
class LLMConfig:
    # Audio + feature params
    sample_rate: int = 8000
    clip_seconds: float = 2.0
    n_fft: int = 200  # 25ms @ 8kHz
    hop_length: int = 80  # 10ms @ 8kHz
    n_mels: int = 64
    fmin: int = 0
    fmax: int = 4000
    center_on_peak: bool = True
    rms_normalize: bool = False
    rms_target: float = 0.1
    silence_gate: bool = True
    silence_rms_threshold: float = 0.05

    # Training params
    batch_size: int = 32
    epochs: int = 25
    seed: int = 42
    val_split: float = 0.1
    test_split: float = 0.1

    # Augmentation params
    add_noise_prob: float = 0.3
    noise_snr_db_min: float = 0.0
    noise_snr_db_max: float = 20.0
    mix_noise_prob: float = 0.7
    mix_snr_db_min: float = 0.0
    mix_snr_db_max: float = 15.0
    gain_db_min: float = -6.0
    gain_db_max: float = 6.0

    # Inference params
    smooth_window: int = 5
    trigger_threshold: float = 0.6
    cooldown_seconds: float = 15.0

    # Paths
    model_dir: str = "edge/llm_artifacts"
