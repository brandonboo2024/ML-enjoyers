{ pkgs ? import <nixpkgs> {} }:

let
  python = pkgs.python311.withPackages (ps: with ps; [
    numpy
    scipy
    librosa
    soundfile
    tensorflow
    kaggle
  ]);

in pkgs.mkShell {
  buildInputs = [ python pkgs.ffmpeg ];
  shellHook = ''
    echo "Python: $(python --version)"
    echo "TensorFlow: $(python - <<'PY'\nimport tensorflow as tf\nprint(tf.__version__)\nPY)"
  '';
}
