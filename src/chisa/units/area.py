"""
Area Dimension Module.

This module defines units for measuring two-dimensional physical surfaces. 
It encompasses squared linear lengths (e.g., Square Meter, Square Inch) 
as well as specialized geographical and land measurement units (e.g., Hectare, Acre).
The absolute base unit for this dimension is the Square Meter (m²).
"""

from ..core.base import BaseUnit
from ..core import axioms as _axiom
from ..core import constants as _const
from .length import Meter, Centimeter, Millimeter, Kilometer, Inch, Foot, Yard, Mile


@_axiom.bound(min_val=0, msg="Area cannot be negative!")
class AreaUnit(BaseUnit):
    """The primary parent class for the Area dimension. The base unit is Square Meter (m²)."""
    dimension = "area"


# =========================================================================
# 1. SQUARE LENGTHS 
# =========================================================================
@_axiom.derive(mul=[Meter, Meter])
class SquareMeter(AreaUnit):
    symbol = "m²"
    aliases = [
        "m2", "m^2", "m**2", "sqm", "sq m", "sq.m.", "sq. m.",
        "square meter", "square meters", "square metre", "square metres"
    ]

@_axiom.derive(mul=[Centimeter, Centimeter])
class SquareCentimeter(AreaUnit):
    symbol = "cm²"
    aliases = [
        "cm2", "cm^2", "sqcm", "sq cm", "sq.cm.", "sq. cm.",
        "square centimeter", "square centimeters", "square centimetre", "square centimetres"
    ]

@_axiom.derive(mul=[Millimeter, Millimeter])
class SquareMillimeter(AreaUnit):
    symbol = "mm²"
    aliases = [
        "mm2", "mm^2", "sqmm", "sq mm", "sq.mm.", "sq. mm.",
        "square millimeter", "square millimeters", "square millimetre", "square millimetres"
    ]

@_axiom.derive(mul=[Kilometer, Kilometer])
class SquareKilometer(AreaUnit):
    symbol = "km²"
    aliases = [
        "km2", "km^2", "sqkm", "sq km", "sq.km.", "sq. km.",
        "square kilometer", "square kilometers", "square kilometre", "square kilometres"
    ]

@_axiom.derive(mul=[Inch, Inch])
class SquareInch(AreaUnit):
    symbol = "sq_in"
    aliases = [
        "in²", "in2", "in^2", "sq in", "sq.in.", "sq. in.",
        "square inch", "square inches"
    ]

@_axiom.derive(mul=[Foot, Foot])
class SquareFoot(AreaUnit):
    symbol = "sq_ft"
    aliases = [
        "ft²", "ft2", "ft^2", "sq ft", "sq.ft.", "sq. ft.",
        "square foot", "square feet"
    ]

@_axiom.derive(mul=[Yard, Yard])
class SquareYard(AreaUnit):
    symbol = "sq_yd"
    aliases = [
        "yd²", "yd2", "yd^2", "sq yd", "sq.yd.", "sq. yd.",
        "square yard", "square yards"
    ]

@_axiom.derive(mul=[Mile, Mile])
class SquareMile(AreaUnit):
    symbol = "sq_mi"
    aliases = [
        "mi²", "mi2", "mi^2", "sq mi", "sq.mi.", "sq. mi.",
        "square mile", "square miles"
    ]


# =========================================================================
# 2. LAND / GEOGRAPHICAL AREA
# =========================================================================
class Hectare(AreaUnit):
    symbol = "ha"
    aliases = ["hectare", "hectares"]
    base_multiplier = _const.HECTARE_TO_SQ_METER

class Are(AreaUnit):
    symbol = "a"
    aliases = ["are", "ares"]
    base_multiplier = _const.ARE_TO_SQ_METER

class Acre(AreaUnit):
    symbol = "ac"
    aliases = ["acre", "acres"]
    base_multiplier = _const.ACRE_TO_SQ_METER