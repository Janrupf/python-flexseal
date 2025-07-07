{
  description = "Program for generating lockfiles for python packages";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
    flake-utils.url = "github:numtide/flake-utils";
  };

  outputs = { nixpkgs, flake-utils, ... }:
  (flake-utils.lib.eachDefaultSystem (system:
    let
      pkgs = import nixpkgs { inherit system; };
      package = pkgs.callPackage ./package.nix {};
    in
    {
      devShell = pkgs.mkShell {
        buildInputs = [ (pkgs.python3.withPackages package.mkDependencies) ];
      };

      packages = rec {
        python-flexseal = package.application;
        default = python-flexseal;
      };

      apps = rec {
        python-flexseal = flake-utils.lib.mkApp {
          drv = package.application;
        };
        default = python-flexseal;
      };
    }
  )) // {
    overlays.default = import ./overlay.nix;
  };
}
