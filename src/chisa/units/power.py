"""
Power Dimension Module.

This module measures the rate of energy transfer or work done over time.
It includes standard electrical/mechanical power (Watts), automotive mechanics 
(Horsepower), and standard HVAC/refrigeration capacities (BTU/h, Tons of Refrigeration).
The absolute base unit for this dimension is the Watt (W).
"""

from ..core.base import BaseUnit
from ..core.axioms import Axiom

from .energy import Joule, FootPound, BTU
from .time import Second, Hour
from .force import KilogramForce
from .length import Meter

axiom = Axiom()

@axiom.bound(min_val=0, msg="Power magnitude cannot be negative.")
class PowerUnit(BaseUnit):
    """The primary parent class for the Power dimension. The base unit is Watt (W)."""
    dimension = "power"


# =========================================================================
# 1. SI / METRIC UNITS (Electrical & Mechanical)
# =========================================================================
# Watt: 1 Joule per Second
@axiom.derive(mul=[Joule], div=[Second])
class Watt(PowerUnit):
    symbol = "W"
    aliases = ["watt", "watts"]

@axiom.derive(mul=[1e3, Watt])
class Kilowatt(PowerUnit):
    symbol = "kW"
    aliases = ["kilowatt", "kilowatts"]

@axiom.derive(mul=[1e6, Watt])
class Megawatt(PowerUnit):
    symbol = "MW"
    aliases = ["megawatt", "megawatts"]

@axiom.derive(mul=[1e9, Watt])
class Gigawatt(PowerUnit):
    symbol = "GW"
    aliases = ["gigawatt", "gigawatts"]


# =========================================================================
# 2. HORSEPOWER
# =========================================================================
# Mechanical Horsepower (Imperial): Defined as 550 foot-pounds per second.
# Chisa dynamically synthesizes this to ~745.6998 Watts.
@axiom.derive(mul=[550, FootPound], div=[Second])
class Horsepower(PowerUnit):
    symbol = "hp"
    aliases = ["horsepower", "mechanical horsepower", "imperial horsepower"]

# Metric Horsepower (PS / Pferdestärke): Defined as 75 kgf·m per second.
# Chisa dynamically synthesizes this to ~735.49875 Watts.
@axiom.derive(mul=[75, KilogramForce, Meter], div=[Second])
class MetricHorsepower(PowerUnit):
    symbol = "PS"
    aliases = ["ps", "metric horsepower", "ch", "pk"]


# =========================================================================
# 3. HVAC / REFRIGERATION
# =========================================================================
# BTU per hour: Standard for Air Conditioner cooling capacity.
@axiom.derive(mul=[BTU], div=[Hour])
class BTUPerHour(PowerUnit):
    symbol = "BTU/h"
    aliases = ["btu/h", "btuh", "btu per hour"]

# Ton of Refrigeration (Freezing capacity of 1 short ton of ice in 24 hours).
# Defined as exactly 12,000 BTU/h.
@axiom.derive(mul=[12000, BTUPerHour])
class TonOfRefrigeration(PowerUnit):
    symbol = "TR"
    aliases = ["tr", "ton of refrigeration", "tons of refrigeration"]