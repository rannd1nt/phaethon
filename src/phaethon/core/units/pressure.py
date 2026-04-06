"""
Pressure and Stress Dimension Module.
This module defines units for force applied perpendicular to a surface.
It supports both Absolute pressure (relative to a perfect vacuum) and
Gauge pressure (which scales dynamically based on environmental atmospheric conditions).
The absolute base unit for this dimension is the Pascal (Pa).
"""
from .. base import BaseUnit
from .. import axioms as _axiom
from .. import constants as _const

from .force import Newton, KilogramForce, PoundForce
from .length import Meter, Centimeter, Foot, Inch
from .mass import Kilogram, Pound

@_axiom.bound(abstract=True)
class PressureUnit(BaseUnit):
    """
    The primary parent class for the Pressure dimension.
    The base unit is Pascal (Pa).
    """
    dimension = "pressure"

@_axiom.bound(min_val=0, abstract=True, msg="Physics Violation: Absolute pressure cannot drop below a perfect vacuum (0 Pa)!")
class AbsolutePressureUnit(PressureUnit):
    pass

@_axiom.bound(abstract=True)
@_axiom.shift(ctx="atmospheric_pressure", default=_const.STANDARD_ATMOSPHERE_PA, op="add")
class GaugePressureUnit(PressureUnit):
    pass

# =========================================================================
# 1. SI UNITS (PASCAL & MULTIPLES)
# =========================================================================

# Pascal: 1 Newton / Square Meter
@_axiom.derive(Newton / Meter**2)
class Pascal(AbsolutePressureUnit):
    __base_unit__ = True
    symbol = "Pa"
    aliases = ["pa", "pascal", "pascals"]

@_axiom.derive(100.0 * Pascal)
class Hectopascal(AbsolutePressureUnit):
    symbol = "hPa"
    aliases = ["hpa", "hectopascal", "hectopascals"]

@_axiom.derive(1e3 * Pascal)
class Kilopascal(AbsolutePressureUnit):
    symbol = "kPa"
    aliases = ["kpa", "kilopascal", "kilopascals"]

@_axiom.derive(1e6 * Pascal)
class Megapascal(AbsolutePressureUnit):
    symbol = "MPa"
    aliases = ["mpa", "megapascal", "megapascals"]

@_axiom.derive(1e9 * Pascal)
class Gigapascal(AbsolutePressureUnit):
    symbol = "GPa"
    aliases = ["gpa", "gigapascal", "gigapascals"]

@_axiom.derive(1e12 * Pascal)
class Terapascal(AbsolutePressureUnit):
    symbol = "TPa"
    aliases = ["tpa", "terapascal", "terapascals"]

@_axiom.derive(1e15 * Pascal)
class Petapascal(AbsolutePressureUnit):
    symbol = "PPa"
    aliases = ["ppa", "petapascal", "petapascals"]

@_axiom.derive(1e18 * Pascal)
class Exapascal(AbsolutePressureUnit):
    symbol = "EPa"
    aliases = ["epa", "exapascal", "exapascals"]

@_axiom.derive(1e21 * Pascal)
class Zettapascal(AbsolutePressureUnit):
    symbol = "ZPa"
    aliases = ["zpa", "zettapascal", "zettapascals"]

@_axiom.derive(1e24 * Pascal)
class Yottapascal(AbsolutePressureUnit):
    symbol = "YPa"
    aliases = ["ypa", "yottapascal", "yottapascals"]

@_axiom.derive(1e27 * Pascal)
class Ronnapascal(AbsolutePressureUnit):
    symbol = "RPa"
    aliases = ["rpa", "ronnapascal", "ronnapascals"]

@_axiom.derive(1e30 * Pascal)
class Quettapascal(AbsolutePressureUnit):
    symbol = "QPa"
    aliases = ["qpa", "quettapascal", "quettapascals"]

# --- SUB-MULTIPLES ---
@_axiom.derive(1e-3 * Pascal)
class Millipascal(AbsolutePressureUnit):
    symbol = "mPa"
    aliases = ["mpa_milli", "millipa", "millipascal", "millipascals"]

@_axiom.derive(1e-6 * Pascal)
class Micropascal(AbsolutePressureUnit):
    symbol = "μPa"
    aliases = ["upa", "uPa", "micropascal", "micropascals", "micro pascal"]

@_axiom.derive(1e-9 * Pascal)
class Nanopascal(AbsolutePressureUnit):
    symbol = "nPa"
    aliases = ["npa", "nanopascal", "nanopascals"]

@_axiom.derive(1e-12 * Pascal)
class Picopascal(AbsolutePressureUnit):
    symbol = "pPa"
    aliases = ["ppa", "picopascal", "picopascals"]

# =========================================================================
# 2. BAR UNITS (METRIC)
# =========================================================================

@_axiom.derive(1e5 * Pascal)
class Bar(AbsolutePressureUnit):
    symbol = "bar"
    aliases = ["bars", "bara", "bar(a)", "bar a", "bar_a", "bar abs", "bar absolute"]

