"""
Temperature and Thermodynamic Dimension Module.

This module defines scales for measuring thermal energy. 
It utilizes mathematical shift operations and absolute boundary constraints 
to prevent violations of physical laws (e.g., dropping below Absolute Zero).
While Kelvin is the absolute thermodynamic baseline, Celsius operates 
as the practical 1:1 scaling reference.
"""

from ..core.base import BaseUnit
from ..core import axioms as axiom
from ..core import constants as const

class TemperatureUnit(BaseUnit):
    """
    The primary parent class for the Temperature dimension.
    While Kelvin is the absolute thermodynamic baseline, Celsius operates 
    as the practical reference point with a 1.0 multiplier and 0.0 offset.
    """
    dimension = "temperature"


# =========================================================================
# 1. CELSIUS (BASE REFERENCE)
# =========================================================================
@axiom.bound(min_val=const.ABSOLUTE_ZERO_C, msg=f"Temperature cannot drop below Absolute Zero ({const.ABSOLUTE_ZERO_C} °C)!")
class Celsius(TemperatureUnit):
    symbol = "c"
    aliases = ["celsius", "celcius", "°c"]
    base_offset = 0.0
    base_multiplier = 1.0


# =========================================================================
# 2. FAHRENHEIT
# =========================================================================
@axiom.bound(min_val=const.ABSOLUTE_ZERO_F, msg=f"Physics Violation: Temperature cannot drop below Absolute Zero ({const.ABSOLUTE_ZERO_F} °F)!")
class Fahrenheit(TemperatureUnit):
    symbol = "f"
    aliases = ["fahrenheit", "°f"]
    # Offset: Minus freezing point
    base_offset = -const.FAHRENHEIT_OFFSET
    base_multiplier = 5.0 / 9.0


# =========================================================================
# 3. KELVIN (ABSOLUTE THERMODYNAMIC SCALE)
# =========================================================================
@axiom.bound(min_val=const.ABSOLUTE_ZERO_K, msg=f"Physics Violation: Temperature cannot drop below Absolute Zero ({const.ABSOLUTE_ZERO_K} K)!")
class Kelvin(TemperatureUnit):
    symbol = "k"
    aliases = ["kelvin", "°k"]
    base_offset = -const.ZERO_CELSIUS_K
    base_multiplier = 1.0


# =========================================================================
# 4. RANKINE
# =========================================================================
@axiom.bound(min_val=const.ABSOLUTE_ZERO_K, msg=f"Physics Violation: Temperature cannot drop below Absolute Zero ({const.ABSOLUTE_ZERO_K} °R)!")
class Rankine(TemperatureUnit):
    symbol = "r"
    aliases = ["rankine", "°r"]
    base_offset = -const.RANKINE_OFFSET
    base_multiplier = 5.0 / 9.0


# =========================================================================
# 5. REAUMUR
# =========================================================================
@axiom.bound(min_val=const.ABSOLUTE_ZERO_RE, msg=f"Physics Violation: Temperature cannot drop below Absolute Zero ({const.ABSOLUTE_ZERO_RE} °Re)!")
class Reaumur(TemperatureUnit):
    symbol = "re"
    aliases = ["reaumur", "réaumur", "°re", "°ré"]
    base_offset = 0.0
    # Multiplier: 5/4 = 1.25
    base_multiplier = 1.25