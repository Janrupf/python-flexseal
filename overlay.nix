final: prev: {
  python-flexseal = (prev.callPackage ./package.nix {}).application;
}