@_axiom.derive(1e2 * Pascal)
class Millibar(AbsolutePressureUnit):
    symbol = "mbar"
    aliases = ["millibar", "millibars", "mbars", "mb"]

@_axiom.derive(1e5 * Pascal)
class BarGauge(GaugePressureUnit):
    symbol = "barg"
    aliases = ["bar gauge", "bar(g)", "bar g", "bar_g"]

# =========================================================================
# 3. ATMOSPHERIC, MANOMETRIC (Hg) & HYDROSTATIC (H2O)
# =========================================================================

@_axiom.derive(_const.STANDARD_ATMOSPHERE_PA * Pascal)
class Atmosphere(AbsolutePressureUnit):
    symbol = "atm"
    aliases = ["ata", "atmosphere", "atmospheres"]

@_axiom.derive(_const.TORR_TO_PA * Pascal)
class Torr(AbsolutePressureUnit):
    symbol = "Torr"
    aliases = ["torr", "mmhg", "mmHg", "mm Hg", "millimeter of mercury", "millimeters of mercury"]

@_axiom.derive(_const.INHG_TO_PA * Pascal)
class InchOfMercury(AbsolutePressureUnit):
    symbol = "inHg"
    aliases = ["inhg", "in Hg", "inch of mercury", "inches of mercury"]

@_axiom.derive(9.80665 * Pascal)
class MillimeterOfWater(AbsolutePressureUnit):
    symbol = "mmH2O"
    aliases = ["mmh2o", "mm H2O", "mm_H2O", "millimeter of water", "millimeters of water", "mmwg", "mm wc"]

@_axiom.derive(249.08891 * Pascal)
class InchOfWater(AbsolutePressureUnit):
    symbol = "inH2O"
    aliases = ["inh2o", "in H2O", "in_H2O", "inch of water", "inches of water", "inwg", "in wc"]

# =========================================================================
# 4. IMPERIAL / US UNITS (PSI)
# =========================================================================

@_axiom.derive(PoundForce / Inch**2)
class PSI(AbsolutePressureUnit):
    symbol = "psi"
    aliases = [
        "psia", "psi(a)", "psi a", "psi_a", "lb/in2", "lb/in^2", "lb/sq in",
        "pound per square inch", "pounds per square inch"
    ]

@_axiom.derive(PoundForce / Inch**2)
class PSIG(GaugePressureUnit):
    symbol = "psig"
    aliases = ["psi(g)", "psi g", "psi_g", "pound per square inch gauge"]

@_axiom.derive(1000.0 * PSI)
class KSI(AbsolutePressureUnit):
    symbol = "ksi"
    aliases = ["kip per square inch", "kips per square inch", "kpsi"]

# =========================================================================
# 5. CGS SYSTEM
# =========================================================================

@_axiom.derive(0.1 * Pascal)
class Barye(AbsolutePressureUnit):
    symbol = "Ba"
    aliases = ["ba", "barye", "dyne/cm2", "dyne/cm²", "dyne per square centimeter", "dyne/cm^2"]

# =========================================================================
# 6. ENGINEERING METRIC (kgf, tf)
# =========================================================================

@_axiom.derive(KilogramForce / Centimeter**2)
class TechnicalAtmosphere(AbsolutePressureUnit):
    symbol = "at"
    aliases = [
        "technical atmosphere", "technical atmospheres",
        "kgf/cm2", "kgf/cm²", "kg/cm2", "kg/cm²", "ksc",
        "kilogram-force per square centimeter", "kilogram/square centimeter"
    ]

@_axiom.derive(KilogramForce / Meter**2)
class KilogramForcePerSqMeter(AbsolutePressureUnit):
    symbol = "kgf/m2"
    aliases = ["kgf/m²", "kg/m2", "kg/m²", "kilogram-force per square meter", "kgf per m2"]

@_axiom.derive(1000.0 * KilogramForcePerSqMeter)
class TonForcePerSqMeter(AbsolutePressureUnit):
    symbol = "tf/m2"
    aliases = ["tf/m²", "t/m2", "t/m²", "ton-force per square meter", "tf per m²"]

# =========================================================================
# 7. ENGINEERING IMPERIAL (tsf, tsi)
# =========================================================================

@_axiom.derive(2000.0 * PSI)
class TonForcePerSqInch(AbsolutePressureUnit):
    symbol = "tsi"
    aliases = ["ton per square inch", "tons per square inch"]

@_axiom.derive((2000.0 / 144.0) * PSI)
class TonForcePerSqFoot(AbsolutePressureUnit):
    symbol = "tsf"
    aliases = ["ton per square foot", "tons per square foot"]

# =========================================================================
# 8. ACOUSTICS (LOGARITHMIC SOUND PRESSURE)
# =========================================================================
@_axiom.logarithmic(reference=Micropascal(20), multiplier=20.0)
class DecibelSPL(PressureUnit):
    symbol = "dB_SPL"
    aliases = ["dbspl", "dB SPL", "dB(SPL)"]