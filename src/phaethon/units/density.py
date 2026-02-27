"""
Density Dimension Module.

This module defines units for mass density (mass per unit volume).
It is highly critical for fluid dynamics, material science, and logistics.
The absolute base unit for this dimension is Kilogram per Cubic Meter (kg/m³).
"""

from ..core.base import BaseUnit
from ..core import axioms as _axiom
from .mass import Kilogram, Gram, Pound
from .volume import CubicMeter, CubicCentimeter, CubicFoot, USGallon


@_axiom.bound(min_val=0, msg="Density cannot be a negative value.")
class DensityUnit(BaseUnit):
    """The primary parent class for the Density dimension. Base: kg/m³."""
    dimension = "density"


# =========================================================================
# 1. METRIC DENSITY
# =========================================================================
@_axiom.derive(mul=[Kilogram], div=[CubicMeter])
class KilogramPerCubicMeter(DensityUnit):
    symbol = "kg/m³"
    aliases = ["kg/m3", "kg/m^3", "kilogram per cubic meter"]

@_axiom.derive(mul=[Gram], div=[CubicCentimeter])
class GramPerCubicCentimeter(DensityUnit):
    symbol = "g/cm³"
    aliases = [
        "g/cm3", "g/cm^3", "g/cc", 
        "gram per cubic centimeter", "grams per cubic centimeter"
    ]


# =========================================================================
# 2. IMPERIAL / US CUSTOMARY DENSITY
# =========================================================================
@_axiom.derive(mul=[Pound], div=[CubicFoot])
class PoundPerCubicFoot(DensityUnit):
    symbol = "lb/ft³"
    aliases = [
        "lb/ft3", "lb/ft^3", "lbs/ft3", "pcf", 
        "pound per cubic foot", "pounds per cubic foot"
    ]

@_axiom.derive(mul=[Pound], div=[USGallon])
class PoundPerGallon(DensityUnit):
    symbol = "lb/gal"
    aliases = [
        "ppg", "lbs/gal", "pound per gallon", "pounds per gallon"
    ]