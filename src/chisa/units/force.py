"""
Force Dimension Module.

This module implements units of physical force, bridging absolute systems 
(like Newtons and Dynes) with gravitational systems (like Kilogram-force 
and Pound-force) based on standard Earth gravity.
The absolute base unit for this dimension is the Newton (N).
"""

from ..core.base import BaseUnit
from ..core.axioms import Axiom

from .mass import Kilogram, Gram, Pound, Ounce, MetricTon
from .length import Meter, Centimeter, Foot
from .time import Second

axiom = Axiom()

@axiom.bound(min_val=0, msg="The scalar magnitude of force cannot be negative.")
class ForceUnit(BaseUnit):
    """The primary parent class for the Force dimension. The base unit is Newton (N)."""
    dimension = "force"


# =========================================================================
# 1. SI / METRIC UNITS (Absolute)
# =========================================================================
# Newton: 1 kg * m / s²
@axiom.derive(mul=[Kilogram, Meter], div=[Second, Second])
class Newton(ForceUnit):
    symbol = "N"
    aliases = ["newton", "newtons"]

@axiom.derive(mul=[1000, Newton])
class Kilonewton(ForceUnit):
    symbol = "kN"
    aliases = ["kilonewton", "kilonewtons"]

@axiom.derive(mul=[1e6, Newton])
class Meganewton(ForceUnit):
    symbol = "MN"
    aliases = ["meganewton", "meganewtons"]

# Dyne (CGS System): 1 g * cm / s² (0.00001 N)
@axiom.derive(mul=[Gram, Centimeter], div=[Second, Second])
class Dyne(ForceUnit):
    symbol = "dyn"
    aliases = ["dyne", "dynes"]


# =========================================================================
# 2. GRAVITATIONAL METRIC UNITS (g_n = 9.80665 m/s²)
# =========================================================================
# Kilogram-force (Kilopond): 1 kg * 9.80665 m/s²
@axiom.derive(mul=[Kilogram, 9.80665, Meter], div=[Second, Second])
class KilogramForce(ForceUnit):
    symbol = "kgf"
    aliases = ["kilogram-force", "kilopond", "kp"]

@axiom.derive(mul=[Gram, 9.80665, Meter], div=[Second, Second])
class GramForce(ForceUnit):
    symbol = "gf"
    aliases = ["gram-force", "pond", "p"]

@axiom.derive(mul=[MetricTon, 9.80665, Meter], div=[Second, Second])
class TonneForce(ForceUnit):
    symbol = "tf"
    aliases = ["tonne-force", "ton-force", "metric ton-force"]


# =========================================================================
# 3. US CUSTOMARY / IMPERIAL UNITS
# =========================================================================
# Pound-force: 1 lb * standard Earth gravity (Automatically synthesizes to ~4.4482216 N)
@axiom.derive(mul=[Pound, 9.80665, Meter], div=[Second, Second])
class PoundForce(ForceUnit):
    symbol = "lbf"
    aliases = ["pound-force", "pounds-force"]

# Ounce-force: 1 oz * standard Earth gravity (Automatically synthesizes to ~0.2780139 N)
@axiom.derive(mul=[Ounce, 9.80665, Meter], div=[Second, Second])
class OunceForce(ForceUnit):
    symbol = "ozf"
    aliases = ["ounce-force", "ounces-force"]

# Poundal (Absolute Imperial): 1 lb * 1 ft / s² (Automatically synthesizes to ~0.138255 N)
@axiom.derive(mul=[Pound, Foot], div=[Second, Second])
class Poundal(ForceUnit):
    symbol = "pdl"
    aliases = ["poundal", "poundals"]

# Ton-force (Short Ton / US): 2000 lb * standard Earth gravity
@axiom.derive(mul=[2000, Pound, 9.80665, Meter], div=[Second, Second])
class ShortTonForce(ForceUnit):
    symbol = "short tonf"
    aliases = ["tonf", "us ton-force", "short ton-force"]