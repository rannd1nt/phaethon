"""
Density Dimension Module.

This module defines units for mass density (mass per unit volume).
It is highly critical for fluid dynamics, material science, and logistics.
The absolute base unit for this dimension is Kilogram per Cubic Meter (kg/m³).
"""

from .. base import BaseUnit
from .. import axioms as _axiom
from .mass import Kilogram, Gram, Pound
from .length import Meter, Centimeter
from .scalar import Count
from .volume import CubicMeter, CubicCentimeter, CubicFoot, USGallon


@_axiom.bound(min_val=0, msg="Density cannot be a negative value.", abstract=True)
class DensityUnit(BaseUnit):
    """The primary parent class for the Density dimension. Base: kg/m³."""
    dimension = "density"

# =========================================================================
# 1. METRIC DENSITY
# =========================================================================
@_axiom.derive(Kilogram / CubicMeter)
class KilogramPerCubicMeter(DensityUnit):
    __base_unit__ = True
    symbol = "kg/m³"
    aliases = ["kg/m3", "kg/m^3", "kilogram per cubic meter"]

@_axiom.derive(Gram / CubicCentimeter)
class GramPerCubicCentimeter(DensityUnit):
    symbol = "g/cm³"
    aliases = [
        "g/cm3", "g/cm^3", "g/cc", 
        "gram per cubic centimeter", "grams per cubic centimeter"
    ]

# =========================================================================
# 2. IMPERIAL / US CUSTOMARY DENSITY
# =========================================================================
@_axiom.derive(Pound / CubicFoot)
class PoundPerCubicFoot(DensityUnit):
    symbol = "lb/ft³"
    aliases = [
        "lb/ft3", "lb/ft^3", "lbs/ft3", "pcf", 
        "pound per cubic foot", "pounds per cubic foot"
    ]

@_axiom.derive(Pound / USGallon)
class PoundPerGallon(DensityUnit):
    symbol = "lb/gal"
    aliases = [
        "ppg", "lbs/gal", "pound per gallon", "pounds per gallon"
    ]

# Number Density

@_axiom.bound(min_val=0, abstract=True)
class NumberDensityUnit(BaseUnit):
    """Measures concentration of discrete items/particles in a volume."""
    dimension = "number_density"

@_axiom.derive(Count / (Meter ** 3))
class ParticlesPerCubicMeter(NumberDensityUnit):
    __base_unit__ = True
    symbol = "m⁻³"
    aliases = ["particles_per_cubic_meter", "count_per_m3"]

@_axiom.derive(Count / (Centimeter ** 3))
class ParticlesPerCubicCentimeter(NumberDensityUnit):
    symbol = "cm⁻³"
    aliases = ["particles_per_cubic_centimeter", "count_per_cm3"]