from flexseal.query import QueryableInstall


class InstallEnvironment:
    def __init__(self, queryable: QueryableInstall):
        """
        Create the install environment.

        :param queryable: the underlying abstract information provider
        """
        self.install = queryable
