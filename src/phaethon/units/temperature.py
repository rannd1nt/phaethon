"""
Temperature and Thermodynamic Dimension Module.

This module defines scales for measuring thermal energy. 
It utilizes mathematical shift operations and absolute boundary _constraints 
to prevent violations of physical laws (e.g., dropping below Absolute Zero).
While Kelvin is the absolute thermodynamic baseline, Celsius operates 
as the practical 1:1 scaling reference.
"""

from ..core.base import BaseUnit
from ..core import axioms as _axiom
from ..core import constants as _const

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
@_axiom.bound(min_val=_const.ABSOLUTE_ZERO_C, msg=f"Temperature cannot drop below Absolute Zero ({_const.ABSOLUTE_ZERO_C} °C)!")
class Celsius(TemperatureUnit):
    symbol = "°C"
    aliases = [
        "C", "c", "celsius", "celcius", "°c", 
        "degC", "deg C", "deg c", "degree C", "degrees C",
        "degree celsius", "degrees celsius"
    ]
    base_offset = 0.0
    base_multiplier = 1.0


# =========================================================================
# 2. FAHRENHEIT
# =========================================================================
@_axiom.bound(min_val=_const.ABSOLUTE_ZERO_F, msg=f"Physics Violation: Temperature cannot drop below Absolute Zero ({_const.ABSOLUTE_ZERO_F} °F)!")
class Fahrenheit(TemperatureUnit):
    symbol = "°F"
    aliases = [
        "F", "f", "fahrenheit", "°f", 
        "degF", "deg F", "deg f", "degree F", "degrees F",
        "degree fahrenheit", "degrees fahrenheit"
    ]
    # Offset: Minus freezing point
    base_offset = -_const.FAHRENHEIT_OFFSET
    base_multiplier = 5.0 / 9.0


# =========================================================================
# 3. KELVIN (ABSOLUTE THERMODYNAMIC SCALE)
# =========================================================================
@_axiom.bound(min_val=_const.ABSOLUTE_ZERO_K, msg=f"Physics Violation: Temperature cannot drop below Absolute Zero ({_const.ABSOLUTE_ZERO_K} K)!")
class Kelvin(TemperatureUnit):
    symbol = "K"
    aliases = [
        "k", "kelvin", "kelvins", "°K", "°k", 
        "degK", "deg K", "degree K", "degrees K"
    ]
    # Secara teknis penulisan °K itu salah dalam fisika, tapi user sering mengetiknya.
    # Kita masukkan ke aliases untuk memaafkan kesalahan mereka di pipeline.
    base_offset = -_const.ZERO_CELSIUS_K
    base_multiplier = 1.0


# =========================================================================
# 4. RANKINE
# =========================================================================
@_axiom.bound(min_val=_const.ABSOLUTE_ZERO_K, msg=f"Physics Violation: Temperature cannot drop below Absolute Zero ({_const.ABSOLUTE_ZERO_K} °R)!")
class Rankine(TemperatureUnit):
    symbol = "°R"
    aliases = [
        "R", "r", "Ra", "ra", "rankine", "°r", "°Ra",
        "degR", "deg R", "degree R", "degrees R"
    ]
    base_offset = -_const.RANKINE_OFFSET
    base_multiplier = 5.0 / 9.0


# =========================================================================
# 5. REAUMUR
# =========================================================================
@_axiom.bound(min_val=_const.ABSOLUTE_ZERO_RE, msg=f"Physics Violation: Temperature cannot drop below Absolute Zero ({_const.ABSOLUTE_ZERO_RE} °Re)!")
class Reaumur(TemperatureUnit):
    symbol = "°Re"
    aliases = [
        "Re", "re", "reaumur", "réaumur", "°re", "°ré",
        "degRe", "deg Re", "degree Re", "degrees Re"
    ]
    base_offset = 0.0
    # Multiplier: 5/4 = 1.25
    base_multiplier = 1.25