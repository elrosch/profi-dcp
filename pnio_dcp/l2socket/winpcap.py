"""
Copyright (c) 2021 Codewerk GmbH, Karlsruhe.
All Rights Reserved.
License: MIT License see LICENSE.md in the pnio_dcp root directory.
"""
import ctypes
import os
import pathlib
import ctypes.util

# Define all necessary structs and type aliases
bpf_u_int32 = ctypes.c_uint32
pcap_t = ctypes.c_void_p
u_char = ctypes.c_ubyte
c_string = ctypes.c_char_p


class bpf_insn(ctypes.Structure):
    _fields_ = [("code", ctypes.c_ushort),
                ("jt", ctypes.c_ubyte),
                ("jf", ctypes.c_ubyte),
                ("k", ctypes.c_int)]


class bpf_program(ctypes.Structure):
    _fields_ = [('bf_len', ctypes.c_int),
                ('bf_insns', ctypes.POINTER(bpf_insn))]


class timeval(ctypes.Structure):
    _fields_ = [('tv_sec', ctypes.c_long),
                ('tv_usec', ctypes.c_long)]


class pcap_pkthdr(ctypes.Structure):
    _fields_ = [('ts', timeval),
                ('caplen', bpf_u_int32),
                ('len', bpf_u_int32)]


class sockaddr(ctypes.Structure):
    _fields_ = [("sa_family", ctypes.c_ushort),
                ("sa_data", ctypes.c_ubyte * 14)]


class sockaddr_in(ctypes.Structure):
    _fields_ = [("sin_family", ctypes.c_ushort),
                ("sin_port", ctypes.c_uint16),
                ("sin_addr", 4 * ctypes.c_ubyte)]


class sockaddr_in6(ctypes.Structure):
    _fields_ = [("sin6_family", ctypes.c_ushort),
                ("sin6_port", ctypes.c_uint16),
                ("sin6_flowinfo", ctypes.c_uint32),
                ("sin6_addr", 16 * ctypes.c_ubyte),
                ("sin6_scope_id", ctypes.c_uint32)]


class pcap_addr(ctypes.Structure):
    pass


pcap_addr._fields_ = [('next', ctypes.POINTER(pcap_addr)),
                      ('addr', ctypes.POINTER(sockaddr)),
                      ('netmask', ctypes.POINTER(sockaddr)),
                      ('broadaddr', ctypes.POINTER(sockaddr)),
                      ('dstaddr', ctypes.POINTER(sockaddr))]


class pcap_if(ctypes.Structure):
    pass


pcap_if._fields_ = [('next', ctypes.POINTER(pcap_if)),
                    ('name', c_string),
                    ('description', c_string),
                    ('addresses', ctypes.POINTER(pcap_addr)),
                    ('flags', ctypes.c_uint)]


def load_dll(library_name):
    library = ctypes.util.find_library(library_name)
    if not library:
        raise OSError(f"Cannot find library {library_name}")
    return ctypes.CDLL(library)


