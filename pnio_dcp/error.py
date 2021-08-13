"""
Copyright (c) 2020 Codewerk GmbH, Karlsruhe.
All Rights Reserved.
License: MIT License see LICENSE.md in the pnio_dcp root directory.
"""


class DcpError(Exception):
    """Base class of the errors thrown by this DCP lib."""
    pass


class DcpTimeoutError(DcpError):
    """Thrown if a timeout occurs withing this DCP lib."""
    pass
