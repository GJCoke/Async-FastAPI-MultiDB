"""
Copy of the uuid6 module from the uuid6-python package.

Repo: https://github.com/oittaa/uuid6-python

Author  : Oittaa
"""

import secrets
import time
import uuid
from typing import Optional, Tuple


class UUID(uuid.UUID):
    """
    Instances of the UUID class represent UUIDs as specified in RFC 9562.

    This class allows creation of UUID objects for versions 6, 7, and 8 as defined
    in RFC 9562. It provides properties to handle time and subsecond information.

    Attributes:
        subsec: The subsecond value encoded in the UUID.
        time: The timestamp associated with the UUID, depending on the version.

    Args:
        hex (str, optional): The hexadecimal representation of the UUID.
        bytes (bytes, optional): The byte representation of the UUID.
        bytes_le (bytes, optional): The little-endian byte representation of the UUID.
        fields (Tuple[int, int, int, int, int, int], optional): The 6 integer fields that form the UUID.
        int (int, optional): The integer representation of the UUID.
        version (int, optional): The version of the UUID (6, 7, or 8).
        is_safe (uuid.SafeUUID, optional): The safety level of the UUID, default is unknown.

    Raises:
        ValueError: If the version is not 6, 7, or 8, or if the integer is out of range.
    """

    __slots__ = ()

    def __init__(
        self,
        hex: Optional[str] = None,
        bytes: Optional[bytes] = None,
        bytes_le: Optional[bytes] = None,
        fields: Optional[Tuple[int, int, int, int, int, int]] = None,
        int: Optional[int] = None,
        version: Optional[int] = None,
        *,
        is_safe: uuid.SafeUUID = uuid.SafeUUID.unknown,
    ) -> None:
        """
        Create a UUID.

        Args:
            hex (Optional[str]): Hexadecimal representation of the UUID.
            bytes (Optional[bytes]): Byte representation of the UUID.
            bytes_le (Optional[bytes]): Little-endian byte representation of the UUID.
            fields (Optional[Tuple[int, int, int, int, int, int]]): 6 integer fields that form the UUID.
            int (Optional[int]): Integer representation of the UUID.
            version (Optional[int]): The version of the UUID (6, 7, or 8).
            is_safe (uuid.SafeUUID): Safety level of the UUID.

        Raises:
            ValueError: If the integer is out of range or if the version is not 6, 7, or 8.
        """
        if int is None or [hex, bytes, bytes_le, fields].count(None) != 4:
            return super().__init__(
                hex=hex,
                bytes=bytes,
                bytes_le=bytes_le,
                fields=fields,
                int=int,
                version=version,
                is_safe=is_safe,
            )
        if not 0 <= int < 1 << 128:
            raise ValueError("int is out of range (need a 128-bit value)")
        if version is not None:
            if not 6 <= version <= 8:
                raise ValueError("illegal version number")
            # Set the variant to RFC 4122.
            int &= ~(0xC000 << 48)
            int |= 0x8000 << 48
            # Set the version number.
            int &= ~(0xF000 << 64)
            int |= version << 76
        super().__init__(int=int, is_safe=is_safe)

    @property
    def subsec(self) -> int:
        """
        Get the subsecond value encoded in the UUID.

        Returns:
            int: The subsecond part of the UUID.
        """
        return ((self.int >> 64) & 0x0FFF) << 8 | ((self.int >> 54) & 0xFF)

    @property
    def time(self) -> int:
        """
        Get the timestamp associated with the UUID.

        Returns:
            int: The timestamp based on the UUID version (6, 7, or 8).
        """
        if self.version == 6:
            return (self.time_low << 28) | (self.time_mid << 12) | (self.time_hi_version & 0x0FFF)
        if self.version == 7:
            return self.int >> 80
        if self.version == 8:
            return (self.int >> 80) * 10**6 + _subsec_decode(self.subsec)
        return super().time


