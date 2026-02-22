"""
Volume and 3D Space Dimension Module.

This module measures the three-dimensional space enclosed within a boundary.
It bridges derived geometric cubic lengths (e.g., Cubic Meter, Cubic Inch) 
with liquid capacity standards from metric, imperial, and US customary systems 
(e.g., Liters, Gallons, Barrels).
The absolute base unit for this dimension is the Cubic Meter (m³).
"""

from ..core.base import BaseUnit
from ..core import axioms as axiom
from ..core import constants as const
from .length import (
    Meter, Centimeter, Millimeter, Kilometer, Decimeter,
    Inch, Foot, Yard
)

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
    base_multiplier = const.LITER_TO_CUBIC_METER

class Hectoliter(VolumeUnit):
    symbol = "hl"
    aliases = ["hectoliter", "hectoliters"]
    base_multiplier = const.LITER_TO_CUBIC_METER * 100.0

class Dekaliter(VolumeUnit):
    symbol = "dal"
    aliases = ["dekaliter", "dekaliters"]
    base_multiplier = const.LITER_TO_CUBIC_METER * 10.0

class Deciliter(VolumeUnit):
    symbol = "dl"
    aliases = ["deciliter", "deciliters"]
    base_multiplier = const.LITER_TO_CUBIC_METER / 10.0

class Centiliter(VolumeUnit):
    symbol = "cl"
    aliases = ["centiliter", "centiliters"]
    base_multiplier = const.LITER_TO_CUBIC_METER / 100.0

class Milliliter(VolumeUnit):
    symbol = "ml"
    aliases = ["milliliter", "milliliters"]
    base_multiplier = const.LITER_TO_CUBIC_METER / 1000.0

class Microliter(VolumeUnit):
    symbol = "µl"
    aliases = ["ul", "microliter", "microliters"]
    base_multiplier = const.LITER_TO_CUBIC_METER / 1e6

class Nanoliter(VolumeUnit):
    symbol = "nl"
    aliases = ["nanoliter", "nanoliters"]
    base_multiplier = const.LITER_TO_CUBIC_METER / 1e9


# =========================================================================
# 3. US CUSTOMARY & IMPERIAL LIQUID VOLUME (NIST Standards)
# =========================================================================
class USGallon(VolumeUnit):
    symbol = "gal"
    aliases = ["us sgal", "gallon", "gallons", "us gal"]
    base_multiplier = const.US_GALLON_TO_CUBIC_METER

class USQuart(VolumeUnit):
    symbol = "qt"
    aliases = ["quart", "quarts"]
    # 1 Gallon = 4 Quarts
    base_multiplier = const.US_GALLON_TO_CUBIC_METER / 4.0

class USPint(VolumeUnit):
    symbol = "pt"
    aliases = ["pint", "pints"]
    # 1 Gallon = 8 Pints
    base_multiplier = const.US_GALLON_TO_CUBIC_METER / 8.0

class USCup(VolumeUnit):
    symbol = "cup"
    aliases = ["cups"]
    # 1 Gallon = 16 Cups
    base_multiplier = const.US_GALLON_TO_CUBIC_METER / 16.0

class USFluidOunce(VolumeUnit):
    symbol = "floz"
    aliases = ["fl oz", "fluid ounce", "fluid ounces"]
    # 1 Gallon = 128 Fluid Ounces
    base_multiplier = const.US_GALLON_TO_CUBIC_METER / 128.0

class USTablespoon(VolumeUnit):
    symbol = "tbsp"
    aliases = ["tablespoon", "tablespoons"]
    # 1 Fluid Ounce = 2 Tablespoons -> 1 Gallon = 256 Tablespoons
    base_multiplier = const.US_GALLON_TO_CUBIC_METER / 256.0

class USTeaspoon(VolumeUnit):
    symbol = "tsp"
    aliases = ["teaspoon", "teaspoons"]
    # 1 Tablespoon = 3 Teaspoons -> 1 Gallon = 768 Teaspoons
    base_multiplier = const.US_GALLON_TO_CUBIC_METER / 768.0

class UKGallon(VolumeUnit):
    symbol = "uk gal"
    aliases = ["uk-gal", "gal-uk", "imperial gallon", "imperial gallons"]
    base_multiplier = const.UK_GALLON_TO_CUBIC_METER

class OilBarrel(VolumeUnit):
    symbol = "bbl"
    aliases = ["barrel", "barrels", "oil barrel"]
    # 1 Standard Oil Barrel = 42 US Gallons
    base_multiplier = const.US_GALLON_TO_CUBIC_METER * 42.0