"""
Energy and Work Dimension Module.
This module defines units representing the capacity to do work or produce heat.
It covers mechanical work, electrical energy, thermodynamics, food energy,
and quantum physics (e.g., Joules, Calories, Watt-hours, Electronvolts).
The absolute base unit for this dimension is the Joule (J).
"""
from ..core.base import BaseUnit
from ..core import axioms as _axiom
from ..core import constants as _const
from .force import Newton, PoundForce
from .length import Meter, Foot

@_axiom.bound(min_val=0, msg="Absolute energy (scalar) cannot have a negative value.")
class EnergyUnit(BaseUnit):
    """The primary parent class for Energy and Work dimensions. The base unit is Joule (J)."""
    dimension = "energy"

# =========================================================================
# 1. SI / METRIC UNITS (Mechanical Energy)
# =========================================================================

# Joule: 1 Newton * 1 Meter
@_axiom.derive(mul=[Newton, Meter])
class Joule(EnergyUnit):
    symbol = "J"
    aliases = ["joule", "joules", "j"]

@_axiom.derive(mul=[1e3, Joule])
class Kilojoule(EnergyUnit):
    symbol = "kJ"
    aliases = ["kj", "kilojoule", "kilojoules"]

@_axiom.derive(mul=[1e6, Joule])
class Megajoule(EnergyUnit):
    symbol = "MJ"
    aliases = ["mj", "megajoule", "megajoules"]

@_axiom.derive(mul=[1e9, Joule])
class Gigajoule(EnergyUnit):
    symbol = "GJ"
    aliases = ["gj", "gigajoule", "gigajoules"]

# =========================================================================
# 2. THERMODYNAMICS & FOOD (Calories)
# =========================================================================

@_axiom.derive(mul=[_const.CALORIE_TO_JOULE, Joule])
class Calorie(EnergyUnit):
    symbol = "cal"
    aliases = ["calorie", "calories", "gram calorie", "small calorie"]

@_axiom.derive(mul=[_const.CALORIE_TO_JOULE * 1000.0, Joule])
class Kilocalorie(EnergyUnit):
    symbol = "kcal"
    aliases = [
        "Cal", "Calories", "Kcal", "kilocalorie", "kilocalories",
        "food calorie", "large calorie"
    ]

# =========================================================================
# 3. ELECTRICAL ENERGY
# =========================================================================

# Watt-hour is defined as 1 Watt over 1 Hour
@_axiom.derive(mul=[_const.HOUR_TO_SECOND, Joule])
class WattHour(EnergyUnit):
    symbol = "Wh"
    aliases = ["wh", "watt-hour", "watthour", "watt hours", "watt hour", "W h", "W.h", "w-hr"]

@_axiom.derive(mul=[_const.HOUR_TO_SECOND * 1000.0, Joule])
class KilowattHour(EnergyUnit):
    symbol = "kWh"
    aliases = [
        "kwh", "kilowatt-hour", "kilowatt hour", "kilowatt hours",
        "kW h", "kW.h", "kwhr", "kw-hr"
    ]

@_axiom.derive(mul=[_const.HOUR_TO_SECOND * 1e6, Joule])
class MegawattHour(EnergyUnit):
    symbol = "MWh"
    aliases = ["mwh", "megawatt-hour", "megawatt hour", "megawatt hours", "MW h", "mwhr", "mw-hr"]

@_axiom.derive(mul=[_const.HOUR_TO_SECOND * 1e9, Joule])
class GigawattHour(EnergyUnit):
    symbol = "GWh"
    aliases = ["gwh", "gigawatt-hour", "gigawatt hour", "gigawatt hours", "gwhr", "gw-hr"]

# =========================================================================
# 4. IMPERIAL / US CUSTOMARY & HVAC
# =========================================================================

# British Thermal Unit (International Table)
@_axiom.derive(mul=[_const.BTU_TO_JOULE, Joule])
class BTU(EnergyUnit):
    symbol = "BTU"
    aliases = ["btu", "british thermal unit", "british thermal units", "Btu", "btus"]

# MMBTU is standard in Oil & Gas (1 Million BTU)
@_axiom.derive(mul=[1e6, BTU])
class MMBTU(EnergyUnit):
    symbol = "MMBtu"
    aliases = ["mmbtu", "million btu", "million british thermal units"]

# Foot-pound force: Imperial mechanical work (1 lbf applied over 1 foot)
@_axiom.derive(mul=[PoundForce, Foot])
class FootPound(EnergyUnit):
    symbol = "ft-lbf"
    aliases = [
        "foot-pound", "foot-pounds", "ft·lbf", "ftlbf",
        "ft-lb", "ft lb", "ft lbs", "ftlb", "foot pound force"
    ]

# =========================================================================
# 5. QUANTUM / ATOMIC PHYSICS
# =========================================================================

# Electronvolt: Kinetic energy gained by a single electron
@_axiom.derive(mul=[_const.ELECTRON_VOLT_TO_JOULE, Joule])
class Electronvolt(EnergyUnit):
    symbol = "eV"
    aliases = ["ev", "electronvolt", "electronvolts", "electron-volt", "e.V."]