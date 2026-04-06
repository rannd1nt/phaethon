"""
Digital Data and Information Dimension Module.

This module provides units for measuring digital storage and information entropy.
It safely handles the mathematical distinctions between base-10 SI decimal bytes 
(e.g., Kilobyte, Megabyte) and base-2 IEC binary bytes (e.g., Kibibyte, Mebibyte).
The absolute base unit for this dimension is the Byte (B).
"""

from ..base import BaseUnit
from .. import axioms as _axiom
from .scalar import SymbolData
from .time import Second
from .. import constants as _const

@_axiom.bound(min_val=0, msg="Data size cannot be negative!", abstract=True)
class DataUnit(BaseUnit):
    """
    The primary parent class for all digital information and data storage units.
    The base unit is Byte (B).
    """
    dimension = "data"

    def bin(self) -> 'DataUnit':
        """
        Auto-scales the data size to the most appropriate Binary/IEC unit (KiB, MiB, GiB, etc.).
        Base multiplier: 1024.
        """
        import math
        bytes_val = float(self._to_base_value())
        
        if bytes_val == 0:
            return self.to("B")
            
        power = int(math.floor(math.log(abs(bytes_val), 1024)))
        power = max(0, min(power, 8))
        
        iec_map = {
            0: 'B', 1: 'KiB', 2: 'MiB', 3: 'GiB', 
            4: 'TiB', 5: 'PiB', 6: 'EiB', 7: 'ZiB', 8: 'YiB'
        }
        return self.to(iec_map[power])

    def dec(self) -> 'DataUnit':
        """
        Auto-scales the data size to the most appropriate Decimal/SI unit (KB, MB, GB, etc.).
        Base multiplier: 1000.
        """
        import math
        bytes_val = float(self._to_base_value())
        
        if bytes_val == 0:
            return self.to("B")
            
        power = int(math.floor(math.log(abs(bytes_val), 1000)))
        power = max(0, min(power, 10))
        
        si_map = {
            0: 'B', 1: 'KB', 2: 'MB', 3: 'GB', 4: 'TB', 5: 'PB', 
            6: 'EB', 7: 'ZB', 8: 'YB', 9: 'RB', 10: 'QB'
        }
        return self.to(si_map[power])

# =========================================================================
# 1. BITS, NIBBLE, & BASE BYTE
# =========================================================================
class Byte(DataUnit):
    """The fundamental base unit for the data dimension."""
    __base_unit__ = True
    symbol = "B"
    aliases = ["byte", "bytes"]
    base_multiplier = 1.0

@_axiom.derive(_const.BYTES_PER_BIT * Byte)
class Bit(DataUnit):
    symbol = "b"
    aliases = ["bit", "bits"]

@_axiom.derive(_const.BYTES_PER_NIBBLE * Byte)
class Nibble(DataUnit):
    symbol = "nibble"
    aliases = ["nibbles", "nybble", "nybbles"]

# =========================================================================
# 2. METRIC / SI BYTES (Base 10 / 1000)
# =========================================================================
@_axiom.derive(1e3 * Byte)
class Kilobyte(DataUnit):
    symbol = "KB"
    aliases = ["kB", "kilobyte", "kilobytes", "kbyte", "kbytes"]

@_axiom.derive(1e6 * Byte)
class Megabyte(DataUnit):
    symbol = "MB"
    aliases = ["megabyte", "megabytes", "mbyte", "mbytes"]

@_axiom.derive(1e9 * Byte)
class Gigabyte(DataUnit):
    symbol = "GB"
    aliases = ["gigabyte", "gigabytes", "gbyte", "gbytes"]

@_axiom.derive(1e12 * Byte)
class Terabyte(DataUnit):
    symbol = "TB"
    aliases = ["terabyte", "terabytes", "tbyte", "tbytes"]

@_axiom.derive(1e15 * Byte)
class Petabyte(DataUnit):
    symbol = "PB"
    aliases = ["petabyte", "petabytes", "pbyte", "pbytes"]

@_axiom.derive(1e18 * Byte)
class Exabyte(DataUnit):
    symbol = "EB"
    aliases = ["exabyte", "exabytes", "ebyte", "ebytes"]

@_axiom.derive(1e21 * Byte)
class Zettabyte(DataUnit):
    symbol = "ZB"
    aliases = ["zettabyte", "zettabytes", "zbyte", "zbytes"]

@_axiom.derive(1e24 * Byte)
class Yottabyte(DataUnit):
    symbol = "YB"
    aliases = ["yottabyte", "yottabytes", "ybyte", "ybytes"]

@_axiom.derive(1e27 * Byte)
class Ronnabyte(DataUnit):
    symbol = "RB"
    aliases = ["ronnabyte", "ronnabytes", "rbyte", "rbytes"]

