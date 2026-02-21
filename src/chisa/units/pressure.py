"""
Pressure and Stress Dimension Module.

This module defines units for force applied perpendicular to a surface. 
It supports both Absolute pressure (relative to a perfect vacuum) and 
Gauge pressure (which scales dynamically based on environmental atmospheric conditions).
The absolute base unit for this dimension is the Pascal (Pa).
"""

from ..core.base import BaseUnit
from ..core.axioms import Axiom

axiom = Axiom()

class PressureUnit(BaseUnit):
    """
    The primary parent class for the Pressure dimension.
    The base unit is Pascal (Pa).
    """
    dimension = "pressure"

@axiom.bound(min_val=0, msg="Physics Violation: Absolute pressure cannot drop below a perfect vacuum (0 Pa)!")
class AbsolutePressureUnit(PressureUnit):
    """
    Represents absolute pressure measurements (e.g., psia, Pa, bar).
    Measured relative to a perfect vacuum.
    """
    pass

@axiom.shift(ctx="atm_pressure_pa", default=101325.0, op="add")
class GaugePressureUnit(PressureUnit):
    """
    Represents gauge pressure measurements (e.g., psig, barg).
    The value is automatically shifted by the local atmospheric pressure 
    (provided via the 'atm_pressure_pa' context key) to obtain the absolute base value.
    """
    pass


# =========================================================================
# 1. SI UNITS (PASCAL & MULTIPLES)
# =========================================================================
class Pascal(AbsolutePressureUnit):
    symbol = "pa"
    aliases = ["pascal", "pascals"]
    base_multiplier = 1.0

class Kilopascal(AbsolutePressureUnit):
    symbol = "kpa"
    aliases = ["kilopascal", "kilopascals"]
    base_multiplier = 1e3

class Megapascal(AbsolutePressureUnit):
    symbol = "mpa"
    aliases = ["megapascal", "megapascals"]
    base_multiplier = 1e6

class Gigapascal(AbsolutePressureUnit):
    symbol = "gpa"
    aliases = ["gigapascal", "gigapascals"]
    base_multiplier = 1e9

class Hectopascal(AbsolutePressureUnit):
    symbol = "hpa"
    aliases = ["hectopascal", "hectopascals"]
    base_multiplier = 100.0

class Millipascal(AbsolutePressureUnit):
    symbol = "mpa_milli"
    aliases = ["millipa", "millipascal", "millipascals"]
    base_multiplier = 1e-3

class Micropascal(AbsolutePressureUnit):
    symbol = "μpa"
    aliases = ["micropascal", "micropascals", "micro pascal"]
    base_multiplier = 1e-6

class Nanopascal(AbsolutePressureUnit):
    symbol = "npa"
    aliases = ["nanopascal", "nanopascals"]
    base_multiplier = 1e-9

class Picopascal(AbsolutePressureUnit):
    symbol = "ppa"
    aliases = ["picopascal", "picopascals"]
    base_multiplier = 1e-12

class Terapascal(AbsolutePressureUnit):
    symbol = "tpa"
    aliases = ["terapascal", "terapascals"]
    base_multiplier = 1e12

class Exapascal(AbsolutePressureUnit):
    symbol = "epa"
    aliases = ["exapascal", "exapascals"]
    base_multiplier = 1e18


# =========================================================================
# 2. BAR UNITS (METRIC)
# =========================================================================
class Bar(AbsolutePressureUnit):
    symbol = "bar"
    aliases = ["bars"]
    base_multiplier = 1e5

class Millibar(AbsolutePressureUnit):
    symbol = "mbar"
    aliases = ["millibar", "millibars"]
    base_multiplier = 1e2

class BarGauge(GaugePressureUnit):
    symbol = "barg"
    aliases = ["bar gauge"]
    base_multiplier = 1e5


# =========================================================================
# 3. ATMOSPHERIC & MANOMETRIC (Hg)
# =========================================================================
class Atmosphere(AbsolutePressureUnit):
    symbol = "atm"
    aliases = ["atmosphere", "atmospheres"]
    base_multiplier = 101325.0

class Torr(AbsolutePressureUnit):
    symbol = "torr"
    aliases = ["mmhg", "millimeter of mercury", "millimeters of mercury"]
    base_multiplier = 133.322

class InchOfMercury(AbsolutePressureUnit):
    symbol = "inhg"
    aliases = ["inch of mercury", "inches of mercury"]
    base_multiplier = 3386.39


# =========================================================================
# 4. IMPERIAL / US UNITS (PSI)
# =========================================================================
class PSI(AbsolutePressureUnit):
    """Pounds per square inch (Absolute by default in most scientific contexts)."""
    symbol = "psi"
    aliases = ["psia", "pound per square inch", "pounds per square inch"]
    base_multiplier = 6894.76

class PSIG(GaugePressureUnit):
    """Pounds per square inch (Gauge). Value is influenced by 'atm_pressure_pa'."""
    symbol = "psig"
    base_multiplier = 6894.76

class KSI(AbsolutePressureUnit):
    symbol = "ksi"
    aliases = ["kip per square inch", "kips per square inch"]
    base_multiplier = 6894760.0


# =========================================================================
# 5. CGS SYSTEM
# =========================================================================
class Barye(AbsolutePressureUnit):
    symbol = "ba"
    aliases = ["barye", "dyne/cm2", "dyne/cm²", "dyne per square centimeter", "dyne per cm 2"]
    base_multiplier = 0.1


# =========================================================================
# 6. ENGINEERING METRIC (kgf, tf)
# =========================================================================
class TechnicalAtmosphere(AbsolutePressureUnit):
    symbol = "at"
    aliases = [
        "technical atmosphere", "technical atmospheres", 
        "kgf/cm2", "kgf/cm²", "kilogram-force per square centimeter", "kilogram-force/square centimeter"
    ]
    base_multiplier = 98066.5

class KilogramForcePerSqMeter(AbsolutePressureUnit):
    symbol = "kgf/m2"
    aliases = ["kgf/m²", "kilogram-force per square meter", "kgf per m2"]
    base_multiplier = 9.80665

class TonForcePerSqMeter(AbsolutePressureUnit):
    symbol = "tf/m2"
    aliases = ["tf/m²", "ton-force per square meter", "tf per m²"]
    base_multiplier = 9806650.0


# =========================================================================
# 7. ENGINEERING IMPERIAL (tsf, tsi)
# =========================================================================
class TonForcePerSqInch(AbsolutePressureUnit):
    symbol = "tsi"
    aliases = ["ton per square inch", "tons per square inch"]
    base_multiplier = 1.379e7

class TonForcePerSqFoot(AbsolutePressureUnit):
    symbol = "tsf"
    aliases = ["ton per square foot", "tons per square foot"]
    base_multiplier = 9.578e4