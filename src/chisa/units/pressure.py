"""
Pressure and Stress Dimension Module.
This module defines units for force applied perpendicular to a surface.
It supports both Absolute pressure (relative to a perfect vacuum) and
Gauge pressure (which scales dynamically based on environmental atmospheric conditions).
The absolute base unit for this dimension is the Pascal (Pa).
"""
from ..core.base import BaseUnit
from ..core import axioms as _axiom
from ..core import constants as _const

class PressureUnit(BaseUnit):
    """
    The primary parent class for the Pressure dimension.
    The base unit is Pascal (Pa).
    """
    dimension = "pressure"

@_axiom.bound(min_val=0, msg="Physics Violation: Absolute pressure cannot drop below a perfect vacuum (0 Pa)!")
class AbsolutePressureUnit(PressureUnit):
    """
    Represents absolute pressure measurements (e.g., psia, Pa, bara).
    Measured relative to a perfect vacuum.
    """
    pass

@_axiom.shift(ctx="atmospheric_pressure", default=_const.STANDARD_ATMOSPHERE_PA, op="add")
class GaugePressureUnit(PressureUnit):
    """
    Represents gauge pressure measurements (e.g., psig, barg).
    The value is automatically shifted by the local atmospheric pressure
    (provided via the 'atmospheric_pressure' context key).
    """
    pass

# =========================================================================
# 1. SI UNITS (PASCAL & MULTIPLES)
# =========================================================================

class Pascal(AbsolutePressureUnit):
    symbol = "Pa"
    aliases = ["pa", "pascal", "pascals"]
    base_multiplier = 1.0

class Kilopascal(AbsolutePressureUnit):
    symbol = "kPa"
    aliases = ["kpa", "kilopascal", "kilopascals"]
    base_multiplier = 1e3

class Megapascal(AbsolutePressureUnit):
    symbol = "MPa"
    aliases = ["mpa", "megapascal", "megapascals"]
    base_multiplier = 1e6

class Gigapascal(AbsolutePressureUnit):
    symbol = "GPa"
    aliases = ["gpa", "gigapascal", "gigapascals"]
    base_multiplier = 1e9

class Hectopascal(AbsolutePressureUnit):
    symbol = "hPa"
    aliases = ["hpa", "hectopascal", "hectopascals"]
    base_multiplier = 100.0

class Millipascal(AbsolutePressureUnit):
    symbol = "mPa"
    aliases = ["mpa_milli", "millipa", "millipascal", "millipascals"]
    base_multiplier = 1e-3

class Micropascal(AbsolutePressureUnit):
    symbol = "μPa"
    aliases = ["upa", "uPa", "micropascal", "micropascals", "micro pascal"]
    base_multiplier = 1e-6

class Nanopascal(AbsolutePressureUnit):
    symbol = "nPa"
    aliases = ["npa", "nanopascal", "nanopascals"]
    base_multiplier = 1e-9

class Picopascal(AbsolutePressureUnit):
    symbol = "pPa"
    aliases = ["ppa", "picopascal", "picopascals"]
    base_multiplier = 1e-12

class Terapascal(AbsolutePressureUnit):
    symbol = "TPa"
    aliases = ["tpa", "terapascal", "terapascals"]
    base_multiplier = 1e12

# =========================================================================
# 2. BAR UNITS (METRIC)
# =========================================================================

class Bar(AbsolutePressureUnit):
    symbol = "bar"
    aliases = ["bars", "bara", "bar(a)", "bar a", "bar_a", "bar abs", "bar absolute"]
    base_multiplier = 1e5

class Millibar(AbsolutePressureUnit):
    symbol = "mbar"
    aliases = ["millibar", "millibars", "mbars", "mb"]
    base_multiplier = 1e2

class BarGauge(GaugePressureUnit):
    symbol = "barg"
    aliases = ["bar gauge", "bar(g)", "bar g", "bar_g"]
    base_multiplier = 1e5

# =========================================================================
# 3. ATMOSPHERIC, MANOMETRIC (Hg) & HYDROSTATIC (H2O)
# =========================================================================

class Atmosphere(AbsolutePressureUnit):
    symbol = "atm"
    aliases = ["ata", "atmosphere", "atmospheres"]
    base_multiplier = _const.STANDARD_ATMOSPHERE_PA

