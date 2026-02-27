"""
Volume and 3D Space Dimension Module.
This module measures the three-dimensional space enclosed within a boundary.
It bridges derived geometric cubic lengths (e.g., Cubic Meter, Cubic Inch)
with liquid capacity standards from metric, imperial, and US customary systems
(e.g., Liters, Gallons, Barrels).
The absolute base unit for this dimension is the Cubic Meter (m³).
"""
from ..core.base import BaseUnit
from ..core import axioms as _axiom
from ..core import constants as _const
from .length import (
    Meter, Centimeter, Millimeter, Kilometer, Decimeter,
    Inch, Foot, Yard
)

@_axiom.bound(min_val=0, msg="Volume (Space) cannot be negative!")
class VolumeUnit(BaseUnit):
    """
    The primary parent class for the Volume dimension.
    The base unit is strictly synthesized as Cubic Meter (m³).
    """
    dimension = "volume"

# =========================================================================
# 1. CUBIC LENGTHS
# =========================================================================

@_axiom.derive(mul=[Meter, Meter, Meter])
class CubicMeter(VolumeUnit):
    symbol = "m³"
    aliases = [
        "m3", "m^3", "m**3", "cu m", "cu. m.", "cum",
        "cubicmeter", "cubic meters", "cubic meter", "cubicmeters",
        "cubic metre", "cubic metres"
    ]

@_axiom.derive(mul=[Decimeter, Decimeter, Decimeter])
class CubicDecimeter(VolumeUnit):
    symbol = "dm³"
    aliases = [
        "dm3", "dm^3", "cu dm",
        "cubic decimeter", "cubic decimeters", "cubic decimetre", "cubic decimetres"
    ]

@_axiom.derive(mul=[Centimeter, Centimeter, Centimeter])
class CubicCentimeter(VolumeUnit):
    symbol = "cm³"
    aliases = [
        "cm3", "cm^3", "cc", "c.c.", "cu cm",
        "cubic centimeter", "cubic centimeters", "cubic centimetre", "cubic centimetres"
    ]

@_axiom.derive(mul=[Millimeter, Millimeter, Millimeter])
class CubicMillimeter(VolumeUnit):
    symbol = "mm³"
    aliases = [
        "mm3", "mm^3", "cu mm",
        "cubic millimeter", "cubic millimeters", "cubic millimetre", "cubic millimetres"
    ]

@_axiom.derive(mul=[Kilometer, Kilometer, Kilometer])
class CubicKilometer(VolumeUnit):
    symbol = "km³"
    aliases = [
        "km3", "km^3", "cu km",
        "cubic kilometer", "cubic kilometers", "cubic kilometre", "cubic kilometres"
    ]

@_axiom.derive(mul=[Inch, Inch, Inch])
class CubicInch(VolumeUnit):
    symbol = "in³"
    aliases = [
        "in3", "in^3", "cu in", "cu. in.", "cu_in",
        "cubic inch", "cubic inches"
    ]

@_axiom.derive(mul=[Foot, Foot, Foot])
class CubicFoot(VolumeUnit):
    symbol = "ft³"
    aliases = [
        "ft3", "ft^3", "cu ft", "cu. ft.", "cu_ft",
        "cubic foot", "cubic feet"
    ]

@_axiom.derive(mul=[Yard, Yard, Yard])
class CubicYard(VolumeUnit):
    symbol = "yd³"
    aliases = [
        "yd3", "yd^3", "cu yd", "cu. yd.", "cu_yd",
        "cubic yard", "cubic yards"
    ]

# =========================================================================
# 2. METRIC LIQUID VOLUME (Liters)
# =========================================================================

class Liter(VolumeUnit):
    symbol = "L" 
    aliases = ["l", "liter", "liters", "litre", "litres", "ltr", "ltrs"]
    base_multiplier = _const.LITER_TO_CUBIC_METER

