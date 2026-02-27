"""
Force Dimension Module.

This module implements units of physical force, bridging absolute systems 
(like Newtons and Dynes) with gravitational systems (like Kilogram-force 
and Pound-force) based on standard Earth gravity.
The absolute base unit for this dimension is the Newton (N).
"""

from ..core.base import BaseUnit
from ..core import axioms as _axiom
from ..core import constants as _const

from .mass import Kilogram, Gram, Pound, Ounce, MetricTon
from .length import Meter, Centimeter, Foot
from .time import Second


@_axiom.bound(min_val=0, msg="The scalar magnitude of force cannot be negative.")
class ForceUnit(BaseUnit):
    """The primary parent class for the Force dimension. The base unit is Newton (N)."""
    dimension = "force"


# =========================================================================
# 1. SI / METRIC UNITS (Absolute)
# =========================================================================
# Newton: 1 kg * m / s²
@_axiom.derive(mul=[Kilogram, Meter], div=[Second, Second])
class Newton(ForceUnit):
    symbol = "N"
    aliases = ["n", "newton", "newtons"]

@_axiom.derive(mul=[1000, Newton])
class Kilonewton(ForceUnit):
    symbol = "kN"
    aliases = ["kn", "KN", "kilonewton", "kilonewtons", "kilo-newton"]

@_axiom.derive(mul=[1e6, Newton])
class Meganewton(ForceUnit):
    symbol = "MN"
    aliases = ["mn", "meganewton", "meganewtons", "mega-newton"]

# Dyne (CGS System): 1 g * cm / s² (0.00001 N)
@_axiom.derive(mul=[Gram, Centimeter], div=[Second, Second])
class Dyne(ForceUnit):
    symbol = "dyn"
    aliases = ["dyne", "dynes"]


# =========================================================================
# 2. GRAVITATIONAL METRIC UNITS
# =========================================================================
# Kilogram-force (Kilopond): 1 kg * STANDARD_GRAVITY
@_axiom.derive(mul=[Kilogram, _const.STANDARD_GRAVITY, Meter], div=[Second, Second])
class KilogramForce(ForceUnit):
    symbol = "kgf"
    aliases = [
        "kg-f", "kg_f", "kg f", "kilogram-force", "kilogram force", 
        "kilograms-force", "kilopond", "kiloponds", "kp"
    ]

@_axiom.derive(mul=[Gram, _const.STANDARD_GRAVITY, Meter], div=[Second, Second])
class GramForce(ForceUnit):
    symbol = "gf"
    aliases = [
        "g-f", "g_f", "g f", "gram-force", "gram force", 
        "grams-force", "pond", "ponds", "p"
    ]

@_axiom.derive(mul=[MetricTon, _const.STANDARD_GRAVITY, Meter], div=[Second, Second])
class TonneForce(ForceUnit):
    symbol = "tf"
    aliases = [
        "t-f", "t_f", "t f", "tonne-force", "ton-force", 
        "metric ton-force", "metric ton force", "tonnes-force"
    ]


# =========================================================================
# 3. US CUSTOMARY / IMPERIAL UNITS
# =========================================================================
# Pound-force: 1 lb * standard Earth gravity
@_axiom.derive(mul=[Pound, _const.STANDARD_GRAVITY, Meter], div=[Second, Second])
class PoundForce(ForceUnit):
    symbol = "lbf"
    aliases = [
        "lb-f", "lb_f", "lb f", "lbsf", "lbs-f", 
        "pound-force", "pounds-force", "pound force", "pounds force"
    ]

# Kip (Kilopound-force): 1000 lbf (Crucial for Civil Engineering)
@_axiom.derive(mul=[1000, PoundForce])
class Kip(ForceUnit):
    symbol = "kip"
    aliases = ["kips", "klbf", "kilopound-force", "kilopounds-force"]

# Ounce-force: 1 oz * standard Earth gravity
@_axiom.derive(mul=[Ounce, _const.STANDARD_GRAVITY, Meter], div=[Second, Second])
class OunceForce(ForceUnit):
    symbol = "ozf"
    aliases = [
        "oz-f", "oz_f", "oz f", "ozsf", 
        "ounce-force", "ounces-force", "ounce force", "ounces force"
    ]

# Poundal (Absolute Imperial): 1 lb * 1 ft / s²
@_axiom.derive(mul=[Pound, Foot], div=[Second, Second])
class Poundal(ForceUnit):
    symbol = "pdl"
    aliases = ["poundal", "poundals"]

# Ton-force (Short Ton / US): 2000 lb * standard Earth gravity
@_axiom.derive(mul=[2000, Pound, _const.STANDARD_GRAVITY, Meter], div=[Second, Second])
class ShortTonForce(ForceUnit):
    symbol = "short_tonf"
    aliases = [
        "tonf", "us ton-force", "short ton-force", "short ton force",
        "ton-force (US)", "ton-f", "ton_f", "tons-force"
    ]