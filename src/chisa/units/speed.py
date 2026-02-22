"""
Speed and Velocity Dimension Module.

This module measures the rate of change of position over time.
It supports linear velocities (m/s, mph), nautical speeds (Knots), 
cosmic constants (Speed of Light), and dynamically scaled environmental 
speeds (Mach, dependent on temperature).
The absolute base unit for this dimension is Meters per Second (m/s).
"""
from ..core.base import BaseUnit
from ..core import axioms as axiom
from ..core import constants as const
from ..core import vmath
from .temperature import Kelvin


@axiom.bound(min_val=0, msg="Speed (scalar magnitude) cannot be negative!")
class SpeedUnit(BaseUnit):
    """
    The primary parent class for the Speed dimension.
    The absolute base unit is Meter per Second (m/s).
    """
    dimension = "speed"

@axiom.prepare(temperature=Kelvin)
def _calc_mach_scale(temperature = const.STANDARD_ATMOSPHERE_TEMP_K) -> float:
    safe_temp = vmath.maximum(temperature, const.ABSOLUTE_ZERO_K)
    return const.SPEED_OF_SOUND_0C * vmath.sqrt(safe_temp / const.ZERO_CELSIUS_K)


# =========================================================================
# 1. METRIC UNITS (Base: Meters per second)
# =========================================================================
class MeterPerSecond(SpeedUnit):
    symbol = "m/s"
    aliases = ["meter per second", "meters per second"]
    base_multiplier = 1.0

class MeterPerMinute(SpeedUnit):
    symbol = "m/min"
    aliases = ["meter per minute", "meters per minute"]
    base_multiplier = 1.0 / 60.0

class KilometerPerHour(SpeedUnit):
    symbol = "km/h"
    aliases = ["kph", "kilometer per hour", "kilometers per hour", "km per hour"]
    base_multiplier = 1000.0 / 3600.0

class MillimeterPerSecond(SpeedUnit):
    symbol = "mm/s"
    aliases = ["millimeter per second", "millimeters per second", "mm per second"]
    base_multiplier = 0.001

class MillimeterPerMinute(SpeedUnit):
    symbol = "mm/min"
    aliases = ["millimeter per minute", "millimeters per minute", "mm per minute"]
    base_multiplier = 0.001 / 60.0

class CentimeterPerSecond(SpeedUnit):
    symbol = "cm/s"
    aliases = ["centimeter per second", "centimeters per second", "cm per second"]
    base_multiplier = 0.01

class CentimeterPerMinute(SpeedUnit):
    symbol = "cm/min"
    aliases = ["centimeter per minute", "centimeters per minute", "cm per minute"]
    base_multiplier = 0.01 / 60.0


# =========================================================================
# 2. IMPERIAL & US CUSTOMARY UNITS
# =========================================================================
class MilePerHour(SpeedUnit):
    symbol = "mi/h"
    aliases = ["mph", "mile per hour", "miles per hour"]
    # 1 mil/jam = (1 mil dalam meter) dibagi 3600 detik
    base_multiplier = const.MILE_TO_METER / 3600.0

class FootPerSecond(SpeedUnit):
    symbol = "ft/s"
    aliases = ["fps", "foot per second", "feet per second"]
    base_multiplier = const.FOOT_TO_METER

class FootPerMinute(SpeedUnit):
    symbol = "ft/min"
    aliases = ["fpm", "foot per minute", "feet per minute"]
    base_multiplier = const.FOOT_TO_METER / 60.0

class InchPerSecond(SpeedUnit):
    symbol = "in/s"
    aliases = ["inch per second", "inches per second"]
    base_multiplier = const.INCH_TO_METER


# =========================================================================
# 3. NAUTICAL & AEROSPACE UNITS
# =========================================================================
class Knot(SpeedUnit):
    symbol = "kt"
    aliases = ["knot", "knots", "kn"]
    base_multiplier = const.NAUTICAL_MILE_TO_METER / 3600.0

@axiom.scale(formula=_calc_mach_scale)
class Mach(SpeedUnit):
    symbol = "mach"
    aliases = ["ma"]
    base_multiplier = 1.0


# =========================================================================
# 4. COSMIC / THEORETICAL UNITS
# =========================================================================
class SpeedOfLight(SpeedUnit):
    symbol = "c"
    aliases = ["speed of light", "lightspeed"]
    base_multiplier = const.SPEED_OF_LIGHT
