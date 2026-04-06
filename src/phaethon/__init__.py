"""
Phaethon: The End-to-End Physics-Constrained Scientific Computing & Sci-ML Framework
-----------------

Phaethon is an enterprise-grade scientific computing framework that fundamentally 
redefines the lifecycle of physical data in Python. It provides a unified, 
end-to-end ecosystem bridging the gap between messy real-world data and advanced machine learning.

With a custom zero-allocation Rust backend to fuse physical string parsing and data ingestion pipelines, 
rigorous dimensional tensor mechanics, and physics-constrained neural networks, Phaethon ensures absolute 
mathematical and physical integrity from raw sensor streams all the way to complex PDE simulations.

Core Architecture
-----------------
#### Dimensional Engine (phaethon.units)
    A comprehensive dimensional algebra system supporting 90+ domains that goes 
    beyond simple unit conversion by enforcing absolute physical integrity. It 
    utilizes Isomorphic Firewalls and Semantic Domain Locks to strictly isolate 
    semantically distinct entities that share identical mathematical base units. 
    It natively resolves non-linear algebra, enabling real-time logarithmic scale 
    computations and instant baseline linearization. Engineered for seamless 
    vectorization, it features zero-overhead tensor mechanics for NumPy broadcasting 
    across high-dimensional arrays and complex matrix operations, while automatically 
    collapsing perfectly balanced physical ratios down to pure dimensionless scalars.

#### Hybrid Data Engineering (phaethon.Schema)
    A multi-language tabular processing engine with a custom zero-allocation Rust backend to fuse physical 
    string parsing and utilizing C++ (RapidFuzz) for fuzzy ontology matching, unit resolution, and Axiom enforcement. This hybrid core 
    bypasses standard Python string bottlenecks, enabling both Pandas and Polars 
    to normalize millions of irregular records with exceptional throughput.
    Dependency Note:
        Requires tabular backends.
        Install via: `pip install 'phaethon[dataframe]'` (Pandas + RapidFuzz)
        Or for extreme scale: `pip install 'phaethon[polars]'`

#### Polyglot I/O & Storage (phaethon.Dataset, phaethon.save, phaethon.load)
    A highly optimized, multi-modal columnar store with a Pandas-like UX that 
    seamlessly orchestrates zero-dimensional scalars, n-dimensional arrays, and 
    computational tensors into a unified tabular structure. Backed by universal 
    root-level I/O targeting .phx, .h5, and .parquet formats for cross-language 
    scientific interoperability.
    Dependency Note:
        HDF5 and Parquet formats require the `io` optional dependency group.
        Install via: `pip install 'phaethon[io]'` (or `[h5]`, `[arrow]` individually)

#### Classical Sci-ML (phaethon.ml)
    A Scikit-Learn bridge that forces predictive algorithms to respect physical 
    dimensions. It features automated feature synthesis via the Buckingham Pi 
    Theorem and rigorously bounds machine learning predictions back into physical 
    reality using declarative mathematical axioms.
    Dependency Note:
        Requires Scikit-Learn.
        Install via: `pip install 'phaethon[sklearn]'` or `pip install 'phaethon[sciml]'`

#### Deep Learning & PINNs (phaethon.pinns)
    Deep PyTorch integration providing physics-aware autograd tensors (PTensor). 
    Equipped with native physical calculus for solving coupled partial differential 
    equations and spectral layers for advanced neural operator architectures. It 
    tracks physical states dynamically, ensuring absolute dimensional safety and 
    unit coherence throughout the entire backpropagation graph without compromising 
    the computational model's integrity.
    Dependency Note:
        Requires PyTorch.
        Install via: `pip install 'phaethon[torch]'` or `pip install 'phaethon[sciml]'`
"""

from .core.registry import baseof, dims, unitsin, dimof
from .core.schema import Schema, Field, DerivedField, post_normalize, pre_normalize, col
from .core.semantics import SemanticState, Ontology, Concept, Condition
from .core.config import config, using
from .core.plotting import symtag, unwrap
from .core.dataset import Dataset
from .core.io import load, save, peek
from .core import constants as const
from .core import vmath
from .core.fluent import convert
from .core.tensor import array, asarray, asanyarray

Schema.normalize
from . import axiom
from . import units
from . import linalg
from . import random

__version__ = "0.4.0"

__all__ = [
    "units",
    "exceptions",
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
    "const",
    "vmath",
    "symtag",
    "unwrap",
    "Dataset",
    "load",
    "save",
    "peek",
    "random",
    "linalg",
    "array",
    "asarray",
    "asanyarray"
]