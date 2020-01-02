import os

import homebase

from penaltymodel.cache.package_info import __version__

__all__ = ['cache_file']

APPNAME = 'dwave-penaltymodel-cache'
"""The application name is used to determine the cache location."""

APPAUTHOR = 'dwave-systems'
"""The application author is used to determine the cache location."""

DATABASENAME = 'penaltymodel_cache_v%s.db' % __version__
"""The name for the sqlite database itself. Based on the version of the package."""


def cache_file(app_name=APPNAME, app_author=APPAUTHOR, filename=DATABASENAME):
    """Returns the filename (including path) for the data cache.

    The path will depend on the operating system, certain environmental
    variables and whether it is being run inside a virtual environment.
    See `homebase <https://github.com/dwavesystems/homebase>`_.

    Args:
        app_name (str, optional): The application name.
            Default is given by :obj:`.APPNAME`.
        app_author (str, optional): The application author. Default
            is given by :obj:`.APPAUTHOR`.
        filename (str, optional): The name of the database file.
            Default is given by :obj:`DATABASENAME`.

    Returns:
        str: The full path to the file that can be used as a cache.

    Notes:
        Creates the directory if it does not already exist.

        If run inside of a virtual environment, the cache will be stored
        in `/path/to/virtualenv/data/app_name`

    """
    user_data_dir = homebase.user_data_dir(app_name=app_name, app_author=app_author, create=True)
    return os.path.join(user_data_dir, filename)
