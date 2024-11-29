# python-flexseal
###### generate reproducible python lockfiles for existing projects

I frequently find myself in the need of generating lockfiles that can be used with the nix package manager
for reproducible installations of python packages. This little program takes some sort of installation report
or lockfile and generates a common, package manager independent lockfile that can be used to install the same
packages in a different environment.
