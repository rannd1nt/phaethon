"""
Kinematics: Acceleration Dimension Module.

Defines the rate of change of velocity per unit of time.
"""
from ..base import BaseUnit
from .. import axioms as _axiom
from .length import Meter, Kilometer, Foot
from .time import Second, Hour

@_axiom.bound(abstract=True)
class AccelerationUnit(BaseUnit):
    dimension = "acceleration"

# =========================================================================
# 1. SI & METRIC UNITS
# =========================================================================

# Menggunakan Sintaks Dimensional Synthesis yang baru! (Lebih bersih)
@_axiom.derive(Meter / (Second ** 2))
class MeterPerSecondSquared(AccelerationUnit):
    __base_unit__ = True
    symbol = "m/s²"
    aliases = ["m/s2", "meter_per_second_squared"]

@_axiom.derive(Kilometer / (Hour ** 2))
class KilometerPerHourSquared(AccelerationUnit):
    symbol = "km/h²"
    aliases = ["km/h2", "kilometer_per_hour_squared"]

@_axiom.derive(0.01 * MeterPerSecondSquared)
class Galileo(AccelerationUnit):
    symbol = "Gal"
    aliases = ["gal", "galileo", "cm/s²", "centimeter_per_second_squared"]

# =========================================================================
# 2. GRAVITY & IMPERIAL UNITS
# =========================================================================

@_axiom.derive(9.80665 * MeterPerSecondSquared)
class StandardGravity(AccelerationUnit):
    """Standard acceleration due to gravity on Earth."""
    symbol = "g"
    aliases = ["g_force", "gforce", "gravity"]

@_axiom.derive(Foot / (Second ** 2))
class FootPerSecondSquared(AccelerationUnit):
    symbol = "ft/s²"
    aliases = ["ft/s2", "foot_per_second_squared"]