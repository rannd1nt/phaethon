from __future__ import annotations

import importlib.util
import importlib.metadata
import warnings
from packaging.version import parse
from typing import Any, TYPE_CHECKING, TypeAlias, Iterable, TypeVar, Callable, Literal, Protocol, Mapping


def _check_dep(module_name: str, package_name: str | None = None) -> tuple[bool, str | None]:
    if package_name is None:
        package_name = module_name
        
    if importlib.util.find_spec(module_name) is not None:
        try:
            return True, importlib.metadata.version(package_name)
        except importlib.metadata.PackageNotFoundError:
            return True, "unknown"
    return False, None

def _require_min_version(pkg_name: str, current_ver: str | None, min_ver: str) -> None:
    if current_ver and current_ver != "unknown":
        if parse(current_ver) < parse(min_ver):
            warnings.warn(
                f"\033[33m[Phaethon Warning]\033[0m {pkg_name} version {current_ver} is installed, "
                f"but Phaethon recommends >= {min_ver}. Expect potential instability."
            )

HAS_NUMPY, NUMPY_VERSION = _check_dep("numpy")
HAS_PANDAS, PANDAS_VERSION = _check_dep("pandas")
HAS_POLARS, POLARS_VERSION = _check_dep("polars")
HAS_SKLEARN, SKLEARN_VERSION = _check_dep("sklearn", "scikit-learn")
HAS_TORCH, TORCH_VERSION = _check_dep("torch")
HAS_RAPIDFUZZ, RAPIDFUZZ_VERSION = _check_dep("rapidfuzz")
HAS_PYARROW, PYARROW_VERSION = _check_dep("pyarrow")
HAS_H5PY, H5PY_VERSION = _check_dep("h5py")

if not HAS_NUMPY:
    raise ImportError("Phaethon requires 'numpy' as its core engine. Please install it: pip install numpy>=1.26.0")
_require_min_version("numpy", NUMPY_VERSION, "1.26.0")

SCHEMA_COMPAT = HAS_PANDAS or HAS_POLARS

def require_dataframe_backend(feature_name: str = "This feature") -> None:
    if not SCHEMA_COMPAT:
        raise ImportError(f"{feature_name} requires Pandas or Polars. Install via: pip install 'phaethon[dataframe]'")

def require_torch(feature_name: str = "This feature") -> None:
    if not HAS_TORCH:
        raise ImportError(f"{feature_name} requires PyTorch. Install via: pip install 'phaethon[pinns]' or torch>=2.0.0")

def require_sklearn(feature_name: str = "This feature") -> None:
    if not HAS_SKLEARN:
        raise ImportError(f"{feature_name} requires Scikit-Learn. Install via: pip install 'phaethon[ml]' or scikit-learn>=1.3.0")

def require_parquet(feature_name: str = "Parquet I/O") -> None:
    if not HAS_PYARROW:
        raise ImportError(f"{feature_name} requires PyArrow. Install via: pip install 'phaethon[io]' or pyarrow>=14.0.0")

def require_h5py(feature_name: str = "HDF5 I/O") -> None:
    if not HAS_H5PY:
        raise ImportError(f"{feature_name} requires h5py. Install via: pip install 'phaethon[io]' or h5py>=3.0.0")


