"""
Energy and Work Dimension Module.

This module defines units representing the capacity to do work or produce heat.
It covers mechanical work, electrical energy, thermodynamics, food energy, 
and quantum physics (e.g., Joules, Calories, Watt-hours, Electronvolts).
The absolute base unit for this dimension is the Joule (J).
"""

from ..core.base import BaseUnit
from ..core.axioms import Axiom

from .force import Newton, PoundForce
from .length import Meter, Foot

axiom = Axiom()

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
@axiom.derive(mul=[4.184, Joule])
class Calorie(EnergyUnit):
    symbol = "cal"
    aliases = ["calorie", "calories", "gram calorie"]

@axiom.derive(mul=[4184.0, Joule])
class Kilocalorie(EnergyUnit):
    symbol = "kcal"
    aliases = ["kilocalorie", "kilocalories", "food calorie", "Cal"]


# =========================================================================
# 3. ELECTRICAL ENERGY
# =========================================================================
# Watt-hour is defined as 3600 Joules (1 Watt = 1 J/s, multiplied by 3600 s)
@axiom.derive(mul=[3600.0, Joule])
class WattHour(EnergyUnit):
    symbol = "Wh"
    aliases = ["watt-hour", "watthour", "watt hours"]

@axiom.derive(mul=[3.6e6, Joule])
class KilowattHour(EnergyUnit):
    symbol = "kWh"
    aliases = ["kilowatt-hour", "kilowatt hour", "kilowatt hours", "kwh"]

@axiom.derive(mul=[3.6e9, Joule])
class MegawattHour(EnergyUnit):
    symbol = "MWh"
    aliases = ["megawatt-hour", "megawatt hour", "megawatt hours"]


# =========================================================================
# 4. IMPERIAL / US CUSTOMARY & HVAC
# =========================================================================
# British Thermal Unit (International Table): Standard for room air conditioning
@axiom.derive(mul=[1055.05585262, Joule])
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
@axiom.derive(mul=[1.602176634e-19, Joule])
class Electronvolt(EnergyUnit):
    symbol = "eV"
    aliases = ["electronvolt", "electronvolts", "ev"]