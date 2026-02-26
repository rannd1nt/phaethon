"""
Frequency Dimension Module.

This module defines units for measuring the rate of repeating events.
It covers electromagnetic frequencies (Hertz) and mechanical rotational 
speeds (RPM).
The absolute base unit for this dimension is Hertz (Hz), which is 1/Second.
"""

from ..core.base import BaseUnit
from ..core import axioms as _axiom

@_axiom.bound(min_val=0, msg="Frequency cannot be a negative value.")
class FrequencyUnit(BaseUnit):
    """The primary parent class for the Frequency dimension. Base: Hertz (Hz)."""
    dimension = "frequency"

# =========================================================================
# 1. SI UNITS (HERTZ)
# =========================================================================
class Hertz(FrequencyUnit):
    symbol = "Hz"
    aliases = ["hz", "hertz", "cycle per second", "cycles per second", "cps"]
    base_multiplier = 1.0

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