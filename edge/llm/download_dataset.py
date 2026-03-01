import os
import subprocess
from pathlib import Path

DATASET = "antonygarciag/fall-audio-detection-dataset"


def main() -> int:
    out_dir = Path("edge/data")
    out_dir.mkdir(parents=True, exist_ok=True)

    kaggle_json = Path.home() / ".kaggle" / "kaggle.json"
    if not kaggle_json.exists() and not (os.getenv("KAGGLE_USERNAME") and os.getenv("KAGGLE_KEY")):
        print("Kaggle credentials not found. Set KAGGLE_USERNAME/KAGGLE_KEY or place kaggle.json in ~/.kaggle/")
        return 1

    cmd = [
        "kaggle",
        "datasets",
        "download",
        "-d",
        DATASET,
        "-p",
        str(out_dir),
        "--unzip",
    ]
    print("Running:", " ".join(cmd))
    subprocess.check_call(cmd)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
