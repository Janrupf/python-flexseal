from dataclasses import dataclass, field

from pydantic import BaseModel


@dataclass
class SealedPackageSource(BaseModel):
    urls: list[str]
    hashes: dict[str, str]
    is_wheel: bool


@dataclass
class SealedInstallPackage(BaseModel):
    name: str
    version: str
    source: SealedPackageSource
    enabled_extras: list[str]
    dependencies: list[str] = field(default_factory=list)


@dataclass
class SealedInstallInstructions(BaseModel):
    packages: list[SealedInstallPackage] = field(default_factory=list)