# =========================================================================
# THE TYPE REGISTRY & CONFIGURATIONS
# =========================================================================
if TYPE_CHECKING:
    from typing import TypedDict, Unpack
    if HAS_POLARS: import polars as pl
    if HAS_PANDAS: import pandas as pd
    if HAS_NUMPY: import numpy as np
    if HAS_TORCH: import torch
    from .base import BaseUnit

    DataFrameLike: TypeAlias = pd.DataFrame | pl.DataFrame
    NumericLike: TypeAlias = int | float | str | np.ndarray | Iterable[Any]
    UnitLike: TypeAlias = str | type[BaseUnit]

    ConvertibleInput: TypeAlias = NumericLike | 'BaseUnit' | Iterable['BaseUnit']
    ColumnTarget: TypeAlias = str | Any
    Extractable: TypeAlias = BaseUnit | torch.Tensor | np.ndarray | float | int | str | list[Any] | tuple[Any, ...] | None
    UnwrappedArray: TypeAlias = np.ndarray | float | int | None

    ContextDict: TypeAlias = dict[str, NumericLike | BaseUnit]
    AliasRegistry: TypeAlias = dict[str, str | list[str]]

    ImputeMethod: TypeAlias = Literal['mean', 'median', 'mode', 'ffill', 'bfill'] | str | float
    InterpolationMethod = Literal[
        "linear", "nearest", "time", "index", "values", "pad", "zero", "slinear","quadratic",
        "cubic", "spline", "barycentric", "polynomial", "krogh","piecewise_polynomial",
        "pchip", "akima", "cubicspline"
    ]
    ErrorAction: TypeAlias = Literal['raise', 'coerce', 'clip']
    StrictnessLevel = Literal["default", "strict", "strict_warn", "loose_warn", "ignore"]
    NumDtype: TypeAlias = Literal["float64", "float32", "float16", "int64", "int32"]

    if HAS_TORCH:
        from .pinns.tensor import PTensor
        TensorLikeDict: TypeAlias = dict[str, PTensor | torch.Tensor]
        TensorLikeTuple: TypeAlias = tuple[PTensor | torch.Tensor, ...]
        GradTarget: TypeAlias = bool | list[str]

    class _ParquetConfig(TypedDict, total=False):
        engine: Literal["pyarrow", "fastparquet", "auto"]
        compression: Literal["snappy", "gzip", "brotli", "lz4", "zstd"]
        index: bool
        partition_cols: list[str]

    class _HDF5Config(TypedDict, total=False):
        compression: Literal["gzip", "lzf", "szip"]
        compression_opts: int
        chunks: bool | tuple[int, ...]

    DatasetInput: TypeAlias = Mapping[str, Any] | Iterable[Any] | Any
    DatasetStateDict: TypeAlias = dict[str, dict[str, Any]]

    class _ResponsiveTableConfig(TypedDict, total=False):
        max_col_width: int
        float_format: str
        justify: Literal["left", "right", "center"]
        
else:
    DataFrameLike: TypeAlias = Any
    NumericLike: TypeAlias = Any
    UnitLike: TypeAlias = Any
    ConvertibleInput: TypeAlias = Any
    ColumnTarget: TypeAlias = Any
    Extractable: TypeAlias = Any
    UnwrappedArray: TypeAlias = Any
    ContextDict: TypeAlias = Any
    AliasRegistry: TypeAlias = Any
    ImputeMethod: TypeAlias = Any
    InterpolationMethod: TypeAlias = Any
    ErrorAction: TypeAlias = Any
    StrictnessLevel: TypeAlias = Any
    NumDtype: TypeAlias = Any
    TensorLikeDict: TypeAlias = Any
    TensorLikeTuple: TypeAlias = Any
    GradTarget: TypeAlias = Any

_Signature: TypeAlias = frozenset[tuple[str, int]]
_DataFrameT = TypeVar("_DataFrameT", bound=DataFrameLike)
_NumericT = TypeVar("_NumericT", bound=NumericLike)
_UnitT = TypeVar("_UnitT", bound='BaseUnit')
_UnitT_co = TypeVar("_UnitT_co", bound='BaseUnit', covariant=True)
_UnitClassT = TypeVar("_UnitClassT", bound=type)
_CallableT = TypeVar("_CallableT", bound=Callable[..., Any])
_ReturnT = TypeVar("_ReturnT")
_KeyT = TypeVar('_KeyT')

class SupportsPredict(Protocol):
    def fit(self, X: Any, y: Any = None, **kwargs: Any) -> Any: ...
    def predict(self, X: Any) -> Any: ...

class SupportsTransform(Protocol):
    def fit(self, X: Any, y: Any = None, **kwargs: Any) -> Any: ...
    def transform(self, X: Any) -> Any: ...

class SupportsInverseTransform(SupportsTransform, Protocol):
    def inverse_transform(self, X: Any) -> Any: ...

_EstimatorT = TypeVar("_EstimatorT", bound=SupportsPredict)
_TransformerT = TypeVar("_TransformerT", bound=SupportsTransform)
_InvTransformerT = TypeVar("_InvTransformerT", bound=SupportsInverseTransform)

# =========================================================================
# COMPATIBILITY HELPERS
# =========================================================================
def is_pandas_df(df: Any) -> bool:
    return HAS_PANDAS and df.__class__.__module__.startswith('pandas')

def is_polars_df(df: Any) -> bool:
    return HAS_POLARS and df.__class__.__module__.startswith('polars')