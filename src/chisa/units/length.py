"""
Length and Distance Dimension Module.

This module defines units for measuring one-dimensional physical space. 
It spans an extreme range of magnitudes, from microscopic and atomic scales 
(e.g., Nanometer, Angstrom) to human-scale imperial/metric systems, up to 
astronomical distances (e.g., Light Year, Parsec).
The absolute base unit for this dimension is the Meter (m).
"""

from ..core.base import BaseUnit
from ..core import axioms as _axiom
from ..core import constants as _const

@_axiom.bound(min_val=0, msg="Length cannot be a negative value.")
class LengthUnit(BaseUnit):
    """
    The primary parent class for the Length dimension.
    The base unit is Meter (m).
    """
    dimension = "length"


# =========================================================================
# 1. METRIC UNITS (SI)
# =========================================================================
class Meter(LengthUnit):
    symbol = "m"
    aliases = ["meter", "meters", "metre", "metres"]
    base_multiplier = 1.0

class Kilometer(LengthUnit):
    symbol = "km"
    aliases = ["kilometer", "kilometers", "kilometre", "kilometres"]
    base_multiplier = 1000.0

class Decimeter(LengthUnit):
    symbol = "dm"
    aliases = ["decimeter", "decimeters", "decimetre", "decimetres"]
    base_multiplier = 1e-1

class Centimeter(LengthUnit):
    symbol = "cm"
    aliases = ["centimeter", "centimeters", "centimetre", "centimetres"]
    base_multiplier = 1e-2

class Millimeter(LengthUnit):
    symbol = "mm"
    aliases = ["millimeter", "millimeters", "millimetre", "millimetres"]
    base_multiplier = 1e-3

class Micrometer(LengthUnit):
    symbol = "um"
    aliases = ["µm", "micrometer", "micrometers", "micrometre", "micrometres", "micron", "microns"]
    base_multiplier = 1e-6

class Nanometer(LengthUnit):
    symbol = "nm"
    aliases = ["nanometer", "nanometers", "nanometre", "nanometres"]
    base_multiplier = 1e-9

class Picometer(LengthUnit):
    symbol = "pm"
    aliases = ["picometer", "picometers", "picometre", "picometres"]
    base_multiplier = 1e-12

class Femtometer(LengthUnit):
    symbol = "fm"
    aliases = ["femtometer", "femtometers", "fermi", "fermis"]
    base_multiplier = 1e-15

class Angstrom(LengthUnit):
    symbol = "Å"
    aliases = ["angstrom", "angstroms", "A"] # 'A' is safe here because of expected_dim isolated context
    base_multiplier = 1e-10


# =========================================================================
# 2. ASTRONOMICAL UNITS
# =========================================================================
class LightYear(LengthUnit):
    symbol = "ly"
    aliases = ["lightyear", "lightyears", "light-year", "light-years", "light year", "light years"]
    base_multiplier = _const.LIGHT_YEAR_METER

class AstronomicalUnit(LengthUnit):
    symbol = "au"
    aliases = ["AU", "astronomicalunit", "astronomicalunits", "astronomical unit", "astronomical units"]
    base_multiplier = _const.ASTRONOMICAL_UNIT_METER

class Parsec(LengthUnit):
    symbol = "pc"
    aliases = ["parsec", "parsecs"]
    base_multiplier = _const.PARSEC_METER


# =========================================================================
# 3. IMPERIAL / US UNITS
# =========================================================================
class Inch(LengthUnit):
    symbol = "in"
    aliases = ["inch", "inches", "in.", '"', "''"]
    base_multiplier = _const.INCH_TO_METER

class Foot(LengthUnit):
    symbol = "ft"
    aliases = ["foot", "feet", "ft.", "'"]
    base_multiplier = _const.FOOT_TO_METER

class Yard(LengthUnit):
    symbol = "yd"
    aliases = ["yard", "yards", "yds", "yd."]
    base_multiplier = _const.FOOT_TO_METER * 3.0

class Mile(LengthUnit):
    symbol = "mi"
    aliases = ["mile", "miles", "mi."]
    base_multiplier = _const.MILE_TO_METER

class NauticalMile(LengthUnit):
    symbol = "nmi"
    aliases = ["nauticalmile", "nauticalmiles", "nautical mile", "nautical miles", "NM"]
    base_multiplier = _const.NAUTICAL_MILE_TO_METER

class Mil(LengthUnit):
    symbol = "mil"
    aliases = ["mils", "thou"]
    base_multiplier = _const.INCH_TO_METER / 1000.0

class League(LengthUnit):
    symbol = "league"
    aliases = ["leagues"]
    base_multiplier = _const.MILE_TO_METER * 3.0

class Hand(LengthUnit):
    symbol = "hand"
    aliases = ["hands"]
    base_multiplier = _const.INCH_TO_METER * 4.0

class Barleycorn(LengthUnit):
    symbol = "barleycorn"
    aliases = ["barleycorns"]
    base_multiplier = _const.INCH_TO_METER / 3.0


# =========================================================================
# 4. ENGINEERING / SURVEY UNITS
# =========================================================================
class Chain(LengthUnit):
    symbol = "chain"
    aliases = ["chains", "ch"]
    base_multiplier = _const.FOOT_TO_METER * 66.0

class Link(LengthUnit):
    symbol = "link"
    aliases = ["links", "l", "li"]
    base_multiplier = _const.FOOT_TO_METER * 0.66

class Rod(LengthUnit):
    symbol = "rod"
    aliases = ["rods", "pole", "poles", "perch", "perches"]
    base_multiplier = _const.FOOT_TO_METER * 16.5

class Furlong(LengthUnit):
    symbol = "furlong"
    aliases = ["furlongs", "fur"]
    base_multiplier = _const.FOOT_TO_METER * 660.0


# =========================================================================
# 5. TYPOGRAPHIC UNITS
# =========================================================================
class Point(LengthUnit):
    symbol = "pt"
    aliases = ["point", "points", "pts", "pt."]
    base_multiplier = _const.INCH_TO_METER / 72.0

class Pica(LengthUnit):
    symbol = "pica"
    aliases = ["picas"]
    base_multiplier = _const.INCH_TO_METER / 6.0