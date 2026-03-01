{ pkgs ? import <nixpkgs> {} }:

let
  python = pkgs.python311.withPackages (ps: with ps; [
    numpy
    scipy
    librosa
    soundfile
    tensorflow
    keras
    kaggle
  ]);

in pkgs.mkShell {
  buildInputs = [ python pkgs.ffmpeg ];
  shellHook = ''
    python --version
    python -c 'import tensorflow as tf; print("TensorFlow:", tf.__version__)'
  '';
}
