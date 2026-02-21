"""
Area Dimension Module.

This module defines units for measuring two-dimensional physical surfaces. 
It encompasses squared linear lengths (e.g., Square Meter, Square Inch) 
as well as specialized geographical and land measurement units (e.g., Hectare, Acre).
The absolute base unit for this dimension is the Square Meter (m²).
"""

from ..core.base import BaseUnit
from ..core.axioms import Axiom
from .length import Meter, Centimeter, Millimeter, Kilometer, Inch, Foot, Yard, Mile

axiom = Axiom()

@axiom.bound(min_val=0, msg="Area cannot be negative!")
class AreaUnit(BaseUnit):
    """The primary parent class for the Area dimension. The base unit is Square Meter (m²)."""
    dimension = "area"


# =========================================================================
# 1. SQUARE LENGTHS 
# =========================================================================
@axiom.derive(mul=[Meter, Meter])
class SquareMeter(AreaUnit):
    symbol = "m²"
    aliases = ["sqm", "square meter", "square meters"]

@axiom.derive(mul=[Centimeter, Centimeter])
class SquareCentimeter(AreaUnit):
    symbol = "cm²"
    aliases = ["sqcm", "square centimeter", "square centimeters"]

@axiom.derive(mul=[Millimeter, Millimeter])
class SquareMillimeter(AreaUnit):
    symbol = "mm²"
    aliases = ["sqmm", "square millimeter"]

@axiom.derive(mul=[Kilometer, Kilometer])
class SquareKilometer(AreaUnit):
    symbol = "km²"
    aliases = ["sqkm", "square kilometer", "square kilometers"]

@axiom.derive(mul=[Inch, Inch])
class SquareInch(AreaUnit):
    symbol = "sq in"
    aliases = ["in²", "square inch", "square inches"]

@axiom.derive(mul=[Foot, Foot])
class SquareFoot(AreaUnit):
    symbol = "sq ft"
    aliases = ["ft²", "square foot", "square feet"]

@axiom.derive(mul=[Yard, Yard])
class SquareYard(AreaUnit):
    symbol = "sq yd"
    aliases = ["yd²", "square yard", "square yards"]

@axiom.derive(mul=[Mile, Mile])
class SquareMile(AreaUnit):
    symbol = "sq mi"
    aliases = ["mi²", "square mile", "square miles"]


# =========================================================================
# 2. LAND / GEOGRAPHICAL AREA
# =========================================================================
class Hectare(AreaUnit):
    symbol = "ha"
    aliases = ["hectare", "hectares"]
    base_multiplier = 10000.0

class Are(AreaUnit):
    symbol = "a"
    aliases = ["are", "ares"]
    base_multiplier = 100.0

class Acre(AreaUnit):
    symbol = "ac"
    aliases = ["acre", "acres"]
    base_multiplier = 4046.8564224