"""
Temperature and Thermodynamic Dimension Module.

Kelvin is the absolute thermodynamic baseline (Multiplier=1.0, Offset=0.0).
All other scales are mathematically shifted relative to absolute zero.
Essential for Physics-Informed Neural Networks to prevent exploding gradients.
"""

from .. base import BaseUnit
from .. import axioms as _axiom

@_axiom.bound(abstract=True)
class TemperatureUnit(BaseUnit):
    """The primary parent class for the Temperature dimension."""
    dimension = "temperature"

    @property
    def isabsolute(self) -> bool:
        """Returns True if the scale starts at absolute zero (e.g., Kelvin, Rankine)."""
        return float(self.base_offset) == 0.0

# =========================================================================
# 1. KELVIN (ABSOLUTE THERMODYNAMIC SCALE - THE BASE)
# =========================================================================
@_axiom.bound(min_val=0.0, msg="Physics Violation: Temperature cannot drop below Absolute Zero (0 K)!")
class Kelvin(TemperatureUnit):
    __base_unit__ = True
    symbol = "K"
    aliases = ["k", "kelvin", "kelvins", "°K", "°k"]
    base_offset = 0.0
    base_multiplier = 1.0

# =========================================================================
# 2. CELSIUS
# =========================================================================
@_axiom.bound(min_val=-273.15, msg="Physics Violation: Temperature cannot drop below Absolute Zero (-273.15 °C)!")
class Celsius(TemperatureUnit):
    symbol = "°C"
    aliases = ["C", "c", "celsius", "celcius", "°c", "degC"]
    base_offset = 273.15
    base_multiplier = 1.0

# =========================================================================
# 3. FAHRENHEIT
# =========================================================================
# Formula: K = (F - 32) * 5/9 + 273.15 -> (F + 459.67) * 5/9
@_axiom.bound(min_val=-459.67, msg="Physics Violation: Temperature cannot drop below Absolute Zero (-459.67 °F)!")
class Fahrenheit(TemperatureUnit):
    symbol = "°F"
    aliases = ["F", "f", "fahrenheit", "°f", "degF"]
    base_offset = 459.67
    base_multiplier = 5.0 / 9.0

# =========================================================================
# 4. RANKINE (ABSOLUTE FAHRENHEIT)
# =========================================================================
# Formula: K = R * 5/9 -> (R + 0.0) * 5/9
@_axiom.bound(min_val=0.0, msg="Physics Violation: Temperature cannot drop below Absolute Zero (0 °R)!")
class Rankine(TemperatureUnit):
    symbol = "°R"
    aliases = ["R", "r", "rankine", "°r", "degR"]
    base_offset = 0.0
    base_multiplier = 5.0 / 9.0

# =========================================================================
# 5. REAUMUR
# =========================================================================
# Formula: K = Re * 1.25 + 273.15 -> (Re + 218.52) * 1.25
@_axiom.bound(min_val=-218.52, msg="Physics Violation: Temperature cannot drop below Absolute Zero (-218.52 °Re)!")
class Reaumur(TemperatureUnit):
    symbol = "°Re"
    aliases = ["Re", "re", "reaumur", "°re", "degRe"]
    base_offset = 218.52
    base_multiplier = 1.25