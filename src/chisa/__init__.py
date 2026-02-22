"""
Chisa is a logic-driven Dimensional Algebra and Physics Modeling Framework for Python.

Chisa provides a robust, developer-friendly ecosystem for handling physical and 
digital unit conversions, mathematical operations across different units, and 
strict dimensional validation. It is designed to prevent dimensional mismatch 
errors in scientific computing, engineering applications, and everyday scripting.

Scope and Capabilities:
    Chisa covers a wide array of physical and digital dimensions, including:
    Area, Data, Energy, Force, Length, Mass, Power, Pressure, Speed, 
    Temperature, Time, and Volume.

Core Paradigms:

    1. The Fluent API (Quick Conversions)
       A chainable, readable interface for straightforward conversions and string formatting.
       >>> from chisa import convert
       >>> result = convert(1.5, 'kg').to('g').use(format='verbose').resolve()
       >>> print(result) # "1.5 kg = 1500 g"

    2. Explicit OOP (Dimensional Math & State)
       Treat units as first-class objects. Chisa automatically handles base-value 
       normalization, allowing seamless math and comparisons between different units 
       of the same dimension.
       >>> from chisa.units.length import Meter, Centimeter
       >>> total = Meter(1) + Centimeter(50)
       >>> print(total) # <Meter: 1.5 m>

    3. The Axiom Engine (Strict Physics Modeling)
       Developers can extend Chisa by defining custom units or entirely new dimensions 
       by inheriting from `BaseUnit`. The `@axiom` decorators act as a physics rule engine
       to model real-world physical laws:
       
       >>> from chisa import axiom
       >>> from chisa.units.energy import Joule
       >>> from chisa.units.time import Second
       >>> from chisa.units.power import PowerUnit
       >>> 
       >>> # Synthesize a new unit based on physical laws (P = W / t)
       >>> @axiom.derive(mul=[Joule], div=[Second])
       >>> class Watt(PowerUnit):
       ...     symbol = "W"
       ...     aliases = ["watt", "watts"]

       - `@axiom.derive`: Synthesizes base multipliers dynamically.
       - `@axiom.bound`: Enforces physical limits (e.g., Absolute Zero for Kelvin).
       - `@axiom.scale` / `.shift`: Models context-dependent unit scaling (e.g., Mach).
       - `@axiom.require`: Acts as a guardrail for custom physics functions.

    4. Vectorized Computations (NumPy Integration)
       Seamlessly supports multidimensional NumPy arrays for high-performance 
       scientific computing without losing dimensional integrity.
       >>> import numpy as np
       >>> speeds = convert(np.array([1, 2, 3]), 'mach').to('m/s').resolve()
"""

from chisa.exceptions import (
    ChisaError, ConversionError, DimensionMismatchError, AxiomViolationError, AmbiguousUnitError,
    UnitNotFoundError
)

from .core.registry import baseof, dims, unitsin, dimof
from .core import axioms as axiom
from .core import constants as const
from .core import vmath
from .core.axioms import C
from .core.engine import convert
from .core.base import BaseUnit

def _bootstrap_units() -> None:
    """
    Silently loads all built-in unit modules to trigger the Axiom Engine's
    auto-registration (__init_subclass__).
    """
    import importlib
    
    _core_dimensions = [
        "length", "mass", "pressure", "time", "speed", "temperature", 
        "data", "volume", "force", "energy", "power", "area"
    ]
    
    for dim in _core_dimensions:
        importlib.import_module(f".units.{dim}", package=__name__)


_bootstrap_units()
del _bootstrap_units


__version__ = "0.1.0"
__all__ = [
    "convert",
    "axiom",
    "C",
    "const",
    "vmath",
    "BaseUnit",
    "get_base_unit",
    "get_dimensions",
    "get_units_by_dimension",
    "dimension_of",
    "ChisaError",
    "ConversionError",
    "DimensionMismatchError",
    "AxiomViolationError",
    "AmbiguousUnitError",
    "UnitNotFoundError"
]