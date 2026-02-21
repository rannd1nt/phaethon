"""
Volume and 3D Space Dimension Module.

This module measures the three-dimensional space enclosed within a boundary.
It bridges derived geometric cubic lengths (e.g., Cubic Meter, Cubic Inch) 
with liquid capacity standards from metric, imperial, and US customary systems 
(e.g., Liters, Gallons, Barrels).
The absolute base unit for this dimension is the Cubic Meter (m³).
"""

from ..core.base import BaseUnit
from ..core.axioms import Axiom
from .length import (
    Meter, Centimeter, Millimeter, Kilometer, Decimeter,
    Inch, Foot, Yard
)

axiom = Axiom()

@axiom.bound(min_val=0, msg="Volume (Space) cannot be negative!")
class VolumeUnit(BaseUnit):
    """
    The primary parent class for the Volume dimension.
    The base unit is strictly synthesized as Cubic Meter (m³).
    """
    dimension = "volume"


# =========================================================================
# 1. CUBIC LENGTHS
# =========================================================================
@axiom.derive(mul=[Meter, Meter, Meter])
class CubicMeter(VolumeUnit):
    symbol = "m³"
    aliases = ["m3", "cubicmeter", "cubic meters", "cubic meter", "cubicmeters"]

@axiom.derive(mul=[Decimeter, Decimeter, Decimeter])
class CubicDecimeter(VolumeUnit):
    symbol = "dm³"
    aliases = ["dm3", "cubic decimeter", "cubic decimeters"]

@axiom.derive(mul=[Centimeter, Centimeter, Centimeter])
class CubicCentimeter(VolumeUnit):
    symbol = "cm³"
    aliases = ["cm3", "cc", "cubic centimeter", "cubic centimeters", "cubic centimetre"]

@axiom.derive(mul=[Millimeter, Millimeter, Millimeter])
class CubicMillimeter(VolumeUnit):
    symbol = "mm³"
    aliases = ["mm3", "cubic millimeter", "cubic millimeters"]

@axiom.derive(mul=[Kilometer, Kilometer, Kilometer])
class CubicKilometer(VolumeUnit):
    symbol = "km³"
    aliases = ["km3", "cubic kilometer", "cubic kilometers"]

@axiom.derive(mul=[Inch, Inch, Inch])
class CubicInch(VolumeUnit):
    symbol = "in³"
    aliases = ["in3", "cubic inch", "cubic inches"]

@axiom.derive(mul=[Foot, Foot, Foot])
class CubicFoot(VolumeUnit):
    symbol = "ft³"
    aliases = ["ft3", "cubic foot", "cubic feet"]

@axiom.derive(mul=[Yard, Yard, Yard])
class CubicYard(VolumeUnit):
    symbol = "yd³"
    aliases = ["yd3", "cubic yard", "cubic yards"]


# =========================================================================
# 2. METRIC LIQUID VOLUME (Liters)
# =========================================================================
class Liter(VolumeUnit):
    symbol = "l"
    aliases = ["liter", "liters", "litre"]
    base_multiplier = 1e-3

class Hectoliter(VolumeUnit):
    symbol = "hl"
    aliases = ["hectoliter", "hectoliters"]
    base_multiplier = 0.1

class Dekaliter(VolumeUnit):
    symbol = "dal"
    aliases = ["dekaliter", "dekaliters"]
    base_multiplier = 1e-2

class Deciliter(VolumeUnit):
    symbol = "dl"
    aliases = ["deciliter", "deciliters"]
    base_multiplier = 1e-4

class Centiliter(VolumeUnit):
    symbol = "cl"
    aliases = ["centiliter", "centiliters"]
    base_multiplier = 1e-5

class Milliliter(VolumeUnit):
    symbol = "ml"
    aliases = ["milliliter", "milliliters"]
    base_multiplier = 1e-6

class Microliter(VolumeUnit):
    symbol = "µl"
    aliases = ["ul", "microliter", "microliters"]
    base_multiplier = 1e-9

class Nanoliter(VolumeUnit):
    symbol = "nl"
    aliases = ["nanoliter", "nanoliters"]
    base_multiplier = 1e-12


# =========================================================================
# 3. US CUSTOMARY & IMPERIAL LIQUID VOLUME (NIST Standards)
# =========================================================================
class USGallon(VolumeUnit):
    symbol = "gal"
    aliases = ["us sgal", "gallon", "gallons", "us gal"]
    base_multiplier = 3.785411784e-3

class USQuart(VolumeUnit):
    symbol = "qt"
    aliases = ["quart", "quarts"]
    base_multiplier = 9.4635295e-4

class USPint(VolumeUnit):
    symbol = "pt"
    aliases = ["pint", "pints"]
    base_multiplier = 4.73176475e-4

class USCup(VolumeUnit):
    symbol = "cup"
    aliases = ["cups"]
    base_multiplier = 2.365882375e-4

class USFluidOunce(VolumeUnit):
    symbol = "floz"
    aliases = ["fl oz", "fluid ounce", "fluid ounces"]
    base_multiplier = 2.95735295625e-5

class USTablespoon(VolumeUnit):
    symbol = "tbsp"
    aliases = ["tablespoon", "tablespoons"]
    base_multiplier = 1.478676478125e-5

class USTeaspoon(VolumeUnit):
    symbol = "tsp"
    aliases = ["teaspoon", "teaspoons"]
    base_multiplier = 4.92892159375e-6

class UKGallon(VolumeUnit):
    symbol = "uk gal"
    aliases = ["uk-gal", "gal-uk", "imperial gallon", "imperial gallons"]
    base_multiplier = 4.54609e-3

class OilBarrel(VolumeUnit):
    symbol = "bbl"
    aliases = ["barrel", "barrels", "oil barrel"]
    base_multiplier = 0.158987294928