@_axiom.derive(1e30 * Byte)
class Quettabyte(DataUnit):
    symbol = "QB"
    aliases = ["quettabyte", "quettabytes", "qbyte", "qbytes"]

# =========================================================================
# 3. BINARY / IEC BYTES (Base 2 / 1024)
# =========================================================================
@_axiom.derive((_const.IEC_BASE ** 1) * Byte)
class Kibibyte(DataUnit):
    symbol = "KiB"
    aliases = ["kibibyte", "kibibytes", "kib"]

@_axiom.derive((_const.IEC_BASE ** 2) * Byte)
class Mebibyte(DataUnit):
    symbol = "MiB"
    aliases = ["mebibyte", "mebibytes", "mib"]

@_axiom.derive((_const.IEC_BASE ** 3) * Byte)
class Gibibyte(DataUnit):
    symbol = "GiB"
    aliases = ["gibibyte", "gibibytes", "gib"]

@_axiom.derive((_const.IEC_BASE ** 4) * Byte)
class Tebibyte(DataUnit):
    symbol = "TiB"
    aliases = ["tebibyte", "tebibytes", "tib"]

@_axiom.derive((_const.IEC_BASE ** 5) * Byte)
class Pebibyte(DataUnit):
    symbol = "PiB"
    aliases = ["pebibyte", "pebibytes", "pib"]

@_axiom.derive((_const.IEC_BASE ** 6) * Byte)
class Exbibyte(DataUnit):
    symbol = "EiB"
    aliases = ["exbibyte", "exbibytes", "eib"]

@_axiom.derive((_const.IEC_BASE ** 7) * Byte)
class Zebibyte(DataUnit):
    symbol = "ZiB"
    aliases = ["zebibyte", "zebibytes", "zib"]

@_axiom.derive((_const.IEC_BASE ** 8) * Byte)
class Yobibyte(DataUnit):
    symbol = "YiB"
    aliases = ["yobibyte", "yobibytes", "yib"]

# =========================================================================
# 4. METRIC BITS
# =========================================================================
@_axiom.derive(1e3 * Bit)
class Kilobit(DataUnit):
    symbol = "Kb"
    aliases = ["kilobit", "kilobits", "kbit", "kbits"]

@_axiom.derive(1e6 * Bit)
class Megabit(DataUnit):
    symbol = "Mb"
    aliases = ["megabit", "megabits", "mbit", "mbits"]

@_axiom.derive(1e9 * Bit)
class Gigabit(DataUnit):
    symbol = "Gb"
    aliases = ["gigabit", "gigabits", "gbit", "gbits"]

@_axiom.derive(1e12 * Bit)
class Terabit(DataUnit):
    symbol = "Tb"
    aliases = ["terabit", "terabits", "tbit", "tbits"]

@_axiom.derive(1e15 * Bit)
class Petabit(DataUnit):
    symbol = "Pb"
    aliases = ["petabit", "petabits", "pbit", "pbits"]

@_axiom.derive(1e18 * Bit)
class Exabit(DataUnit):
    symbol = "Eb"
    aliases = ["exabit", "exabits", "ebit", "ebits"]

@_axiom.derive(1e21 * Bit)
class Zettabit(DataUnit):
    symbol = "Zb"
    aliases = ["zettabit", "zettabits", "zbit", "zbits"]

@_axiom.derive(1e24 * Bit)
class Yottabit(DataUnit):
    symbol = "Yb"
    aliases = ["yottabit", "yottabits", "ybit", "ybits"]

@_axiom.derive(1e27 * Bit)
class Ronnabit(DataUnit):
    symbol = "Rb"
    aliases = ["ronnabit", "ronnabits", "rbit", "rbits"]

@_axiom.derive(1e30 * Bit)
class Quettabit(DataUnit):
    symbol = "Qb"
    aliases = ["quettabit", "quettabits", "qbit", "qbits"]

# BAUD RATE UNIT

@_axiom.bound(min_val=0, abstract=True)
class BaudRateUnit(BaseUnit):
    """Measures symbol rate in telecommunications."""
    dimension = "baud_rate"

@_axiom.derive(SymbolData / Second)
class Baud(BaudRateUnit):
    __base_unit__ = True
    symbol = "Bd"
    aliases = ["bd", "baud", "symbols_per_second"]

@_axiom.derive(1e3 * Baud)
class Kilobaud(BaudRateUnit):
    symbol = "kBd"
    aliases = ["kbd", "kilobaud"]

@_axiom.derive(1e6 * Baud)
class Megabaud(BaudRateUnit):
    symbol = "MBd"
    aliases = ["mbd", "megabaud"]

@_axiom.derive(1e9 * Baud)
class Gigabaud(BaudRateUnit):
    symbol = "GBd"
    aliases = ["gbd", "gigabaud"]