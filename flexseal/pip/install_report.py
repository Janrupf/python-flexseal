from flexseal.pip.models import InstallReportModel, InstallReportItemModel
from flexseal.query import QueryableInstall, Package
from dataclasses import dataclass
from flexseal.sealed import SealedInstallPackage, SealedPackageSource
from packaging.requirements import Requirement
import packaging.utils


@dataclass(frozen=True)
class _InstallReportPackage(Package):
    data: InstallReportItemModel

    def __str__(self):
        return f"{self.data.metadata.name} ({self.data.metadata.version})"

    def __hash__(self):
        return hash((self.data.metadata.name, self.data.metadata.version))


class InstallReport(QueryableInstall):
    """
    A pip install report.
    """

    enabled_extras: dict[str, set[str]] = dict()

    def __init__(self, data: InstallReportModel):
        """
        Create a new install report.

        :param data: the parsed json data from a pip install report
        """
        super().__init__()
        self.data = data

        # Resolve enabled extras
        queued_packages = self.explicit_packages()
        for package in queued_packages:
            self.enabled_extras[package.data.metadata.name] = set(package.data.requested_extras)

        while len(queued_packages) > 0:
            package = queued_packages.pop()
            package_name = packaging.utils.canonicalize_name(package.data.metadata.name)

            enabled_package_extras = self.enabled_extras.get(package_name, set())
            for requirement in package.data.metadata.requires_dist or []:
                if requirement.marker is None or requirement.marker.evaluate(self.data.environment):
                    queued_packages.append(self._package_by_requirement(requirement))

                    for enabled_extra in requirement.extras:
                        self._enable_extra(requirement, enabled_extra)

            for enabled_extra in enabled_package_extras:
                for requirement in package.data.metadata.requires_dist or []:
                    environment = self._environment_with_extra(enabled_extra)
                    if requirement.marker is not None and requirement.marker.evaluate(environment):
                        if self._enable_extra(requirement, enabled_extra):
                            # Enqueue again because we enabled a new extra
                            queued_packages.append(self._package_by_requirement(requirement))

    def _enable_extra(self, requirement: Requirement, extra: str) -> bool:
        name = packaging.utils.canonicalize_name(requirement.name)
        enabled_extras = self.enabled_extras.get(name, set())
        if extra not in enabled_extras:
            enabled_extras.add(extra)
            self.enabled_extras[name] = enabled_extras
            return True

        return False

    def all_packages(self) -> list[Package]:
        return [_InstallReportPackage(item) for item in self.data.install]

    def explicit_packages(self) -> list[_InstallReportPackage]:
        return [_InstallReportPackage(item) for item in self.data.install if item.requested]

    def dependencies_of(self, package: _InstallReportPackage) -> list[_InstallReportPackage]:
        if package.data.metadata.requires_dist is None:
            return []

        active_requirements = filter(
            lambda req: self.requires_dependency(package, req),
            package.data.metadata.requires_dist
        )

        return [self._package_by_requirement(dep) for dep in active_requirements]

    def requires_dependency(self, package: _InstallReportPackage, dependency: Requirement) -> bool:
        if dependency.marker is None or dependency.marker.evaluate(self.data.environment):
            return True

        # Check if any enabled extra enables the dependency
        package_name = packaging.utils.canonicalize_name(package.data.metadata.name)
        package_extras = self.enabled_extras.get(package_name, set())

        for enabled_extra in package_extras:
            environment = self._environment_with_extra(enabled_extra)
            if dependency.marker.evaluate(environment):
                return True

        return False

    def seal(self, package: _InstallReportPackage) -> SealedInstallPackage:
        dependencies = self.dependencies_of(package)

        hashes = dict()
        generic_hash_key, generic_hash_value = package.data.download_info.archive_info.hash.split("=", 1)
        hashes[generic_hash_key] = generic_hash_value

        for hash_name, hash_value in package.data.download_info.archive_info.hashes.items():
            hashes[hash_name] = hash_value

        package_name = packaging.utils.canonicalize_name(package.data.metadata.name)
        extras = list(self.enabled_extras.get(package_name, set()))

        source = SealedPackageSource.model_construct(
            urls=[package.data.download_info.url],
            hashes=hashes,
            is_wheel=package.data.download_info.url.endswith(".whl"),
        )

        return SealedInstallPackage.model_construct(
            name=packaging.utils.canonicalize_name(package.data.metadata.name),
            version=str(package.data.metadata.version),
            dependencies=list(set(packaging.utils.canonicalize_name(dep.data.metadata.name) for dep in dependencies)),
            source=source,
            enabled_extras=extras,
        )

    def _package_by_requirement(self, req: Requirement) -> _InstallReportPackage:
        for package in self.data.install:
            if packaging.utils.canonicalize_name(package.metadata.name) == packaging.utils.canonicalize_name(req.name):
                return _InstallReportPackage(package)

        raise ValueError(f"Requirement {req} not found in install report")

    def _environment_with_extra(self, extra: str):
        return {**self.data.environment, "extra": extra}
