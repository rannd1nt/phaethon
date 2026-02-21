"""
Speed and Velocity Dimension Module.

This module measures the rate of change of position over time.
It supports linear velocities (m/s, mph), nautical speeds (Knots), 
cosmic constants (Speed of Light), and dynamically scaled environmental 
speeds (Mach, dependent on temperature).
The absolute base unit for this dimension is Meters per Second (m/s).
"""

import math
from typing import Dict, Any
from ..core.base import BaseUnit
from ..core.axioms import Axiom

axiom = Axiom()

@axiom.bound(min_val=0, msg="Speed (scalar magnitude) cannot be negative!")
class SpeedUnit(BaseUnit):
    """
    The primary parent class for the Speed dimension.
    The absolute base unit is Meter per Second (m/s).
    """
    dimension = "speed"

def _mach_scale_context(ctx: Dict[str, Any]) -> float:
    """
    Dynamically calculates the speed of sound based on environmental temperature.
    Serves as the contextual scaling factor for the Mach unit.

    Args:
        ctx (Dict[str, Any]): The context dictionary containing temperature properties.

    Returns:
        float: The speed of sound in meters per second (m/s).
    """
    if 'speed_of_sound_m_s' in ctx:
        return float(ctx['speed_of_sound_m_s'])

    temp_c = 15.0  # Standard sea-level temperature

    if 'temp_c' in ctx:
        temp_c = float(ctx['temp_c'])
    elif 'temp_k' in ctx:
        temp_c = float(ctx['temp_k']) - 273.15
    elif 'temp_f' in ctx:
        temp_c = (float(ctx['temp_f']) - 32.0) * (5.0 / 9.0)
    elif 'temp_r' in ctx:
        temp_c = (float(ctx['temp_r']) - 491.67) * (5.0 / 9.0)
    elif 'temp_re' in ctx:
        temp_c = float(ctx['temp_re']) * (5.0 / 4.0)

    # Absolute zero boundary enforcement for the calculation
    if temp_c < -273.15:
        temp_c = -273.15 

    return 331.3 * math.sqrt(1 + (temp_c / 273.15))


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
    base_multiplier = 0.44704

class FootPerSecond(SpeedUnit):
    symbol = "ft/s"
    aliases = ["fps", "foot per second", "feet per second"]
    base_multiplier = 0.3048

class FootPerMinute(SpeedUnit):
    symbol = "ft/min"
    aliases = ["fpm", "foot per minute", "feet per minute"]
    base_multiplier = 0.3048 / 60.0

class InchPerSecond(SpeedUnit):
    symbol = "in/s"
    aliases = ["inch per second", "inches per second"]
    base_multiplier = 0.0254

class InchPerMinute(SpeedUnit):
    symbol = "in/min"
    aliases = ["inch per minute", "inches per minute"]
    base_multiplier = 0.0254 / 60.0


# =========================================================================
# 3. NAUTICAL & AEROSPACE UNITS
# =========================================================================
class Knot(SpeedUnit):
    symbol = "kt"
    aliases = ["knot", "knots", "kn"]
    base_multiplier = 1852.0 / 3600.0

@axiom.scale(formula=_mach_scale_context)
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
    base_multiplier = 299792458.0