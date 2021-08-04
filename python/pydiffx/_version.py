"""pydiffx version and package information.

These variables and functions can be used to identify the version of pydiffx.
They're largely used for packaging purposes.
"""

from __future__ import unicode_literals


#: The version of pydiffx.
#:
#: This is in the format of:
#:
#: (Major, Minor, Micro, Patch, alpha/beta/rc/final, Release Number, Released)
#:
#: Type:
#:     tuple
VERSION = (1, 0, 1, 0, 'final', 0, True)


def get_version_string():
    """Return the pydiffx version as a human-readable string.

    Returns:
        unicode:
        The human-readable pydiffx version.
    """
    version = '%s.%s' % (VERSION[0], VERSION[1])

    if VERSION[2] or VERSION[3]:
        version += '.%s' % VERSION[2]

    if VERSION[3]:
        version += '.%s' % VERSION[3]

    if VERSION[4] != 'final':
        if VERSION[4] == 'rc':
            version += ' RC%s' % VERSION[5]
        else:
            version += ' %s %s' % (VERSION[4], VERSION[5])

    if not is_release():
        version += ' (dev)'

    return version


def get_package_version():
    """Return the Review Board version as a Python package version string.

    Returns:
        unicode:
        The Review Board package version.
    """
    version = '%s.%s' % (VERSION[0], VERSION[1])

    if VERSION[2] or VERSION[3]:
        version = '%s.%s' % (version, VERSION[2])

    if VERSION[3]:
        version = '%s.%s' % (version, VERSION[3])

    tag = VERSION[4]

    if tag != 'final':
        if tag == 'alpha':
            tag = 'a'
        elif tag == 'beta':
            tag = 'b'

        version = '%s%s%s' % (version, tag, VERSION[5])

    return version


def is_release():
    """Return whether this is a released version of pydiffx.

    Returns:
        bool:
        ``True`` if this is a released version. ``False`` if it is not.
    """
    return VERSION[6]


#: An alias for the the version information from :py:data:`VERSION`.
#:
#: This does not include the last entry in the tuple (the released state).
#:
#: Type:
#:     tuple
__version_info__ = VERSION[:-1]

#: An alias for the version used for the Python package.
#:
#: Type:
#:     unicode
__version__ = get_package_version()
