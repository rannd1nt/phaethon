"""
Advanced Kinematics and Rotational Mechanics Module.
Handles Jerk, Angular velocities, Momentum, and Torque.
"""
from .. base import BaseUnit
from .. import axioms as _axiom
from .force import PoundForce
from .mass import Kilogram, Pound, Gram
from .length import Meter, Foot, Centimeter
from .time import Second
from .geometry import Radian, Degree
from .energy import Joule
from .force import Newton
from .acceleration import StandardGravity

# 1. JERK 
@_axiom.bound(abstract=True)
class JerkUnit(BaseUnit):
    dimension = "jerk"

@_axiom.derive(Meter / Second**3)
class MeterPerSecondCubed(JerkUnit):
    __base_unit__ = True
    symbol = "m/s³"
    aliases = ["m/s3", "jerk"]

@_axiom.derive(StandardGravity / Second)
class GravityPerSecond(JerkUnit):
    symbol = "g/s"
    aliases = ["g_force_per_second"]

# 2. ANGULAR VELOCITY (rad/s)
@_axiom.bound(abstract=True)
class AngularVelocityUnit(BaseUnit):
    dimension = "angular_velocity"

@_axiom.derive(Radian / Second)
class RadianPerSecond(AngularVelocityUnit):
    __base_unit__ = True
    symbol = "rad/s"

# 3. ANGULAR ACCELERATION (rad/s²)
@_axiom.bound(abstract=True)
class AngularAccelerationUnit(BaseUnit):
    dimension = "angular_acceleration"

@_axiom.derive(Radian / Second**2)
class RadianPerSecondSquared(AngularAccelerationUnit):
    __base_unit__ = True
    symbol = "rad/s²"
    aliases = ["rad/s2"]

@_axiom.derive(Degree / Second)
class DegreePerSecond(AngularVelocityUnit):
    symbol = "°/s"
    aliases = ["deg/s", "degree_per_second"]

@_axiom.derive(Degree / Second**2)
class DegreePerSecondSquared(AngularAccelerationUnit):
    symbol = "°/s²"
    aliases = ["deg/s2", "degree_per_second_squared"]

# 4. MOMENTUM (kg·m/s)
@_axiom.bound(abstract=True)
class MomentumUnit(BaseUnit):
    dimension = "momentum"

@_axiom.derive(Kilogram * Meter / Second)
class KilogramMeterPerSecond(MomentumUnit):
    __base_unit__ = True
    symbol = "kg·m/s"
    aliases = ["kg.m/s", "momentum"]

@_axiom.derive(Gram * Centimeter / Second)
class GramCentimeterPerSecond(MomentumUnit):
    symbol = "g·cm/s"

@_axiom.derive(Pound * Foot / Second)
class PoundFootPerSecond(MomentumUnit):
    symbol = "lb·ft/s"

# 5. TORQUE (N·m/rad J/rad) 
@_axiom.bound(abstract=True)
class TorqueUnit(BaseUnit):
    __exclusive_domain__ = True
    dimension = "torque"

@_axiom.derive(Joule / Radian)
class NewtonMeter(TorqueUnit):
    __base_unit__ = True
    symbol = "N·m"
    aliases = ["n_m", "newton_meter", "nm", "N·m/rad"]

@_axiom.derive((Joule / 100) / Radian)
class NewtonCentimeter(TorqueUnit):
    symbol = "N·cm"
    aliases = ["n_cm", "newton_centimeter"]

@_axiom.derive((PoundForce * Foot) / Radian)
class PoundForceFootPerRadian(TorqueUnit):
    symbol = "lbf·ft/rad"
    aliases = ["lbf_ft", "pound_force_foot"]

# 6. MOMENT OF INERTIA (kg·m²)
@_axiom.bound(abstract=True)
class MomentOfInertiaUnit(BaseUnit):
    dimension = "moment_of_inertia"

@_axiom.derive(Kilogram * Meter**2)
class KilogramSquareMeter(MomentOfInertiaUnit):
    __base_unit__ = True
    symbol = "kg·m²"
    aliases = ["kg.m2", "inertia"]

@_axiom.derive(Gram * Centimeter**2)
class GramSquareCentimeter(MomentOfInertiaUnit):
    symbol = "g·cm²"

@_axiom.derive(Pound * Foot**2)
class PoundSquareFoot(MomentOfInertiaUnit):
    symbol = "lb·ft²"


@_axiom.bound(min_val=0)
class StiffnessUnit(BaseUnit):
    """Dimension for Spring Constant / Surface Tension / Stiffness."""
    dimension = "stiffness"

@_axiom.derive(Newton / Meter)
class NewtonPerMeter(StiffnessUnit):
    """The SI Base Unit for Stiffness."""
    __base_unit__ = True
    symbol = "N/m"
    aliases = ["newton per meter", "spring_constant"]

@_axiom.bound(abstract=True)
class RateUnit(BaseUnit):
    dimension = "rate"

@_axiom.derive(1 / Second)
class Rate(RateUnit):
    __base_unit__ = True
    symbol = "/ s"
    aliases = ["per_second"]


@_axiom.bound(min_val=0, abstract=True)
class StiffnessUnit(BaseUnit):
    __exclusive_domain__ = True
    dimension = "stiffness"

@_axiom.derive(Newton / Meter)
class NewtonPerMeter(StiffnessUnit):
    __base_unit__ = True
    symbol = "N/m"


@_axiom.bound(min_val=0, abstract=True)
class SurfaceTensionUnit(BaseUnit):
    __exclusive_domain__ = True
    dimension = "surface_tension"

@_axiom.derive(Newton / Meter)
class NewtonPerMeterSurface(SurfaceTensionUnit):
    __base_unit__ = True
    symbol = "N/m"

@_axiom.bound(abstract=True)
class AngularMomentumUnit(BaseUnit):
    __exclusive_domain__ = True
    dimension = "angular_momentum"

@_axiom.derive((Joule * Second) / Radian)
class JouleSecondPerRadian(AngularMomentumUnit):
    __base_unit__ = True
    symbol = "J·s/rad"
    aliases = ["angular_momentum_si", "j_s_per_rad"]

class ReducedPlanckConstantUnit(AngularMomentumUnit):
    base_multiplier = 1.054571817e-34
    symbol = "ħ"
    aliases = ["h_bar", "reduced_planck"]