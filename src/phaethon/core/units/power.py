"""
Power Dimension Module.

This module measures the rate of energy transfer or work done over time.
It includes standard electrical/mechanical power (Watts), automotive mechanics 
(Horsepower), and standard HVAC/refrigeration capacities (BTU/h, Tons of Refrigeration).
The absolute base unit for this dimension is the Watt (W).
"""

from .. base import BaseUnit
from .. import axioms as _axiom

from .energy import Joule, FootPound, BTU
from .time import Second, Hour
from .force import KilogramForce
from .length import Meter


@_axiom.bound(min_val=0, msg="Power magnitude cannot be negative.", abstract=True)
class PowerUnit(BaseUnit):
    """The primary parent class for the Power dimension. The base unit is Watt (W)."""
    dimension = "power"


# =========================================================================
# 1. SI / METRIC UNITS (Electrical & Mechanical)
# =========================================================================
# Watt: 1 Joule per Second
@_axiom.derive(Joule / Second)
class Watt(PowerUnit):
    __base_unit__ = True
    symbol = "W"
    aliases = ["w", "watt", "watts", "j/s", "joule/s", "joule per second"]

@_axiom.derive(1e-3 * Watt)
class Milliwatt(PowerUnit):
    symbol = "mW"
    aliases = ["mw", "milliwatt", "milliwatts"]

@_axiom.derive(1e3 * Watt)
class Kilowatt(PowerUnit):
    symbol = "kW"
    aliases = ["kw", "kilowatt", "kilowatts"]

@_axiom.derive(1e6 * Watt)
class Megawatt(PowerUnit):
    symbol = "MW"
    aliases = ["mw", "megawatt", "megawatts"]

@_axiom.derive(1e9 * Watt)
class Gigawatt(PowerUnit):
    symbol = "GW"
    aliases = ["gw", "gigawatt", "gigawatts"]

@_axiom.derive(1e12 * Watt)
class Terawatt(PowerUnit):
    symbol = "TW"
    aliases = ["tw", "terawatt", "terawatts"]

@_axiom.derive(1e15 * Watt)
class Petawatt(PowerUnit):
    symbol = "PW"
    aliases = ["pw", "petawatt", "petawatts"]

@_axiom.derive(1e18 * Watt)
class Exawatt(PowerUnit):
    symbol = "EW"
    aliases = ["ew", "exawatt", "exawatts"]

@_axiom.derive(1e21 * Watt)
class Zettawatt(PowerUnit):
    symbol = "ZW"
    aliases = ["zw", "zettawatt", "zettawatts"]

@_axiom.derive(1e24 * Watt)
class Yottawatt(PowerUnit):
    symbol = "YW"
    aliases = ["yw", "yottawatt", "yottawatts"]

@_axiom.derive(1e27 * Watt)
class Ronnawatt(PowerUnit):
    symbol = "RW"
    aliases = ["rw", "ronnawatt", "ronnawatts"]

@_axiom.derive(1e30 * Watt)
class Quettawatt(PowerUnit):
    symbol = "QW"
    aliases = ["qw", "quettawatt", "quettawatts"]

# =========================================================================
# 2. HORSEPOWER
# =========================================================================
# Mechanical Horsepower (Imperial): Defined as 550 foot-pounds per second.
@_axiom.derive(550 * FootPound / Second)
class Horsepower(PowerUnit):
    symbol = "hp"
    aliases = ["horsepower", "mechanical horsepower", "imperial horsepower", "bhp"]

@_axiom.derive(75 * KilogramForce * Meter / Second)
class MetricHorsepower(PowerUnit):
    symbol = "PS"
    aliases = ["ps", "metric horsepower", "metric hp", "ch", "pk", "cv"]


# =========================================================================
# 3. HVAC / REFRIGERATION
# =========================================================================
# BTU per hour: Standard for Air Conditioner cooling capacity.
@_axiom.derive(BTU / Hour)
class BTUPerHour(PowerUnit):
    symbol = "BTU/h"
    aliases = ["btu/h", "btuh", "btu per hour", "btu/hr"]

@_axiom.derive(12000 * BTUPerHour)
class TonOfRefrigeration(PowerUnit):
    symbol = "TR"
    aliases = ["tr", "ton of refrigeration", "tons of refrigeration", "rt"]

# =========================================================================
# 4. LOGARITHMIC POWER SCALES (TELECOM & RF)
# =========================================================================
@_axiom.logarithmic(reference=Watt(1), multiplier=10.0)
class DecibelWatt(PowerUnit):
    symbol = "dBW"
    aliases = ["dbw"]

@_axiom.logarithmic(reference=Milliwatt(1), multiplier=10.0)
class DecibelMilliwatt(PowerUnit):
    symbol = "dBm"
    aliases = ["dbm"]