class Hectoliter(VolumeUnit):
    symbol = "hL"
    aliases = ["hl", "hectoliter", "hectoliters", "hectolitre", "hectolitres"]
    base_multiplier = _const.LITER_TO_CUBIC_METER * 100.0

class Dekaliter(VolumeUnit):
    symbol = "daL"
    aliases = ["dal", "dekaliter", "dekaliters", "decaliter", "decaliters"]
    base_multiplier = _const.LITER_TO_CUBIC_METER * 10.0

class Deciliter(VolumeUnit):
    symbol = "dL"
    aliases = ["dl", "deciliter", "deciliters", "decilitre", "decilitres"]
    base_multiplier = _const.LITER_TO_CUBIC_METER / 10.0

class Centiliter(VolumeUnit):
    symbol = "cL"
    aliases = ["cl", "centiliter", "centiliters", "centilitre", "centilitres"]
    base_multiplier = _const.LITER_TO_CUBIC_METER / 100.0

class Milliliter(VolumeUnit):
    symbol = "mL"
    aliases = ["ml", "milliliter", "milliliters", "millilitre", "millilitres"]
    base_multiplier = _const.LITER_TO_CUBIC_METER / 1000.0

class Microliter(VolumeUnit):
    symbol = "µL"
    aliases = ["ul", "uL", "microliter", "microliters", "microlitre", "microlitres"]
    base_multiplier = _const.LITER_TO_CUBIC_METER / 1e6

class Nanoliter(VolumeUnit):
    symbol = "nL"
    aliases = ["nl", "nanoliter", "nanoliters", "nanolitre", "nanolitres"]
    base_multiplier = _const.LITER_TO_CUBIC_METER / 1e9

# =========================================================================
# 3. US CUSTOMARY & IMPERIAL LIQUID VOLUME (NIST Standards)
# =========================================================================

class USGallon(VolumeUnit):
    symbol = "gal"
    aliases = ["us gal", "us sgal", "gallon", "gallons", "us gallon", "us gallons", "gal."]
    base_multiplier = _const.US_GALLON_TO_CUBIC_METER

class USQuart(VolumeUnit):
    symbol = "qt"
    aliases = ["quart", "quarts", "qt.", "qts"]
    base_multiplier = _const.US_GALLON_TO_CUBIC_METER / 4.0

class USPint(VolumeUnit):
    symbol = "pt"
    aliases = ["pint", "pints", "pt.", "pts"]
    base_multiplier = _const.US_GALLON_TO_CUBIC_METER / 8.0

class USCup(VolumeUnit):
    symbol = "cup"
    aliases = ["cups"]
    base_multiplier = _const.US_GALLON_TO_CUBIC_METER / 16.0

class USFluidOunce(VolumeUnit):
    symbol = "fl_oz"
    aliases = ["floz", "fl oz", "fl. oz.", "fluid ounce", "fluid ounces", "oz. fl.", "oz", "ozs"]
    base_multiplier = _const.US_GALLON_TO_CUBIC_METER / 128.0

class USTablespoon(VolumeUnit):
    symbol = "tbsp"
    aliases = ["tablespoon", "tablespoons", "tbsp.", "tbs", "T", "Tbs"]
    base_multiplier = _const.US_GALLON_TO_CUBIC_METER / 256.0

class USTeaspoon(VolumeUnit):
    symbol = "tsp"
    aliases = ["teaspoon", "teaspoons", "tsp.", "t", "tspn"]
    base_multiplier = _const.US_GALLON_TO_CUBIC_METER / 768.0

class UKGallon(VolumeUnit):
    symbol = "uk_gal"
    aliases = ["uk gal", "uk-gal", "gal-uk", "imperial gallon", "imperial gallons"]
    base_multiplier = _const.UK_GALLON_TO_CUBIC_METER

class OilBarrel(VolumeUnit):
    symbol = "bbl"
    aliases = ["barrel", "barrels", "oil barrel", "bbls", "oil barrels"]
    base_multiplier = _const.US_GALLON_TO_CUBIC_METER * 42.0