class Torr(AbsolutePressureUnit):
    symbol = "Torr"
    aliases = ["torr", "mmhg", "mmHg", "mm Hg", "millimeter of mercury", "millimeters of mercury"]
    base_multiplier = _const.TORR_TO_PA

class InchOfMercury(AbsolutePressureUnit):
    symbol = "inHg"
    aliases = ["inhg", "in Hg", "inch of mercury", "inches of mercury"]
    base_multiplier = _const.INHG_TO_PA

class MillimeterOfWater(AbsolutePressureUnit):
    symbol = "mmH2O"
    aliases = ["mmh2o", "mm H2O", "mm_H2O", "millimeter of water", "millimeters of water", "mmwg", "mm wc"]
    base_multiplier = 9.80665 # 1 mmH2O is exactly 9.80665 Pa

class InchOfWater(AbsolutePressureUnit):
    symbol = "inH2O"
    aliases = ["inh2o", "in H2O", "in_H2O", "inch of water", "inches of water", "inwg", "in wc"]
    base_multiplier = 249.08891 # 1 inH2O is approx 249.08891 Pa

# =========================================================================
# 4. IMPERIAL / US UNITS (PSI)
# =========================================================================

class PSI(AbsolutePressureUnit):
    """Pounds per square inch (Absolute by default in most scientific contexts)."""
    symbol = "psi"
    aliases = [
        "psia", "psi(a)", "psi a", "psi_a", "lb/in2", "lb/in^2", "lb/sq in",
        "pound per square inch", "pounds per square inch"
    ]
    base_multiplier = _const.PSI_TO_PA

class PSIG(GaugePressureUnit):
    """Pounds per square inch (Gauge). Value is influenced by atmospheric pressure."""
    symbol = "psig"
    aliases = ["psi(g)", "psi g", "psi_g", "pound per square inch gauge"]
    base_multiplier = _const.PSI_TO_PA

class KSI(AbsolutePressureUnit):
    symbol = "ksi"
    aliases = ["kip per square inch", "kips per square inch", "kpsi"]
    # 1 KSI = 1000 PSI
    base_multiplier = _const.PSI_TO_PA * 1000.0

# =========================================================================
# 5. CGS SYSTEM
# =========================================================================

class Barye(AbsolutePressureUnit):
    symbol = "Ba"
    aliases = ["ba", "barye", "dyne/cm2", "dyne/cm²", "dyne per square centimeter", "dyne/cm^2"]
    base_multiplier = 0.1

# =========================================================================
# 6. ENGINEERING METRIC (kgf, tf)
# =========================================================================

class TechnicalAtmosphere(AbsolutePressureUnit):
    symbol = "at"
    aliases = [
        "technical atmosphere", "technical atmospheres",
        "kgf/cm2", "kgf/cm²", "kg/cm2", "kg/cm²", "ksc",
        "kilogram-force per square centimeter", "kilogram/square centimeter"
    ]
    # kgf/cm² = gravity * 10000 (because 1 m² = 10000 cm²)
    base_multiplier = _const.STANDARD_GRAVITY * 10000.0

class KilogramForcePerSqMeter(AbsolutePressureUnit):
    symbol = "kgf/m2"
    aliases = ["kgf/m²", "kg/m2", "kg/m²", "kilogram-force per square meter", "kgf per m2"]
    # Exactly equal to gravity acceleration
    base_multiplier = _const.STANDARD_GRAVITY

class TonForcePerSqMeter(AbsolutePressureUnit):
    symbol = "tf/m2"
    aliases = ["tf/m²", "t/m2", "t/m²", "ton-force per square meter", "tf per m²"]
    # 1 Metric Ton = 1000 kg
    base_multiplier = _const.STANDARD_GRAVITY * 1000.0

# =========================================================================
# 7. ENGINEERING IMPERIAL (tsf, tsi)
# =========================================================================

class TonForcePerSqInch(AbsolutePressureUnit):
    symbol = "tsi"
    aliases = ["ton per square inch", "tons per square inch"]
    # US Short Ton = 2000 lbs. So TSI = 2000 * PSI
    base_multiplier = _const.PSI_TO_PA * 2000.0

class TonForcePerSqFoot(AbsolutePressureUnit):
    symbol = "tsf"
    aliases = ["ton per square foot", "tons per square foot"]
    # 1 sq ft = 144 sq in. So TSF = (2000 * PSI) / 144
    base_multiplier = (_const.PSI_TO_PA * 2000.0) / 144.0