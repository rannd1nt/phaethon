"""
Frequency Dimension Module.

This module defines units for measuring the rate of repeating events.
It covers electromagnetic frequencies (Hertz) and mechanical rotational 
speeds (RPM).
The absolute base unit for this dimension is Hertz (Hz), which is 1/Second.
"""

from .. base import BaseUnit
from .. import axioms as _axiom
from .scalar import Cycle
from .time import Second

@_axiom.bound(min_val=0, msg="Frequency cannot be a negative value.", abstract=True)
class FrequencyUnit(BaseUnit):
    """The primary parent class for the Frequency dimension. Base: Hertz (Hz)."""
    dimension = "frequency"

    @property
    def period(self):
        """Returns the time period (1/f) as a TimeUnit object."""
        from .time import Second
        if self.mag == 0:
            raise ZeroDivisionError("Frequency is 0; period is infinite.")
        
        hz_val = self.to('Hz').mag
        return Second(1.0 / hz_val, context=self.context)

# =========================================================================
# 1. SI UNITS (HERTZ)
# =========================================================================
@_axiom.derive(Cycle / Second)
class Hertz(FrequencyUnit):
    __base_unit__ = True
    symbol = "Hz"
    aliases = ["hz", "hertz", "cycle per second", "cycles per second", "cps"]

class Kilohertz(FrequencyUnit):
    symbol = "kHz"
    aliases = ["khz", "kilohertz"]
    base_multiplier = 1e3

class Megahertz(FrequencyUnit):
    symbol = "MHz"
    aliases = ["mhz", "megahertz"]
    base_multiplier = 1e6

class Gigahertz(FrequencyUnit):
    symbol = "GHz"
    aliases = ["ghz", "gigahertz"]
    base_multiplier = 1e9

class Terahertz(FrequencyUnit):
    symbol = "THz"
    aliases = ["thz", "terahertz"]
    base_multiplier = 1e12

class Petahertz(FrequencyUnit):
    symbol = "PHz"
    aliases = ["phz", "petahertz"]
    base_multiplier = 1e15

class Exahertz(FrequencyUnit):
    symbol = "EHz"
    aliases = ["ehz", "exahertz"]
    base_multiplier = 1e18

class Zettahertz(FrequencyUnit):
    symbol = "ZHz"
    aliases = ["zhz", "zettahertz"]
    base_multiplier = 1e21

class Yottahertz(FrequencyUnit):
    symbol = "YHz"
    aliases = ["yhz", "yottahertz"]
    base_multiplier = 1e24

class Ronnahertz(FrequencyUnit):
    symbol = "RHz"
    aliases = ["rhz", "ronnahertz"]
    base_multiplier = 1e27

class Quettahertz(FrequencyUnit):
    symbol = "QHz"
    aliases = ["qhz", "quettahertz"]
    base_multiplier = 1e30

# =========================================================================
# 2. MECHANICAL & BIOLOGICAL
# =========================================================================
class RevolutionsPerMinute(FrequencyUnit):
    symbol = "RPM"
    aliases = ["rpm", "r/min", "rev/min", "revolutions per minute"]
    # 1 RPM = 1 cycle / 60 seconds
    base_multiplier = 1.0 / 60.0

class BeatsPerMinute(FrequencyUnit):
    symbol = "BPM"
    aliases = ["bpm", "beats per minute"]
    base_multiplier = 1.0 / 60.0