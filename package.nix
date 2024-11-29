{ lib
, python3Packages
, ...}:
rec {
  mkDependencies = pythonPkgs: with pythonPkgs; [
    packaging
    pydantic
  ];

  application = python3Packages.buildPythonApplication rec {
    pname = "python-flexseal";
    version = "0.1.0";
    src = ./.;
    propagatedBuildInputs = mkDependencies python3Packages;
  };
}