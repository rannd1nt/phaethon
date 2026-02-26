"""
Speed and Velocity Dimension Module.
This module measures the rate of change of position over time.
It supports linear velocities (m/s, mph), nautical speeds (Knots),
cosmic constants (Speed of Light), and dynamically scaled environmental
speeds (Mach, dependent on temperature).
The absolute base unit for this dimension is Meters per Second (m/s).
"""
from ..core.base import BaseUnit
from ..core import axioms as _axiom
from ..core import constants as _const
from ..core import vmath as _vmath
from .temperature import Kelvin

@_axiom.bound(min_val=0, msg="Speed (scalar magnitude) cannot be negative!")
class SpeedUnit(BaseUnit):
    """
    The primary parent class for the Speed dimension.
    The absolute base unit is Meter per Second (m/s).
    """
    dimension = "speed"

@_axiom.prepare(temperature=Kelvin)
def _calc_mach_scale(temperature = _const.STANDARD_ATMOSPHERE_TEMP_K) -> float:
    safe_temp = _vmath.maximum(temperature, _const.ABSOLUTE_ZERO_K)
    return _const.SPEED_OF_SOUND_0C * _vmath.sqrt(safe_temp / _const.ZERO_CELSIUS_K)

# =========================================================================
# 1. METRIC UNITS (Base: Meters per second)
# =========================================================================

class MeterPerSecond(SpeedUnit):
    symbol = "m/s"
    aliases = [
        "mps", "m/sec", "m / s", "meter per second", "meters per second",
        "metre per second", "metres per second", "meter/second", "metre/second"
    ]
    base_multiplier = 1.0

class MeterPerMinute(SpeedUnit):
    symbol = "m/min"
    aliases = [
        "m / min", "meter per minute", "meters per minute",
        "metre per minute", "metres per minute", "meter/minute"
    ]
    base_multiplier = 1.0 / 60.0

class KilometerPerHour(SpeedUnit):
    symbol = "km/h"
    aliases = [
        "kph", "kmh", "km/hr", "km / h", "kilometer per hour", "kilometers per hour",
        "kilometre per hour", "kilometres per hour", "km per hour", "kilometer/hour"
    ]
    base_multiplier = 1000.0 / 3600.0

class MillimeterPerSecond(SpeedUnit):
    symbol = "mm/s"
    aliases = [
        "mm/sec", "mm / s", "millimeter per second", "millimeters per second",
        "millimetre per second", "mm per second"
    ]
    base_multiplier = 0.001

class MillimeterPerMinute(SpeedUnit):
    symbol = "mm/min"
    aliases = [
        "mm / min", "millimeter per minute", "millimeters per minute",
        "millimetre per minute", "mm per minute"
    ]
    base_multiplier = 0.001 / 60.0

class CentimeterPerSecond(SpeedUnit):
    symbol = "cm/s"
    aliases = [
        "cm/sec", "cm / s", "centimeter per second", "centimeters per second",
        "centimetre per second", "cm per second"
    ]
    base_multiplier = 0.01

class CentimeterPerMinute(SpeedUnit):
    symbol = "cm/min"
    aliases = [
        "cm / min", "centimeter per minute", "centimeters per minute",
        "centimetre per minute", "cm per minute"
    ]
    base_multiplier = 0.01 / 60.0

# =========================================================================
# 2. IMPERIAL & US CUSTOMARY UNITS
# =========================================================================

class MilePerHour(SpeedUnit):
    symbol = "mph"
    aliases = [
        "mi/h", "mi/hr", "mi / h", "mile per hour", "miles per hour",
        "mile/hour", "miles/hour"
    ]
    base_multiplier = _const.MILE_TO_METER / 3600.0

class FootPerSecond(SpeedUnit):
    symbol = "ft/s"
    aliases = [
        "fps", "ft/sec", "ft / s", "foot per second", "feet per second",
        "foot/second", "feet/second"
    ]
    base_multiplier = _const.FOOT_TO_METER

class FootPerMinute(SpeedUnit):
    symbol = "ft/min"
    aliases = [
        "fpm", "ft / min", "foot per minute", "feet per minute",
        "foot/minute", "feet/minute"
    ]
    base_multiplier = _const.FOOT_TO_METER / 60.0

class InchPerSecond(SpeedUnit):
    symbol = "in/s"
    aliases = [
        "ips", "in/sec", "in / s", "inch per second", "inches per second",
        "inch/second", "inches/second"
    ]
    base_multiplier = _const.INCH_TO_METER

# =========================================================================
# 3. NAUTICAL & AEROSPACE UNITS
# =========================================================================

class Knot(SpeedUnit):
    symbol = "kt"
    aliases = ["kts", "knot", "knots", "kn", "nmi/h"]
    base_multiplier = _const.NAUTICAL_MILE_TO_METER / 3600.0

@_axiom.scale(formula=_calc_mach_scale)
class Mach(SpeedUnit):
    symbol = "mach"
    aliases = ["ma", "mach number"]
    base_multiplier = 1.0

# =========================================================================
# 4. COSMIC / THEORETICAL UNITS
# =========================================================================

class SpeedOfLight(SpeedUnit):
    symbol = "c"
    aliases = ["speed of light", "lightspeed", "speed_of_light"]
    base_multiplier = _const.SPEED_OF_LIGHT