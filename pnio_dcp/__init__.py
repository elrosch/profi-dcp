"""
Copyright (c) 2020 Codewerk GmbH, Karlsruhe.
All Rights Reserved.
License: MIT License see LICENSE.md in the pnio_dcp root directory.
"""
import setuptools_scm
from importlib_metadata import version, PackageNotFoundError

try:  # try getting the installed version
    __version__ = version("pnio_dcp")
except PackageNotFoundError:
    try:  # if not installed, try getting the version from the git repository
        __version__ = setuptools_scm.get_version(root='..', relative_to=__file__)
    except (LookupError, OSError):  # otherwise the version cannot be determined and is set to unknown
        __version__ = "unknown"

from .pnio_dcp import DCP, Device, ResponseCode
from .error import DcpError, DcpTimeoutError
