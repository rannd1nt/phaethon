"""
Digital Data and Information Dimension Module.

This module provides units for measuring digital storage and information entropy.
It safely handles the mathematical distinctions between base-10 SI decimal bytes 
(e.g., Kilobyte, Megabyte) and base-2 IEC binary bytes (e.g., Kibibyte, Mebibyte).
The absolute base unit for this dimension is the Byte (B).
"""

from ..core.base import BaseUnit
from ..core import axioms as axiom
from ..core import constants as const


@axiom.bound(min_val=0, msg="Data size cannot be negative!")
class DataUnit(BaseUnit):
    """
    The primary parent class for all digital information and data storage units.
    The base unit is Byte (B).
    """
    dimension = "data"


# =========================================================================
# 1. BITS & NIBBLE
# =========================================================================
class Bit(DataUnit):
    symbol = "b"
    aliases = ["bit", "bits", "bps"]
    base_multiplier = const.BYTES_PER_BIT

class Nibble(DataUnit):
    symbol = "nibble"
    aliases = ["nibbles"]
    base_multiplier = const.BYTES_PER_NIBBLE

class Byte(DataUnit):
    """The fundamental base unit for the data dimension."""
    symbol = "B"
    aliases = ["byte", "bytes", "Bps"]
    base_multiplier = 1.0


# =========================================================================
# 2. METRIC / SI BYTES (Base 10 / 1000)
# (Scientific notation '1eX' is mathematically standard and clean here)
# =========================================================================
class Kilobyte(DataUnit):
    symbol = "KB"
    aliases = ["kilobyte", "kilobytes", "kbyte", "KBps"]
    base_multiplier = 1e3

class Megabyte(DataUnit):
    symbol = "MB"
    aliases = ["megabyte", "megabytes", "mbyte", "MBps"]
    base_multiplier = 1e6

class Gigabyte(DataUnit):
    symbol = "GB"
    aliases = ["gigabyte", "gigabytes", "gbyte", "GBps"]
    base_multiplier = 1e9

class Terabyte(DataUnit):
    symbol = "TB"
    aliases = ["terabyte", "terabytes", "tbyte", "TBps"]
    base_multiplier = 1e12

class Petabyte(DataUnit):
    symbol = "PB"
    aliases = ["petabyte", "petabytes", "pbyte", "PBps"]
    base_multiplier = 1e15


# =========================================================================
# 3. BINARY / IEC BYTES (Base 2 / 1024)
# =========================================================================
class Kibibyte(DataUnit):
    symbol = "KiB"
    aliases = ["kibibyte", "kibibytes", "kib"]
    base_multiplier = const.IEC_BASE

class Mebibyte(DataUnit):
    symbol = "MiB"
    aliases = ["mebibyte", "mebibytes", "mib"]
    base_multiplier = const.IEC_BASE ** 2

class Gibibyte(DataUnit):
    symbol = "GiB"
    aliases = ["gibibyte", "gibibytes", "gib"]
    base_multiplier = const.IEC_BASE ** 3

class Tebibyte(DataUnit):
    symbol = "TiB"
    aliases = ["tebibyte", "tebibytes", "tib"]
    base_multiplier = const.IEC_BASE ** 4

class Pebibyte(DataUnit):
    symbol = "PiB"
    aliases = ["pebibyte", "pebibytes", "pib"]
    base_multiplier = const.IEC_BASE ** 5


# =========================================================================
# 4. METRIC BITS
# =========================================================================
class Kilobit(DataUnit):
    symbol = "Kb"
    aliases = ["kilobit", "kilobits", "kbit", "kbps"]
    # 1000 bits converted to Bytes
    base_multiplier = 1e3 * const.BYTES_PER_BIT

class Megabit(DataUnit):
    symbol = "Mb"
    aliases = ["megabit", "megabits", "mbit", "mbps"]
    base_multiplier = 1e6 * const.BYTES_PER_BIT

class Gigabit(DataUnit):
    symbol = "Gb"
    aliases = ["gigabit", "gigabits", "gbit", "gbps"]
    base_multiplier = 1e9 * const.BYTES_PER_BIT

class Terabit(DataUnit):
    symbol = "Tb"
    aliases = ["terabit", "terabits", "tbit", "tbps"]
    base_multiplier = 1e12 * const.BYTES_PER_BIT