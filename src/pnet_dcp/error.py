"""
Copyright (c) 2024 Elias Rosch, Esslingen.
Copyright (c) 2020 Codewerk GmbH, Karlsruhe.
All Rights Reserved.
"""


class DcpError(Exception):
    """Base class of the errors thrown by this DCP lib."""
    pass


class DcpTimeoutError(DcpError):
    """Thrown if a timeout occurs withing this DCP lib."""
    pass
