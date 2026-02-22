"""
Length and Distance Dimension Module.

This module defines units for measuring one-dimensional physical space. 
It spans an extreme range of magnitudes, from microscopic and atomic scales 
(e.g., Nanometer, Angstrom) to human-scale imperial/metric systems, up to 
astronomical distances (e.g., Light Year, Parsec).
The absolute base unit for this dimension is the Meter (m).
"""

from ..core.base import BaseUnit
from ..core import axioms as axiom
from ..core import constants as const

@axiom.bound(min_val=0, msg="Length cannot be a negative value.")
class LengthUnit(BaseUnit):
    """
    The primary parent class for the Length dimension.
    The base unit is Meter (m).
    """
    dimension = "length"


# =========================================================================
# 1. METRIC UNITS (SI)
# (Metric is intrinsically base-10, so magic numbers are acceptable here)
# =========================================================================
class Meter(LengthUnit):
    symbol = "m"
    aliases = ["meter", "meters"]
    base_multiplier = 1.0

class Kilometer(LengthUnit):
    symbol = "km"
    aliases = ["kilometer", "kilometers"]
    base_multiplier = 1000.0

class Decimeter(LengthUnit):
    symbol = "dm"
    aliases = ["decimeter", "decimeters"]
    base_multiplier = 1e-1

class Centimeter(LengthUnit):
    symbol = "cm"
    aliases = ["centimeter", "centimeters"]
    base_multiplier = 1e-2

class Millimeter(LengthUnit):
    symbol = "mm"
    aliases = ["millimeter", "millimeters"]
    base_multiplier = 1e-3

class Micrometer(LengthUnit):
    symbol = "um"
    aliases = ["µm", "micrometer", "micrometers"]
    base_multiplier = 1e-6

class Nanometer(LengthUnit):
    symbol = "nm"
    aliases = ["nanometer", "nanometers"]
    base_multiplier = 1e-9

class Picometer(LengthUnit):
    symbol = "pm"
    aliases = ["picometer", "picometers"]
    base_multiplier = 1e-12

class Femtometer(LengthUnit):
    symbol = "fm"
    aliases = ["femtometer", "fermi"]
    base_multiplier = 1e-15

class Angstrom(LengthUnit):
    symbol = "Å"
    aliases = ["angstrom"]
    base_multiplier = 1e-10


# =========================================================================
# 2. ASTRONOMICAL UNITS
# =========================================================================
class LightYear(LengthUnit):
    symbol = "ly"
    aliases = ["lightyear", "lightyears"]
    base_multiplier = const.LIGHT_YEAR_METER

class AstronomicalUnit(LengthUnit):
    symbol = "au"
    aliases = ["astronomicalunit", "astronomicalunits"]
    base_multiplier = const.ASTRONOMICAL_UNIT_METER

class Parsec(LengthUnit):
    symbol = "pc"
    aliases = ["parsec", "parsecs"]
    base_multiplier = const.PARSEC_METER


# =========================================================================
# 3. IMPERIAL / US UNITS
# =========================================================================
class Inch(LengthUnit):
    symbol = "in"
    aliases = ["inch", "inches"]
    base_multiplier = const.INCH_TO_METER

class Foot(LengthUnit):
    symbol = "ft"
    aliases = ["foot", "feet"]
    base_multiplier = const.FOOT_TO_METER

class Yard(LengthUnit):
    symbol = "yd"
    aliases = ["yard", "yards"]
    # 1 Yard = 3 Feet
    base_multiplier = const.FOOT_TO_METER * 3.0

class Mile(LengthUnit):
    symbol = "mi"
    aliases = ["mile", "miles"]
    base_multiplier = const.MILE_TO_METER

class NauticalMile(LengthUnit):
    symbol = "nmi"
    aliases = ["nauticalmile", "nauticalmiles"]
    base_multiplier = const.NAUTICAL_MILE_TO_METER

class Mil(LengthUnit):
    symbol = "mil"
    aliases = ["thou"]
    # 1 Mil = 1/1000 Inch
    base_multiplier = const.INCH_TO_METER / 1000.0

class League(LengthUnit):
    symbol = "league"
    aliases = ["leagues"]
    # 1 League = 3 Miles
    base_multiplier = const.MILE_TO_METER * 3.0

class Hand(LengthUnit):
    symbol = "hand"
    aliases = ["hands"]
    # 1 Hand = 4 Inches
    base_multiplier = const.INCH_TO_METER * 4.0

class Barleycorn(LengthUnit):
    symbol = "barleycorn"
    aliases = ["barleycorns"]
    # 1 Barleycorn = 1/3 Inch
    base_multiplier = const.INCH_TO_METER / 3.0


# =========================================================================
# 4. ENGINEERING / SURVEY UNITS
# =========================================================================
class Chain(LengthUnit):
    symbol = "chain"
    aliases = ["chains"]
    # 1 Chain = 66 Feet
    base_multiplier = const.FOOT_TO_METER * 66.0

class Link(LengthUnit):
    symbol = "link"
    aliases = ["links"]
    # 1 Link = 0.66 Feet
    base_multiplier = const.FOOT_TO_METER * 0.66

class Rod(LengthUnit):
    symbol = "rod"
    aliases = ["rods", "pole", "poles", "perch", "perches"]
    # 1 Rod = 16.5 Feet
    base_multiplier = const.FOOT_TO_METER * 16.5

class Furlong(LengthUnit):
    symbol = "furlong"
    aliases = ["furlongs"]
    # 1 Furlong = 660 Feet
    base_multiplier = const.FOOT_TO_METER * 660.0


# =========================================================================
# 5. TYPOGRAPHIC UNITS
# =========================================================================
class Point(LengthUnit):
    symbol = "pt"
    aliases = ["point", "points"]
    # DTP Point = 1/72 Inch
    base_multiplier = const.INCH_TO_METER / 72.0

class Pica(LengthUnit):
    symbol = "pica"
    aliases = ["picas"]
    # 1 Pica = 1/6 Inch (or 12 Points)
    base_multiplier = const.INCH_TO_METER / 6.0