"""
Geometry and Spatial Dimensions Module.
Defines planar angles (radians, degrees) and solid angles (steradians).
Essential for calculating torque, phase shifts, and photometry.
"""
from .. base import BaseUnit
from .. import axioms as _axiom
import numpy as _np

@_axiom.bound(abstract=True)
class AngleUnit(BaseUnit):
    """The base unit for planar angles is the Radian."""
    dimension = "angle"

    def wrap(self) -> 'AngleUnit':
        """Wraps angle to standard [0, 360) or [0, 2π) range."""
        import numpy as np
        import math
        from ..compat import HAS_NUMPY
        from ..config import get_config
        
        circle_mag = self.__class__._from_base_value(2 * np.pi, self.context)
        wrapped = self._value % circle_mag
        
        atol = get_config("atol")
        
        if HAS_NUMPY and isinstance(wrapped, (np.ndarray, np.generic)):
            wrapped = np.where(
                np.isclose(wrapped, circle_mag, atol=atol) | np.isclose(wrapped, 0.0, atol=atol), 
                0.0, 
                wrapped
            )
        else:
            if math.isclose(float(wrapped), float(circle_mag), abs_tol=atol) or math.isclose(float(wrapped), 0.0, abs_tol=atol):
                wrapped = 0.0
                
        merged_context = {**self.context, "__is_math_op__": True}
        return self.__class__(wrapped, context=merged_context)

    def to_dms(self) -> str:
        """Converts to Degrees, Minutes, Seconds format."""
        degrees = self.to('degree').mag
        d = int(degrees)
        m = int((degrees - d) * 60)
        s = (degrees - d - m/60) * 3600
        return f"{d}° {m}' {s:.2f}\""

class Radian(AngleUnit):
    __base_unit__ = True
    symbol = "rad"
    aliases = ["radian", "radians"]

@_axiom.derive((_np.pi / 180.0) * Radian)
class Degree(AngleUnit):
    symbol = "°"
    aliases = ["deg", "degree", "degrees"]

@_axiom.derive(Degree / 60.0)
class ArcMinute(AngleUnit):
    symbol = "arcmin"
    aliases = ["'", "arc_minute", "minute of arc"]

@_axiom.derive(ArcMinute / 60.0)
class ArcSecond(AngleUnit):
    symbol = "arcsec"
    aliases = ['"', "arc_second", "second of arc"]

@_axiom.derive(360.0 * Degree)
class Revolution(AngleUnit):
    symbol = "rev"
    aliases = ["revolution", "turn", "cycle"]

# 2. SOLID ANGLE (Dibatasi 0 hingga 4π)
@_axiom.bound(min_val=0, max_val=4 * _np.pi, msg="Solid angle must be between 0 and 4π steradians.", abstract=True)
class SolidAngleUnit(BaseUnit):
    """The base unit for 3D solid angles is the Steradian."""
    dimension = "solid_angle"

class Steradian(SolidAngleUnit):
    __base_unit__ = True
    symbol = "sr"
    aliases = ["steradian", "steradians"]

@_axiom.derive(1.0 / (4 * _np.pi) * Steradian)
class Spat(SolidAngleUnit):
    symbol = "sp"