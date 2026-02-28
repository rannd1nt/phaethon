"""
Phaethon: Unit-Safe Data Pipeline Schema
=====================================

Phaethon is a declarative schema validation and semantic data transformation 
tool designed for Data Engineers and Scientists. It normalizes messy 
heterogeneous units and enforces physical integrity before your data hits 
ML models or production databases.

While standard schema tools only validate data types, Phaethon validates 
physical reality using a strict, Metaclass-driven Object-Oriented physics engine.

Core Features
-------------
* Declarative Schemas : Clean and normalize mixed-unit Pandas DataFrames.
* Vectorized Engine   : High-speed, array-safe transformations using NumPy.
* Axiom Engine        : Build custom dimensions and enforce physical laws.
* Pipeline Hooks      : Inject domain logic via pre/post normalization hooks.
* Fluent API          : Quick, chainable conversions supporting both string 
                        aliases ('km') and explicit unit classes (u.Kilometer).

Main Exported Components
------------------------
Schema          : Base class for defining declarative data pipelines.
Field           : Defines column-level unit targets, bounds, and parsing rules.
u               : Namespace for all built-in physical dimensions and units.
axiom           : Decorators for deriving units and enforcing physical bounds.
convert         : Fluent API entry point for inline conversions (scalars or arrays).
"""

from phaethon.exceptions import (
    PhaethonError, ConversionError, DimensionMismatchError, AxiomViolationError, AmbiguousUnitError,
    UnitNotFoundError, NormalizationError
)

from .core.registry import baseof, dims, unitsin, dimof
from .core.schema import Schema, Field, post_normalize, pre_normalize
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
        "length", "mass", "pressure", "time", "speed", "temperature", "volume",
        "data", "force", "energy", "power", "area", "density", "frequency"
    ]
    
    for dim in _core_dimensions:
        importlib.import_module(f".units.{dim}", package=__name__)


_bootstrap_units()
del _bootstrap_units

from . import u

__version__ = "0.2.3"
__all__ = [
    "u",
    "baseof",
    "dims",
    "unitsin",
    "dimof",
    "Schema",
    "Field",
    "post_normalize",
    "pre_normalize",
    "convert",
    "axiom",
    "C",
    "const",
    "vmath",
    "BaseUnit",
    "PhaethonError",
    "ConversionError",
    "DimensionMismatchError",
    "AxiomViolationError",
    "AmbiguousUnitError",
    "UnitNotFoundError",
    "NormalizationError"
]