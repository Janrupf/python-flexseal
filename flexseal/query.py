import abc

from flexseal.sealed import SealedInstallPackage


class Package(abc.ABC):
    """
    Opaque object representing a package.
    """

    def __init__(self):
        pass


class QueryableInstall(abc.ABC):
    """
    Some kind of queryable object which provides a way to query installed
    packages.
    """

    def __init__(self):
        pass

    @abc.abstractmethod
    def all_packages(self) -> list[Package]:
        """
        Get all installed packages.
        """
        pass

    @abc.abstractmethod
    def explicit_packages(self) -> list[Package]:
        """
        Get the explicitly installed packages.
        """
        pass

    @abc.abstractmethod
    def dependencies_of(self, package: Package) -> list[Package]:
        """
        Get the dependencies of a package.
        """
        pass

    def seal(self, package: Package) -> SealedInstallPackage:
        """
        Seal a package.
        """
        pass
