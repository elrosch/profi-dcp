"""
Copyright (c) 2021 Codewerk GmbH, Karlsruhe.
All Rights Reserved.
License: MIT License see LICENSE.md in the pnio_dcp root directory.
"""
import os
from .l2socket import L2PcapSocket

if os.name == 'nt':
    L2Socket = L2PcapSocket
elif os.name == 'posix':
    raise NotImplementedError(f"OS {os.name} is currently not supported.")
else:
    raise NotImplementedError(f"OS {os.name} is currently not supported.")
