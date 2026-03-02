{ pkgs ? import <nixpkgs> {} }:

let
  python = pkgs.python3;
  libPath = pkgs.lib.makeLibraryPath (with pkgs; [
    stdenv.cc.cc
    zlib
    portaudio
  ]);
in
pkgs.mkShell {
  packages = [
    python
    pkgs.portaudio
  ];

  shellHook = ''
<<<<<<< HEAD
    python --version
    python -c 'import tensorflow as tf; print("TensorFlow:", tf.__version__)'
=======
    export LD_LIBRARY_PATH="${libPath}:$LD_LIBRARY_PATH"
>>>>>>> f2387ff ([changes])
  '';
}
