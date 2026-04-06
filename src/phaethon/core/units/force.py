"""
Force Dimension Module.

This module implements units of physical force, bridging absolute systems 
(like Newtons and Dynes) with gravitational systems (like Kilogram-force 
and Pound-force) based on standard Earth gravity.
The absolute base unit for this dimension is the Newton (N).
"""

from .. base import BaseUnit
from .. import axioms as _axiom
from .. import constants as _const

from .mass import Kilogram, Gram, Pound, Ounce, MetricTon
from .length import Meter, Centimeter, Foot
from .time import Second

@_axiom.bound(min_val=0, msg="The scalar magnitude of force cannot be negative.", abstract=True)
class ForceUnit(BaseUnit):
    """The primary parent class for the Force dimension. The base unit is Newton (N)."""
    dimension = "force"

# =========================================================================
# 1. SI / METRIC UNITS (Absolute)
# =========================================================================
@_axiom.derive(Kilogram * Meter / Second**2)
class Newton(ForceUnit):
    __base_unit__ = True
    symbol = "N"
    aliases = ["n", "newton", "newtons"]

@_axiom.derive(1000 * Newton)
class Kilonewton(ForceUnit):
    symbol = "kN"
    aliases = ["kn", "KN", "kilonewton", "kilonewtons", "kilo-newton"]

@_axiom.derive(1e6 * Newton)
class Meganewton(ForceUnit):
    symbol = "MN"
    aliases = ["mn", "meganewton", "meganewtons", "mega-newton"]

@_axiom.derive(Gram * Centimeter / Second**2)
class Dyne(ForceUnit):
    symbol = "dyn"
    aliases = ["dyne", "dynes"]

# =========================================================================
# 2. GRAVITATIONAL METRIC UNITS
# =========================================================================
@_axiom.derive(Kilogram * _const.STANDARD_GRAVITY * Meter / Second**2)
class KilogramForce(ForceUnit):
    symbol = "kgf"
    aliases = ["kg-f", "kg_f", "kg f", "kilogram-force", "kilogram force", "kilopond", "kp"]

@_axiom.derive(Gram * _const.STANDARD_GRAVITY * Meter / Second**2)
class GramForce(ForceUnit):
    symbol = "gf"
    aliases = ["g-f", "g_f", "g f", "gram-force", "gram force", "pond", "p"]

@_axiom.derive(MetricTon * _const.STANDARD_GRAVITY * Meter / Second**2)
class TonneForce(ForceUnit):
    symbol = "tf"
    aliases = ["t-f", "t_f", "tonne-force", "ton-force", "metric ton-force"]

# =========================================================================
# 3. US CUSTOMARY / IMPERIAL UNITS
# =========================================================================
@_axiom.derive(Pound * _const.STANDARD_GRAVITY * Meter / Second**2)
class PoundForce(ForceUnit):
    symbol = "lbf"
    aliases = ["lb-f", "lb_f", "lbsf", "pound-force", "pounds-force", "pound force"]

@_axiom.derive(1000 * PoundForce)
class Kip(ForceUnit):
    symbol = "kip"
    aliases = ["kips", "klbf", "kilopound-force"]

@_axiom.derive(Ounce * _const.STANDARD_GRAVITY * Meter / Second**2)
class OunceForce(ForceUnit):
    symbol = "ozf"
    aliases = ["oz-f", "ozsf", "ounce-force", "ounce force"]

@_axiom.derive(Pound * Foot / Second**2)
class Poundal(ForceUnit):
    symbol = "pdl"
    aliases = ["poundal", "poundals"]

@_axiom.derive(2000 * Pound * _const.STANDARD_GRAVITY * Meter / Second**2)
class ShortTonForce(ForceUnit):
    symbol = "short_tonf"
    aliases = ["tonf", "us ton-force", "short ton-force", "ton-force (US)"]