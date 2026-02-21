"""
Length and Distance Dimension Module.

This module defines units for measuring one-dimensional physical space. 
It spans an extreme range of magnitudes, from microscopic and atomic scales 
(e.g., Nanometer, Angstrom) to human-scale imperial/metric systems, up to 
astronomical distances (e.g., Light Year, Parsec).
The absolute base unit for this dimension is the Meter (m).
"""

from ..core.base import BaseUnit
from ..core.axioms import Axiom

axiom = Axiom()

@axiom.bound(min_val=0, msg="Length cannot be a negative value.")
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
    aliases = ["meter", "meters"]
    base_multiplier = 1.0

class Picometer(LengthUnit):
    symbol = "pm"
    aliases = ["picometer", "picometers"]
    base_multiplier = 1e-12

class Nanometer(LengthUnit):
    symbol = "nm"
    aliases = ["nanometer", "nanometers"]
    base_multiplier = 1e-9

class Micrometer(LengthUnit):
    symbol = "um"
    aliases = ["µm", "micrometer", "micrometers"]
    base_multiplier = 1e-6

class Millimeter(LengthUnit):
    symbol = "mm"
    aliases = ["millimeter", "millimeters"]
    base_multiplier = 1e-3

class Centimeter(LengthUnit):
    symbol = "cm"
    aliases = ["centimeter", "centimeters"]
    base_multiplier = 1e-2

class Decimeter(LengthUnit):
    symbol = "dm"
    aliases = ["decimeter", "decimeters"]
    base_multiplier = 1e-1

class Kilometer(LengthUnit):
    symbol = "km"
    aliases = ["kilometer", "kilometers"]
    base_multiplier = 1000.0

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
    base_multiplier = 9460730472580800.0

class AstronomicalUnit(LengthUnit):
    symbol = "au"
    aliases = ["astronomicalunit", "astronomicalunits"]
    base_multiplier = 149597870700.0

class Parsec(LengthUnit):
    symbol = "pc"
    aliases = ["parsec", "parsecs"]
    base_multiplier = 3.085677581491367e16


# =========================================================================
# 3. ENGINEERING UNITS
# =========================================================================
class Chain(LengthUnit):
    symbol = "chain"
    aliases = ["chains"]
    base_multiplier = 20.1168

class Link(LengthUnit):
    symbol = "link"
    aliases = ["links"]
    base_multiplier = 0.201168

class Rod(LengthUnit):
    symbol = "rod"
    aliases = ["rods", "pole", "poles", "perch", "perches"]
    base_multiplier = 5.0292

class Furlong(LengthUnit):
    symbol = "furlong"
    aliases = ["furlongs"]
    base_multiplier = 201.168


# =========================================================================
# 4. IMPERIAL / US UNITS
# =========================================================================
class Inch(LengthUnit):
    symbol = "in"
    aliases = ["inch", "inches"]
    base_multiplier = 0.0254

class Foot(LengthUnit):
    symbol = "ft"
    aliases = ["foot", "feet"]
    base_multiplier = 0.3048

class Yard(LengthUnit):
    symbol = "yd"
    aliases = ["yard", "yards"]
    base_multiplier = 0.9144

class Mile(LengthUnit):
    symbol = "mi"
    aliases = ["mile", "miles"]
    base_multiplier = 1609.344

class NauticalMile(LengthUnit):
    symbol = "nmi"
    aliases = ["nauticalmile", "nauticalmiles"]
    base_multiplier = 1852.0

class Mil(LengthUnit):
    symbol = "mil"
    aliases = ["thou"]
    base_multiplier = 0.0000254

class League(LengthUnit):
    symbol = "league"
    aliases = ["leagues"]
    base_multiplier = 4828.032

class Hand(LengthUnit):
    symbol = "hand"
    aliases = ["hands"]
    base_multiplier = 0.1016

class Barleycorn(LengthUnit):
    symbol = "barleycorn"
    aliases = ["barleycorns"]
    base_multiplier = 0.00847


# =========================================================================
# 5. TYPOGRAPHIC UNITS
# =========================================================================
class Point(LengthUnit):
    symbol = "pt"
    aliases = ["point", "points"]
    base_multiplier = 0.000352778

class Pica(LengthUnit):
    symbol = "pica"
    aliases = ["picas"]
    base_multiplier = 0.004233333


# =========================================================================
# 6. MICROSCOPIC UNITS
# =========================================================================
class Femtometer(LengthUnit):
    symbol = "fm"  # Standard SI symbol for femtometer
    aliases = ["femtometer", "fermi"]
    base_multiplier = 1e-15