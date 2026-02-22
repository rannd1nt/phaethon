"""
Energy and Work Dimension Module.

This module defines units representing the capacity to do work or produce heat.
It covers mechanical work, electrical energy, thermodynamics, food energy, 
and quantum physics (e.g., Joules, Calories, Watt-hours, Electronvolts).
The absolute base unit for this dimension is the Joule (J).
"""

from ..core.base import BaseUnit
from ..core import axioms as axiom
from ..core import constants as const

from .force import Newton, PoundForce
from .length import Meter, Foot


@axiom.bound(min_val=0, msg="Absolute energy (scalar) cannot have a negative value.")
class EnergyUnit(BaseUnit):
    """The primary parent class for Energy and Work dimensions. The base unit is Joule (J)."""
    dimension = "energy"


# =========================================================================
# 1. SI / METRIC UNITS (Mechanical Energy)
# =========================================================================
# Joule: 1 Newton * 1 Meter
@axiom.derive(mul=[Newton, Meter])
class Joule(EnergyUnit):
    symbol = "J"
    aliases = ["joule", "joules"]

@axiom.derive(mul=[1e3, Joule])
class Kilojoule(EnergyUnit):
    symbol = "kJ"
    aliases = ["kilojoule", "kilojoules"]

@axiom.derive(mul=[1e6, Joule])
class Megajoule(EnergyUnit):
    symbol = "MJ"
    aliases = ["megajoule", "megajoules"]

@axiom.derive(mul=[1e9, Joule])
class Gigajoule(EnergyUnit):
    symbol = "GJ"
    aliases = ["gigajoule", "gigajoules"]


# =========================================================================
# 2. THERMODYNAMICS & FOOD (Calories)
# =========================================================================
@axiom.derive(mul=[const.CALORIE_TO_JOULE, Joule])
class Calorie(EnergyUnit):
    symbol = "cal"
    aliases = ["calorie", "calories", "gram calorie"]

@axiom.derive(mul=[const.CALORIE_TO_JOULE * 1000.0, Joule])
class Kilocalorie(EnergyUnit):
    symbol = "kcal"
    aliases = ["kilocalorie", "kilocalories", "food calorie", "Cal"]


# =========================================================================
# 3. ELECTRICAL ENERGY
# =========================================================================
# Watt-hour is defined as 1 Watt over 1 Hour
@axiom.derive(mul=[const.HOUR_TO_SECOND, Joule])
class WattHour(EnergyUnit):
    symbol = "Wh"
    aliases = ["watt-hour", "watthour", "watt hours"]

@axiom.derive(mul=[const.HOUR_TO_SECOND * 1000.0, Joule])
class KilowattHour(EnergyUnit):
    symbol = "kWh"
    aliases = ["kilowatt-hour", "kilowatt hour", "kilowatt hours", "kwh"]

@axiom.derive(mul=[const.HOUR_TO_SECOND * 1e6, Joule])
class MegawattHour(EnergyUnit):
    symbol = "MWh"
    aliases = ["megawatt-hour", "megawatt hour", "megawatt hours"]


# =========================================================================
# 4. IMPERIAL / US CUSTOMARY & HVAC
# =========================================================================
# British Thermal Unit (International Table)
@axiom.derive(mul=[const.BTU_TO_JOULE, Joule])
class BTU(EnergyUnit):
    symbol = "BTU"
    aliases = ["btu", "british thermal unit"]

# Foot-pound force: Imperial mechanical work (1 lbf applied over 1 foot)
@axiom.derive(mul=[PoundForce, Foot])
class FootPound(EnergyUnit):
    symbol = "ft-lbf"
    aliases = ["foot-pound", "foot-pounds", "ft·lbf", "ftlbf"]


# =========================================================================
# 5. QUANTUM / ATOMIC PHYSICS
# =========================================================================
# Electronvolt: Kinetic energy gained by a single electron
@axiom.derive(mul=[const.ELECTRON_VOLT_TO_JOULE, Joule])
class Electronvolt(EnergyUnit):
    symbol = "eV"
    aliases = ["electronvolt", "electronvolts", "ev"]