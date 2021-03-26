"""
Copyright (c) 2020 Codewerk GmbH, Karlsruhe.
All Rights Reserved.
License: MIT License see LICENSE.md in the pnio_dcp root directory.
"""
import binascii
from collections import namedtuple, OrderedDict
from struct import pack, unpack, calcsize


def mac_to_hex(mac):
    """
    Converts the mac address from ':'-separated strings to bytes by encoding each part as binary and concatenating them.
    :param mac: The mac address given as ':'-separated strings.
    :type mac: string
    :return: The mac address encoded as bytes.
    :rtype: bytes
    """
    return b''.join(binascii.unhexlify(num) for num in mac.split(':'))


def hex_to_mac(hex_mac_str):
    """
    Converts the mac address from bytes to ':'-separated strings by decoding each byte to a 2-digit lower-case string
    and concatenating them separated by ':'.
    :param hex_mac_str: The mac address encoded as bytes.
    :type hex_mac_str: bytes
    :return: The mac address as ':'-separated lower-case strings.
    :rtype: string
    """
    return ':'.join(format(num, '02x') for num in hex_mac_str)


def hex_to_ip(hex_ip_str):
    """
    Converts the ip address from bytes to string by decoding each byte to int and concatenating them separated by '.'.
    :param hex_ip_str: The ip address encoded as bytes.
    :type hex_ip_str: bytes
    :return: The ip address as string.
    :rtype: string
    """
    return '.'.join(str(octet) for octet in hex_ip_str)


def unpack_data_w_keywords(args, preamble, preamble_size, payload, payload_field_len, fields, offset):
    """
    Unpack a single bytes arg to the args and kwargs expected by _Bytestr.__new__ (see create_bytestr).
    The first 'preamble_size' bytes are unpacked to the preamble, i.e. the field values, and are returned as tuple in
    the first return value.
    The second return value are the kwargs, they contain only the keyword "payload" and the corresponding subset of the
    input bytes object as value and are empty if there is no payload.
    :param args: The arguments to unpack. Should contain exactly one argument of type bytes.
    :type args: tuple[bytes]
    :param preamble: the struct format for the _Bytestr preamble (see create_bytestr)
    :type preamble: string
    :param preamble_size: the size of the preamble (that is returned by calcsize(preamble))
    :type preamble_size: integer
    :param payload: Whether there is a payload.
    :type payload: boolean
    :param payload_field_len: The name of the field containing the payload length.
    :type payload_field_len: string
    :param fields: The fields of the _Bytestr in an OrderedDict. The key is the name of the field, the value contains
    either its struct format or a tuple, where the first value defines the struct format.
    :type fields: OrderedDict[string, Union[string, Tuple[string, Any]]]
    :param offset: The offset after the payload (is added to the payload length if applicable).
    :type offset: int
    :return: The unpacked args and kwargs. The kwargs contain only the payload,
    i.e. {"payload", <the subset of the input bytes object containing the payload>} or {} if there is no payload.
    :rtype: tuple[any], dict[string, bytes]
    """
    data = args[0]
    # unpack known-size fields
    unpacked = unpack(preamble, data[0:preamble_size])
    keywords = {}
    # handle payload
    if payload:
        if payload_field_len is not None:
            payload_size = unpacked[list(fields.keys()).index(payload_field_len)] + offset
            keywords["payload"] = data[preamble_size:preamble_size + payload_size]
        else:
            keywords["payload"] = data[preamble_size:]
    return unpacked, keywords


def create_bytestr(name, fields, options={}, payload=True, payload_field_len=None, offset=0):
    """
    Create a new _Bytestr class:
    - a subclass of a namedtuple with the following attributes: the names of all given fields and 'payload'
    - additional methods:
        - __bytes__ to convert it to a bytes object
        - __len__ to return the length of preamble + payload
    - additional attributes: the options passed as dict to this function
    :param name: The name of the created _Bytestr.
    :type name: string
    :param fields: The fields of the created _Bytestr as a tuple of tuples. Each of the tuples describes one field.
    The first value is a string and contains the fields name.
    The second value is either a single string, defining the fields format in a python struct;
    Or a tuple, where the first string defines the struct format (all further values are unused).
    :type fields: Tuple[Tuple[string, Union[string, Tuple[string, any]]]
    :param options: A dict of options and their values. Will be set as additional attributes of the created _Bytestr.
    :type options: dict of string: any
    :param payload: Whether there is a payload.
    :type payload: bool
    :param payload_field_len: The name of the field containing the payload length (if applicable). Default: None.
    :type payload_field_len: Optional[string]
    :param offset: The offset after the payload (is added to the payload length if applicable).
    :type offset: int
    :return: The created _Bytestr with the fields, options etc. defined as described above.
    :rtype: class
    """
    # define the struct format for the preamble and compute the corresponding size:
    # > for big-endian, followed by the format of each field (given as (first) value of the field)
    fields = OrderedDict(fields)
    preamble = ">" + "".join([(f[0] if isinstance(f, tuple) else f) for f in fields.values()])
    preamble_size = calcsize(preamble)

    # Create a named-tuple to be subclassed with all fields as attributes and a payload attribute
    attribute_keys = list(fields.keys())
    attribute_keys.append('payload')
    t = namedtuple(name, attribute_keys)

    class _Bytestr(t):

        def __new__(cls, *args, **kwargs):
            """
            Create a new instance with the given args and kwargs using the __new__ function of the parental namedtuple.
            If exactly one arg is given, it is assumed to be a bytes object returned by cls.__bytes__(). In that case,
            the args and kwargs are unpacked from it using unpack_data_w_keywords.
            __new__ is used instead of __init__ because named tuples are immutable, meaning __init__ cannot be called.
            :param args: If exactly one arg is given, it is assumed to be a bytes object returned by cls.__bytes__()
            Otherwise: values of the fields in the same order as in the 'fields' parameter
            :param kwargs: The (potentially optional) payload kwarg.
            """
            # unpack (parse packet)
            if len(args) == 1:
                unpacked, keywords = unpack_data_w_keywords(args, preamble, preamble_size, payload, payload_field_len,
                                                            fields, offset)
                self = t.__new__(cls, *unpacked, **keywords)
            else:
                self = t.__new__(cls, *args, **kwargs)
            return self

        def __bytes__(self):
            """
            Convert this byte-string to a bytes object containing the fields and the optional payload.
            The fields are packed according the the format defined by 'preamble'.
            If there is a payload, it is converted to bytes and appended to the packed fields.
            :return: This byte-string converted to a bytes object.
            :rtype: bytes
            """
            packed = pack(preamble, *(getattr(self, key) for key in fields.keys()))
            if payload:
                packed += bytes(self.payload)
            return packed

        def __len__(self):
            """
            Compute and return the length of the byte-string.
            That is the size of the preamble + the length of the payload (if there is a payload).
            :return: The length of the byte string.
            :rtype: int
            """
            s = preamble_size
            if payload:
                s += len(self.payload)
            return s

    # set the given options as attributes of the _Bytestr
    for k, v in options.items():
        setattr(_Bytestr, k, v)

    return _Bytestr
