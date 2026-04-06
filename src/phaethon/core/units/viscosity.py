"""
Fluid Dynamics: Viscosity Dimension Module.
"""
from .. base import BaseUnit
from .. import axioms as _axiom
from .pressure import Pascal
from .time import Second
from .length import Meter

class DynamicViscosityUnit(BaseUnit):
    dimension = "dynamic_viscosity"

@_axiom.derive(Pascal * Second)
class PascalSecond(DynamicViscosityUnit):
    __base_unit__ = True
    symbol = "Pa·s"
    aliases = ["Pa.s", "pascal_second", "poiseuille", "Pl"]

@_axiom.derive(0.1 * PascalSecond)
class Poise(DynamicViscosityUnit):
    symbol = "P"
    aliases = ["poise"]

@_axiom.derive(0.001 * PascalSecond)
class Centipoise(DynamicViscosityUnit):
    symbol = "cP"
    aliases = ["cps", "centipoise"]

class KinematicViscosityUnit(BaseUnit):
    dimension = "kinematic_viscosity"

@_axiom.derive(Meter**2 / Second)
class SquareMeterPerSecond(KinematicViscosityUnit):
    __base_unit__ = True
    symbol = "m²/s"
    aliases = ["m2/s", "sq_meter_per_second"]

@_axiom.derive(1e-4 * SquareMeterPerSecond)
class Stokes(KinematicViscosityUnit):
    symbol = "St"
    aliases = ["stokes"]

@_axiom.derive(1e-6 * SquareMeterPerSecond)
class Centistokes(KinematicViscosityUnit):
    symbol = "cSt"
    aliases = ["cst", "centistokes"]