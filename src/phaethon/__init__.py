"""
Phaethon: Dimensional Data Pipelines & Semantic Data Transformations
=============================================================

Phaethon is an enterprise-grade schema validation and semantic engine for 
Data Engineers and Scientists. It enforces absolute physical laws, normalizes 
heterogeneous units, and translates continuous physical data into discrete 
business logic before it hits your ML models or production databases.

While standard schema tools only validate data types, Phaethon validates 
physical reality using a strict, Metaclass-driven physics and semantic engine.

Core Capabilities
-----------------
* High-Performance Backends : Native Rust-powered Polars and vectorized Pandas support.
* Dimensional Schemas       : Clean mixed-unit "Excel Hell" data automatically.
* Semantic Translations     : Map raw physical values to discrete states (e.g., 13.5V -> "OVERCHARGED").
* Declarative Ontologies    : RapidFuzz integration for typo correction on categorical data.
* ML Feature Engineering    : Synthesize cross-column features via dimensional algebra.
* Dynamic Contexts          : Thread-safe environmental variables for real-time FinTech & Physics.
"""

from phaethon.exceptions import (
    PhaethonError, ConversionError, DimensionMismatchError, AxiomViolationError, AmbiguousUnitError,
    UnitNotFoundError, NormalizationError
)

from .core.registry import baseof, dims, unitsin, dimof
from .core.schema import Schema, Field, DerivedField, post_normalize, pre_normalize, col
from .core.semantics import SemanticState, Ontology, Concept, Condition
from .core.config import config, using
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
        "data", "force", "energy", "power", "area", "density", "frequency", 
        "currency", "electromagnetism", "photometry"
    ]
    
    for dim in _core_dimensions:
        importlib.import_module(f".units.{dim}", package=__name__)


_bootstrap_units()
del _bootstrap_units

from . import u

__version__ = "0.3.0"

__all__ = [
    "u",
    "baseof",
    "dims",
    "unitsin",
    "dimof",
    "Schema",
    "Field",
    "DerivedField",
    "SemanticState",
    "Ontology",
    "Concept",
    "Condition",
    "post_normalize",
    "pre_normalize",
    "col",
    "convert",
    "config",
    "using",
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