class WinPcap:
    __pcap_dll = None

    """
    Wrapper class for (a subset of) pcap. See e.g. https://www.winpcap.org/docs/docs_412/html/main.html for a more
    detailed documentation of the underlying functionality.
    """

    def __init__(self):
        """Create a new WinPcap object, load the WinPcap or Npcap DLL and export the necessary functions"""
        self.__load_pcap_dll()
        self.__load_functions_from_dll()

    def __load_pcap_dll(self):
        """
        Try loading WinPcap or Npcap DLL if it is not already loaded.
        Will raise an OSError if neither WinPcap nor Npcap can be found.
        """
        if self.__pcap_dll is None:
            npcap_path = pathlib.Path(os.environ["WINDIR"], "System32", "Npcap")
            if npcap_path.exists():
                os.environ['PATH'] = f"{npcap_path};{os.environ['PATH']}"
                load_dll("Packet")
            self.__pcap_dll = load_dll("wpcap")

    def __load_functions_from_dll(self):
        """
        Import all necessary functions from the DLL and set their argument and return types
        The following functions are imported:
          - pcap_open_live
          - pcap_setmintocopy
          - pcap_close
          - pcap_next_ex
          - pcap_sendpacket
          - pcap_compile
          - pcap_setfilter
          - pcap_findalldevs
        """
        self._pcap_open_live = self.__pcap_dll.pcap_open_live
        self._pcap_open_live.argtypes = [c_string, ctypes.c_int, ctypes.c_int, ctypes.c_int, c_string]
        self._pcap_open_live.restype = ctypes.POINTER(pcap_t)

        self._pcap_setmintocopy = self.__pcap_dll.pcap_setmintocopy
        self._pcap_setmintocopy.argtype = [ctypes.POINTER(pcap_t), ctypes.c_int]
        self._pcap_setmintocopy.restype = ctypes.c_int

        self._pcap_close = self.__pcap_dll.pcap_close
        self._pcap_close.argtypes = [ctypes.POINTER(pcap_t)]
        self._pcap_close.restype = None

        self._pcap_next_ex = self.__pcap_dll.pcap_next_ex
        self._pcap_next_ex.argtypes = [ctypes.POINTER(pcap_t), ctypes.POINTER(ctypes.POINTER(pcap_pkthdr)),
                                       ctypes.POINTER(ctypes.POINTER(u_char))]
        self._pcap_next_ex.restype = ctypes.c_int

        self._pcap_sendpacket = self.__pcap_dll.pcap_sendpacket
        self._pcap_sendpacket.argtypes = [ctypes.POINTER(pcap_t), ctypes.c_void_p, ctypes.c_int]
        self._pcap_sendpacket.restype = ctypes.c_int

        self._pcap_compile = self.__pcap_dll.pcap_compile
        self._pcap_compile.argtypes = [ctypes.POINTER(pcap_t), ctypes.POINTER(bpf_program), c_string, ctypes.c_int,
                                       bpf_u_int32]
        self._pcap_compile.restype = ctypes.c_int

        self._pcap_setfilter = self.__pcap_dll.pcap_setfilter
        self._pcap_setfilter.argtypes = [ctypes.POINTER(pcap_t), ctypes.POINTER(bpf_program)]
        self._pcap_setfilter.restype = ctypes.c_int

        self._pcap_findalldevs = self.__pcap_dll.pcap_findalldevs
        self._pcap_findalldevs.argtypes = [ctypes.POINTER(ctypes.POINTER(pcap_if)), c_string]
        self._pcap_findalldevs.restype = ctypes.c_int

    def pcap_open_live(self, device, to_ms, snaplen=0xffff, promisc=0):
        """
        Create a pcap object and start capturing.
        :param device: The network device to open.
        :type device: string
        :param to_ms: The read timeout in milliseconds (not supported by all platforms). A timeout of 0 corresponds (on
        supporting platforms) to no timeout, i.e. a read waits until enough packets have arrived.
        :type to_ms: int
        :param snaplen: The maximum number of bytes to capture. If a packet is longer than the snaplen, all bytes beyond
        the snaplen are discarded.
        :type snaplen: int
        :param promisc: Whether the interface should be put into promiscuous mode. Note: the interface may already be in
        promiscuous mode independent of this flag.
        :type promisc: int
        :return: To opened pcap object.
        :rtype: POINTER(pcap_t)
        """
        device_buffer = ctypes.create_string_buffer(device.encode("utf8"))
        error_buffer = ctypes.create_string_buffer(256)
        p = self._pcap_open_live(device_buffer, snaplen, promisc, to_ms, error_buffer)

        # Check for potential errors
        error = bytes(bytearray(error_buffer)).strip(b"\x00")
        if error:
            raise OSError(error)

        return p

    def pcap_close(self, p):
        """
        Closes a given pcap object, closing all associated files and deallocating resources.
        :param p: The pcap object to close.
        :type p: POINTER(pcap_t)
        """
        self._pcap_close(p)

    def pcap_setmintocopy(self, p, size):
        """
        Set minimum amount of data received in a single system call (unless the timeout expires).
        :param p: The pcap object.
        :type p: POINTER(pcap_t)
        :param size: The minimum amount of data.
        :type size: int
        :return: 0 on success, -1 on failure.
        :rtype: int
        """
        return self._pcap_setmintocopy(p, size)

    def pcap_next_ex(self, p, pkt_header, pkt_data):
        """
        Read the next available packet from a given interface.
        :param p: The pcap object to read from.
        :type p: POINTER(pcap_t)
        :param pkt_header: The header of the captured packet. Filled by pcap_next_ex, only value if return value is 0.
        :type pkt_header: POINTER(pcap_pkthdr)
        :param pkt_data: The data of the captured packet. Filled by pcap_next_ex, only value if return value is 0.
        :type pkt_data: POINTER(ctypes.c_ubyte)
        :return: 1 on success, 0 on timeout, -1 on error, -2 on EOF (offline capture only)
        :rtype: int
        """
        return self._pcap_next_ex(p, pkt_header, pkt_data)

    def pcap_sendpacket(self, p, buf, size=None):
        """
        Send a raw packet to the network.
        :param p: The pcap object used to send the packet.
        :type p: POINTER(pcap_t)
        :param buf: The data of the packet to send.
        :type buf: c_void_p
        :param size: The size of the packet to send (i.e. the size of buf).
        :type size: int
        :return: -1 on failure, 0 on success.
        :rtype: int
        """
        return self._pcap_sendpacket(p, buf, size)

    def pcap_compile(self, p, fp, filter_string, optimize=0, netmask=-1):
        """
        Compile he given packet filter into a bpf filter program.
        :param p: The pcap object.
        :type p: POINTER(pcap_t)
        :param fp: A reference to the bpf filter program, filled in by pcap_compile()
        :type fp: bpf_program
        :param filter_string: The filter expression to compile.
        :type filter_string: string
        :param optimize: Whether the resulting filter program should be optimized.
        :type optimize: int
        :param netmask: Only used to check for IPv4 broadcast addresses in the filter program. See official Pcap
        documentation for more information.
        :type netmask: uint32
        :return: -1 on error (0 on success?)
        :rtype: int
        """
        filter_buffer = ctypes.create_string_buffer(filter_string.encode("utf8"))
        return self._pcap_compile(p, fp, filter_buffer, optimize, netmask)

    def pcap_setfilter(self, p, fp):
        """
        Apply a bpf filter to the given capture.
        :param p: The pcap object to apply the filter to.
        :type p: POINTER(pcap_t)
        :param fp: The bpf filter program to apply.
        :type fp: bpf_program
        :return: -1 on failure, 0 on success.
        :rtype: int
        """
        return self._pcap_setfilter(p, fp)

    def pcap_findalldevs(self, alldevsp):
        """
        Finds all network devices that can be opened with pcap_open_live and returns them as list of pcap_if objects.
        :param alldevsp: Use to return a pointer to the first device found.
        :type alldevsp: POINTER(POINTER(pcap_if))
        :return: Return value of findalldevs (0 on success, -1 on failure) and the error message in case of an error.
        :rtype: Tuple(int, Optional(string))
        """
        error_buffer = ctypes.create_string_buffer(256)
        return_value = self._pcap_findalldevs(alldevsp, error_buffer)

        error_message = None if return_value == 0 else error_buffer.value
        return return_value, error_message
