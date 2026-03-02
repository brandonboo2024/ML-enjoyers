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
    export LD_LIBRARY_PATH="${libPath}:$LD_LIBRARY_PATH"
  '';
}
