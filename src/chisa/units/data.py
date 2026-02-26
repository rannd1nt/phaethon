"""
Digital Data and Information Dimension Module.

This module provides units for measuring digital storage and information entropy.
It safely handles the mathematical distinctions between base-10 SI decimal bytes 
(e.g., Kilobyte, Megabyte) and base-2 IEC binary bytes (e.g., Kibibyte, Mebibyte).
The absolute base unit for this dimension is the Byte (B).
"""

from ..core.base import BaseUnit
from ..core import axioms as _axiom
from ..core import constants as _const


@_axiom.bound(min_val=0, msg="Data size cannot be negative!")
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
    aliases = ["bit", "bits"]
    base_multiplier = _const.BYTES_PER_BIT

class Nibble(DataUnit):
    symbol = "nibble"
    aliases = ["nibbles", "nybble", "nybbles"]
    base_multiplier = _const.BYTES_PER_NIBBLE

class Byte(DataUnit):
    """The fundamental base unit for the data dimension."""
    symbol = "B"
    aliases = ["byte", "bytes"]
    base_multiplier = 1.0


# =========================================================================
# 2. METRIC / SI BYTES (Base 10 / 1000)
# =========================================================================
class Kilobyte(DataUnit):
    symbol = "KB"
    aliases = ["kB", "kilobyte", "kilobytes", "kbyte", "kbytes"]
    base_multiplier = 1e3

class Megabyte(DataUnit):
    symbol = "MB"
    aliases = ["megabyte", "megabytes", "mbyte", "mbytes"]
    base_multiplier = 1e6

class Gigabyte(DataUnit):
    symbol = "GB"
    aliases = ["gigabyte", "gigabytes", "gbyte", "gbytes"]
    base_multiplier = 1e9

class Terabyte(DataUnit):
    symbol = "TB"
    aliases = ["terabyte", "terabytes", "tbyte", "tbytes"]
    base_multiplier = 1e12

class Petabyte(DataUnit):
    symbol = "PB"
    aliases = ["petabyte", "petabytes", "pbyte", "pbytes"]
    base_multiplier = 1e15


# =========================================================================
# 3. BINARY / IEC BYTES (Base 2 / 1024)
# =========================================================================
class Kibibyte(DataUnit):
    symbol = "KiB"
    aliases = ["kibibyte", "kibibytes", "kib"]
    base_multiplier = _const.IEC_BASE

class Mebibyte(DataUnit):
    symbol = "MiB"
    aliases = ["mebibyte", "mebibytes", "mib"]
    base_multiplier = _const.IEC_BASE ** 2

class Gibibyte(DataUnit):
    symbol = "GiB"
    aliases = ["gibibyte", "gibibytes", "gib"]
    base_multiplier = _const.IEC_BASE ** 3

class Tebibyte(DataUnit):
    symbol = "TiB"
    aliases = ["tebibyte", "tebibytes", "tib"]
    base_multiplier = _const.IEC_BASE ** 4

class Pebibyte(DataUnit):
    symbol = "PiB"
    aliases = ["pebibyte", "pebibytes", "pib"]
    base_multiplier = _const.IEC_BASE ** 5


# =========================================================================
# 4. METRIC BITS
# =========================================================================
class Kilobit(DataUnit):
    symbol = "Kb"
    aliases = ["kilobit", "kilobits", "kbit", "kbits"]
    base_multiplier = 1e3 * _const.BYTES_PER_BIT

class Megabit(DataUnit):
    symbol = "Mb"
    aliases = ["megabit", "megabits", "mbit", "mbits"]
    base_multiplier = 1e6 * _const.BYTES_PER_BIT

class Gigabit(DataUnit):
    symbol = "Gb"
    aliases = ["gigabit", "gigabits", "gbit", "gbits"]
    base_multiplier = 1e9 * _const.BYTES_PER_BIT

class Terabit(DataUnit):
    symbol = "Tb"
    aliases = ["terabit", "terabits", "tbit", "tbits"]
    base_multiplier = 1e12 * _const.BYTES_PER_BIT