def _subsec_decode(value: int) -> int:
    """
    Decode the subsecond value.

    Args:
        value (int): The subsecond value to decode.

    Returns:
        int: The decoded subsecond value.
    """
    return -(-value * 10**6 // 2**20)


def _subsec_encode(value: int) -> int:
    """
    Encode the subsecond value.

    Args:
        value (int): The subsecond value to encode.

    Returns:
        int: The encoded subsecond value.
    """
    return value * 2**20 // 10**6


def uuid1_to_uuid6(uuid1: uuid.UUID) -> UUID:
    """
    Generate a UUID version 6 object from a UUID version 1 object.

    Args:
        uuid1 (uuid.UUID): A UUID version 1 object.

    Returns:
        UUID: A UUID version 6 object.

    Raises:
        ValueError: If the given UUID is not version 1.
    """
    if uuid1.version != 1:
        raise ValueError("given UUID's version number must be 1")
    h = uuid1.hex
    h = h[13:16] + h[8:12] + h[0:5] + "6" + h[5:8] + h[16:]
    return UUID(hex=h, is_safe=uuid1.is_safe)


_last_v6_timestamp = None
_last_v7_timestamp = None
_last_v8_timestamp = None


def uuid6(node: Optional[int] = None, clock_seq: Optional[int] = None) -> UUID:
    """
    Generate a UUID version 6 object.

    UUID version 6 is a field-compatible version of UUIDv1, reordered for
    improved database locality. UUIDv6 is intended for use with systems
    that involve legacy UUIDv1 values. If possible, UUIDv7 should be used.

    Args:
        node (Optional[int]): The node value (48-bit) to use. If not provided, a random value is used.
        clock_seq (Optional[int]): The clock sequence value (14-bit). If not provided, a random value is used.

    Returns:
        UUID: A UUID version 6 object.
    """
    global _last_v6_timestamp

    nanoseconds = time.time_ns()
    timestamp = nanoseconds // 100 + 0x01B21DD213814000
    if _last_v6_timestamp is not None and timestamp <= _last_v6_timestamp:
        timestamp = _last_v6_timestamp + 1
    _last_v6_timestamp = timestamp
    if clock_seq is None:
        clock_seq = secrets.randbits(14)
    if node is None:
        node = secrets.randbits(48)
    time_high_and_time_mid = (timestamp >> 12) & 0xFFFFFFFFFFFF
    time_low_and_version = timestamp & 0x0FFF
    uuid_int = time_high_and_time_mid << 80
    uuid_int |= time_low_and_version << 64
    uuid_int |= (clock_seq & 0x3FFF) << 48
    uuid_int |= node & 0xFFFFFFFFFFFF
    return UUID(int=uuid_int, version=6)


def uuid7() -> UUID:
    """
    Generate a UUID version 7 object.

    UUID version 7 is a time-ordered UUID derived from the Unix epoch timestamp
    (milliseconds since 1970-01-01 UTC). It provides improved entropy compared
    to UUID versions 1 and 6.

    Returns:
        UUID: A UUID version 7 object.
    """
    global _last_v7_timestamp

    nanoseconds = time.time_ns()
    timestamp_ms = nanoseconds // 10**6
    if _last_v7_timestamp is not None and timestamp_ms <= _last_v7_timestamp:
        timestamp_ms = _last_v7_timestamp + 1
    _last_v7_timestamp = timestamp_ms
    uuid_int = (timestamp_ms & 0xFFFFFFFFFFFF) << 80
    uuid_int |= secrets.randbits(76)
    return UUID(int=uuid_int, version=7)


def uuid8() -> UUID:
    """
    Generate a UUID version 8 object.

    UUID version 8 is a custom UUID that uses a time-ordered value field derived
    from the Unix epoch timestamp (nanoseconds since 1970-01-01 UTC).

    Returns:
        UUID: A UUID version 8 object.
    """
    global _last_v8_timestamp

    nanoseconds = time.time_ns()
    if _last_v8_timestamp is not None and nanoseconds <= _last_v8_timestamp:
        nanoseconds = _last_v8_timestamp + 1
    _last_v8_timestamp = nanoseconds
    timestamp_ms, timestamp_ns = divmod(nanoseconds, 10**6)
    subsec = _subsec_encode(timestamp_ns)
    subsec_a = subsec >> 8
    subsec_b = subsec & 0xFF
    uuid_int = (timestamp_ms & 0xFFFFFFFFFFFF) << 80
    uuid_int |= subsec_a << 64
    uuid_int |= subsec_b << 54
    uuid_int |= secrets.randbits(54)
    return UUID(int=uuid_int, version=8)
