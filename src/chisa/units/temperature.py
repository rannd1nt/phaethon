"""
Temperature and Thermodynamic Dimension Module.

This module defines scales for measuring thermal energy. 
It utilizes mathematical shift operations and absolute boundary constraints 
to prevent violations of physical laws (e.g., dropping below Absolute Zero).
While Kelvin is the absolute thermodynamic baseline, Celsius operates 
as the practical 1:1 scaling reference.
"""

from decimal import Decimal
from ..core.base import BaseUnit
from ..core.axioms import Axiom

axiom = Axiom()

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
@axiom.bound(min_val=-273.15, msg="Temperature cannot drop below Absolute Zero (-273.15 °C)!")
class Celsius(TemperatureUnit):
    symbol = "c"
    aliases = ["celsius", "celcius", "°c"]
    base_offset = 0.0
    base_multiplier = 1.0


# =========================================================================
# 2. FAHRENHEIT
# =========================================================================
@axiom.bound(min_val=-459.67, msg="Physics Violation: Temperature cannot drop below Absolute Zero (-459.67 °F)!")
class Fahrenheit(TemperatureUnit):
    symbol = "f"
    aliases = ["fahrenheit", "°f"]
    base_offset = -32.0
    base_multiplier = Decimal('5') / Decimal('9')


# =========================================================================
# 3. KELVIN (ABSOLUTE THERMODYNAMIC SCALE)
# =========================================================================
@axiom.bound(min_val=0, msg="Physics Violation: Temperature cannot drop below Absolute Zero (0 K)!")
class Kelvin(TemperatureUnit):
    symbol = "k"
    aliases = ["kelvin", "°k"]
    base_offset = -273.15
    base_multiplier = 1.0


# =========================================================================
# 4. RANKINE
# =========================================================================
@axiom.bound(min_val=0, msg="Physics Violation: Temperature cannot drop below Absolute Zero (0 °R)!")
class Rankine(TemperatureUnit):
    symbol = "r"
    aliases = ["rankine", "°r"]
    base_offset = -491.67
    base_multiplier = Decimal('5') / Decimal('9')


# =========================================================================
# 5. REAUMUR
# =========================================================================
@axiom.bound(min_val=-218.52, msg="Physics Violation: Temperature cannot drop below Absolute Zero (-218.52 °Re)!")
class Reaumur(TemperatureUnit):
    symbol = "re"
    aliases = ["reaumur", "réaumur", "°re", "°ré"]
    base_offset = 0.0
    base_multiplier = 1.25