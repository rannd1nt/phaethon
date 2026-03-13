from __future__ import annotations

from typing import Any, TYPE_CHECKING, TypeAlias, Iterable, TypeVar, Callable, Literal

SCHEMA_COMPAT = True

try:
    import pandas as pd
    HAS_PANDAS = True
except ImportError:
    HAS_PANDAS = False

try:
    import polars as pl
    HAS_POLARS = True
except ImportError:
    HAS_POLARS = False

if not HAS_PANDAS and not HAS_POLARS:
    SCHEMA_COMPAT = False

# =========================================================================
# THE TYPE REGISTRY
# =========================================================================
# =========================================================================
# THE TYPE REGISTRY
# =========================================================================
if TYPE_CHECKING:
    import pandas as pd
    import numpy as np
    import polars as pl
    from decimal import Decimal
    from .base import BaseUnit

    # --- 1. CORE TYPES (The "Like"s for normalizers) ---
    DataFrameLike: TypeAlias = pd.DataFrame | pl.DataFrame
    """Accepts either a Pandas DataFrame or a Polars DataFrame."""
    
    NumericLike: TypeAlias = int | float | str | Decimal | np.ndarray | Iterable[Any]
    """Accepts standard Python numbers, Decimals, numeric strings, arrays, or iterables."""
    
    UnitLike: TypeAlias = str | type[BaseUnit]
    """Accepts a formal BaseUnit class (e.g., u.Meter) or a string alias (e.g., 'km')."""
    
    # --- 2. INPUT & TARGETS (The Nouns) ---
    ConvertibleInput: TypeAlias = NumericLike | 'BaseUnit' | Iterable['BaseUnit']
    """The raw magnitude or physical object to be ingested by the engine."""
    
    ColumnTarget: TypeAlias = str | Any
    """Represents a column name string or an Ellipsis (...) for auto-mapping."""

    # --- 3. DICTIONARIES & REGISTRIES ---
    ContextDict: TypeAlias = dict[str, NumericLike | BaseUnit]
    """Environmental variables (scalars or units) for dynamic physics axioms."""
    
    AliasRegistry: TypeAlias = dict[str, str | list[str]]
    """Mapping of official unit symbols to a list of dirty/custom string aliases."""

    # --- 4. ENGINE BEHAVIORS & METHODS (The Literals) ---
    ImputeMethod: TypeAlias = Literal['mean', 'median', 'mode', 'ffill', 'bfill'] | str | float
    """Method for handling NaN values (statistical, fill-forward, or physical constants)."""
    
    ErrorAction: TypeAlias = Literal['raise', 'coerce', 'clip']
    """
    Defines the engine's behavior upon encountering a violation:
    - 'raise': Crash and throw an exception.
    - 'coerce': Neutralize bad data to NaN/Null.
    - 'clip': Force bad data to the nearest logical boundary.
    """
else:
    DataFrameLike: TypeAlias = Any
    NumericLike: TypeAlias = Any
    UnitLike: TypeAlias = Any
    ConvertibleInput: TypeAlias = Any
    ColumnTarget: TypeAlias = Any
    ContextDict: TypeAlias = Any
    AliasRegistry: TypeAlias = Any
    ImputeMethod: TypeAlias = Any
    ErrorAction: TypeAlias = Any

_Signature: TypeAlias = frozenset[tuple[str, int]]
_T_DF = TypeVar("_T_DF", bound=DataFrameLike)
_T_Num = TypeVar("_T_Num", bound=NumericLike)
_T_Unit = TypeVar("_T_Unit", bound='BaseUnit')
_T_Cls = TypeVar("_T_Cls", bound=type)
_T_Fn = TypeVar("_T_Fn", bound=Callable[..., Any])
_T_Out = TypeVar("_T_Out")

# =========================================================================
# COMPATIBILITY HELPERS
# =========================================================================
def is_pandas_df(df: Any) -> bool:
    return HAS_PANDAS and df.__class__.__module__.startswith('pandas')

def is_polars_df(df: Any) -> bool:
    return HAS_POLARS and df.__class__.__module__.startswith('polars')