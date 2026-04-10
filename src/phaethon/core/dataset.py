"""
Phaethon Dataset: The Zero-Overhead Physics Columnar Store.

This module provides the central data structure for the Phaethon ecosystem. 
It bridges Data Engineering (Pandas) and SciML (PyTorch) by maintaining a 
strictly vectorized NumPy C-backend while providing zero-copy lazy evaluation 
for physical units and computational graphs.
"""
from __future__ import annotations

import warnings
import inspect
from typing import Any, Mapping, Iterator, TYPE_CHECKING, overload

from .compat import HAS_NUMPY, HAS_TORCH
from .base import BaseUnit, _find_existing_class
from .registry import ureg

if HAS_NUMPY:
    import numpy as np

if TYPE_CHECKING:
    from .compat import DatasetInput, TensorLikeDict
    if HAS_TORCH:
        import torch
        from .pinns.tensor import PTensor


def _auto_map_args(args: tuple[Any, ...]) -> dict[str, Any]:
    """Magically maps positional arguments to variable names from the caller's frame."""
    if not args: return {}
    try:
        caller_frame = inspect.currentframe().f_back.f_back# type: ignore
        caller_locals = caller_frame.f_locals
        id_to_name = {id(v): k for k, v in caller_locals.items() if not k.startswith('_')}
        
        result = {}
        for i, arg in enumerate(args):
            name = id_to_name.get(id(arg), f"var_{i}")
            result[name] = arg
        return result
    finally:
        del caller_frame


class Series:
    """
    An internal proxy representing a single columnar state in the Dataset.
    """
    def __init__(self, key: str, mag_data: np.ndarray, meta: dict[str, Any]) -> None:
        self.name = key
        self._mag = mag_data
        self._meta = meta

    def __getitem__(self, idx: int | slice | np.ndarray) -> Any:
        sliced_mag = self._mag[idx]
        temp_series = Series(self.name, sliced_mag, self._meta)
        return temp_series.value

    @property
    def raw(self) -> np.ndarray:
        """Returns the naked NumPy array, stripping all physical and graph metadata."""
        return self._mag

    @property
    def array(self) -> 'BaseUnit | np.ndarray':
        """Forces resolution as a NumPy-backed physical BaseUnit (or raw array if naked)."""
        if self._meta.get("is_naked", False):
            return self._mag

        dna = frozenset(tuple(x) for x in self._meta.get("signature", []))
        TargetClass = _find_existing_class(dna, float(self._meta.get("base_multiplier", 1.0)))
        if not TargetClass:
            try: TargetClass = ureg().baseof(self._meta.get("dimension", "anonymous"))
            except ValueError: raise RuntimeError(f"Corrupted physical state in '{self.name}'.")

        if self._mag.ndim == 0:
            return TargetClass(float(self._mag))
        return TargetClass(self._mag)

    @property
    def tensor(self) -> 'PTensor | torch.Tensor':
        """Forces resolution as a PyTorch-backed tensor (PTensor or torch.Tensor)."""
        from .compat import require_torch
        require_torch("Series.tensor")
        import torch
        from .pinns.tensor import PTensor

        requires_grad = self._meta.get("requires_grad", False)
        
        if self._meta.get("is_naked", False):
            return torch.tensor(self._mag, dtype=torch.float32, requires_grad=requires_grad)

        dna = frozenset(tuple(x) for x in self._meta.get("signature", []))
        TargetClass = _find_existing_class(dna, float(self._meta.get("base_multiplier", 1.0)))
        if not TargetClass:
            try: TargetClass = ureg().baseof(self._meta.get("dimension", "anonymous"))
            except ValueError: raise RuntimeError(f"Corrupted physical state in '{self.name}'.")

        return PTensor(self._mag, unit=TargetClass, requires_grad=requires_grad)

    @property
    def value(self) -> Any:
        """
        Dynamically resolves to the state encoded in the metadata engine.
        Downgrades gracefully to NumPy if PyTorch is requested but missing.
        """
        if self._meta.get("engine") == "torch":
            if HAS_TORCH: return self.tensor
            else:
                warnings.warn(
                    f"\033[33m[Phaethon Fallback]\033[0m PyTorch missing. "
                    f"Downgrading '{self.name}' to NumPy BaseUnit. Autograd lost.", UserWarning
                )
        return self.array

    def __add__(self, other: Any) -> 'np.ndarray | BaseUnit': return self.value + other
    def __sub__(self, other: Any) -> 'np.ndarray | BaseUnit': return self.value - other
    def __mul__(self, other: Any) -> 'np.ndarray | BaseUnit': return self.value * other
    def __truediv__(self, other: Any) -> 'np.ndarray | BaseUnit': return self.value / other
    def __pow__(self, other: Any) -> 'np.ndarray | BaseUnit': return self.value ** other
    def __lt__(self, other: Any) -> 'np.ndarray': return self.value < other
    def __le__(self, other: Any) -> 'np.ndarray': return self.value <= other
    def __gt__(self, other: Any) -> 'np.ndarray': return self.value > other
    def __ge__(self, other: Any) -> 'np.ndarray': return self.value >= other
    def __eq__(self, other: Any) -> 'np.ndarray': return self.value == other
    def __ne__(self, other: Any) -> 'np.ndarray': return self.value != other

    def __repr__(self) -> str:
        dim = self._meta.get('dimension', 'dimensionless')
        shp = list(self._mag.shape) if self._mag.ndim > 0 else "Scalar"
        return f"<Phaethon Series '{self.name}': Dimension[{dim}] Shape{shp}>"


_MultiIdx = slice | list[int] | np.ndarray

class _IlocIndexer:
    def __init__(self, dataset: 'Dataset') -> None:
        self.ds = dataset

    @overload
    def __getitem__(self, idx: int) -> dict[str, Any]: ...
    
    @overload
    def __getitem__(self, idx: _MultiIdx) -> 'Dataset': ...

    @overload
    def __getitem__(self, idx: tuple[int, int]) -> 'BaseUnit | PTensor | np.ndarray | float': ...

    @overload
    def __getitem__(self, idx: tuple[int, _MultiIdx]) -> dict[str, Any]: ...
    
    @overload
    def __getitem__(self, idx: tuple[_MultiIdx, int]) -> 'Series': ...
    
    @overload
    def __getitem__(self, idx: tuple[_MultiIdx, _MultiIdx]) -> 'Dataset': ...

    def __getitem__(self, idx: Any) -> Any:
        if isinstance(idx, tuple):
            if len(idx) > 2:
                raise IndexError("Too many indexers. Phaethon .iloc only supports 2D indexing [row, col]")
            row_idx = idx[0]
            col_idx = idx[1] if len(idx) == 2 else slice(None)
        else:
            row_idx = idx
            col_idx = slice(None)

        all_keys = list(self.ds.keys())
        
        if isinstance(col_idx, int):
            target_keys = [all_keys[col_idx]]
            single_col = True
        elif isinstance(col_idx, slice):
            target_keys = all_keys[col_idx]
            single_col = False
        elif isinstance(col_idx, (list, np.ndarray)):
            target_keys = [all_keys[i] for i in col_idx]
            single_col = False
        else:
            raise TypeError(f"Invalid column indexer type: {type(col_idx)}")

        single_row = isinstance(row_idx, int) and not isinstance(row_idx, bool)


        if single_row and single_col:
            k = target_keys[0]
            arr = self.ds._mag_store[k]
            val_mag = arr if arr.ndim == 0 else arr[row_idx]
            return Series(k, val_mag, self.ds._meta_store[k]).value
            
        elif single_row and not single_col:
            res = {}
            for k in target_keys:
                arr = self.ds._mag_store[k]
                val_mag = arr if arr.ndim == 0 else arr[row_idx]
                res[k] = Series(k, val_mag, self.ds._meta_store[k]).value
            return res
            
        elif not single_row and single_col:
            k = target_keys[0]
            arr = self.ds._mag_store[k]
            val_mag = arr if arr.ndim == 0 else arr[row_idx]
            return Series(k, val_mag, self.ds._meta_store[k])
            
        else:
            new_ds = self.ds.__class__.__new__(self.ds.__class__) 
            new_ds._meta_store = {k: self.ds._meta_store[k] for k in target_keys}
            new_ds._mag_store = {}
            
            for k in target_keys:
                arr = self.ds._mag_store[k]
                if arr.ndim == 0: 
                    new_ds._mag_store[k] = arr 
                else: 
                    new_ds._mag_store[k] = arr[row_idx]
                    
            new_ds._calculate_length()
            return new_ds


class Dataset(Mapping[str, Series]):
    """    A unified, dimension-aware columnar data structure.
    """
    
    def __init__(self, data: DatasetInput | None = None, *args: Any, **kwargs: Any) -> None:
        if not HAS_NUMPY:
            raise ImportError("Dataset requires 'numpy' as its core vector engine.")

        self._mag_store: dict[str, np.ndarray] = {}
        self._meta_store: dict[str, dict[str, Any]] = {}
        self._length: int = 1

        payload = {}
        
        if data is not None:
            if isinstance(data, dict):
                payload.update(data)
            elif isinstance(data, (list, tuple)) and not isinstance(data[0], BaseUnit):
                payload.update({str(i): v for i, v in enumerate(data)})
            else:
                payload.update(_auto_map_args((data,) + args))
        elif args:
            payload.update(_auto_map_args(args))
            
        if kwargs:
            payload.update(kwargs)

        for key, item in payload.items():
            self._ingest_column(str(key), item)
            
        self._calculate_length()

    def _ingest_column(self, key: str, item: Any) -> None:
        """Strips physical and autodiff wrappers, storing pure numerical state."""
        is_ptensor = type(item).__name__ == "PTensor"
        is_baseunit = isinstance(item, BaseUnit) or (isinstance(item, type) and issubclass(item, BaseUnit))

        meta: dict[str, Any] = {
            "is_naked": True, "engine": "numpy", "dimension": "dimensionless", "symbol": ""
        }
        
        if is_baseunit or is_ptensor:
            unit_source = item.unit if is_ptensor else item
            meta.update({
                "is_naked": False,
                "dimension": getattr(unit_source, 'dimension', 'anonymous'),
                "signature": [list(x) for x in getattr(unit_source, '_signature', frozenset())],
                "base_multiplier": float(getattr(unit_source, 'base_multiplier', 1.0)),
                "symbol": getattr(unit_source, 'symbol', ''),
            })
            mag_data = item.mag
        else:
            mag_data = item

        if HAS_TORCH and type(mag_data).__name__ == "Tensor":
            meta["engine"] = "torch"
            meta["requires_grad"] = mag_data.requires_grad
            mag_data = mag_data.detach().cpu().numpy()

        if not isinstance(mag_data, np.ndarray):
            mag_data = np.array(mag_data, dtype=np.float64)

        meta["shape"] = list(mag_data.shape)
        meta["dtype"] = str(mag_data.dtype)
        
        self._mag_store[key] = mag_data
        self._meta_store[key] = meta

    def _calculate_length(self) -> None:
        """Determines the tabular row length based on 1D+ arrays."""
        lengths = [arr.shape[0] for arr in self._mag_store.values() if arr.ndim > 0]
        self._length = max(lengths) if lengths else 1

    @overload
    def __getitem__(self, key: str) -> Series: ...
    @overload
    def __getitem__(self, key: list[str] | tuple[str, ...]) -> 'Dataset': ...
    @overload
    def __getitem__(self, key: Any) -> 'Dataset': ...
    def __getitem__(self, key: Any) -> Any:
        if isinstance(key, str):
            if key not in self._meta_store:
                raise KeyError(f"Column '{key}' not found in Dataset.")
            return Series(key, self._mag_store[key], self._meta_store[key])
            
        if isinstance(key, Series):
            key = key.raw
            
        if HAS_NUMPY and isinstance(key, np.ndarray) and key.dtype == bool:
            if key.ndim != 1:
                raise ValueError("Boolean mask must be 1-dimensional.")
            
            new_ds = self.__class__.__new__(self.__class__)
            new_ds._meta_store = self._meta_store.copy()
            new_ds._mag_store = {}
            
            for k, v in self._mag_store.items():
                if v.ndim > 0:
                    safe_mask = key[:v.shape[0]]
                    new_ds._mag_store[k] = v[safe_mask]
                else:
                    new_ds._mag_store[k] = v
                    
            new_ds._calculate_length()
            return new_ds
            
        if isinstance(key, (list, tuple)):
            new_ds = self.__class__.__new__(self.__class__)
            new_ds._meta_store = {k: self._meta_store[k] for k in key}
            new_ds._mag_store = {k: self._mag_store[k] for k in key}
            new_ds._calculate_length()
            return new_ds

        raise TypeError(f"Invalid indexer type for Dataset: {type(key).__name__}")

    def __iter__(self) -> Iterator[str]:
        return iter(self._meta_store)

    def __len__(self) -> int:
        return len(self._meta_store)

    def to_pandas(self, raw: bool = True) -> Any:
        """
        Converts the Dataset into a standard Pandas DataFrame.
        Args:
            raw: If True (default), strips physics and returns naked float arrays 
                 to ensure optimal Pandas C-engine compatibility (preventing dtype=object).
        """
        from .compat import HAS_PANDAS
        if not HAS_PANDAS: raise ImportError("Pandas is required. Install via: pip install pandas")
        import pandas as pd
        
        payload = {k: (self[k].raw if raw else self[k].value) for k in self.keys()}
        return pd.DataFrame(payload)

    def to_polars(self, raw: bool = True) -> Any:
        """Converts the Dataset into a Polars DataFrame."""
        from .compat import HAS_POLARS
        if not HAS_POLARS: raise ImportError("Polars is required. Install via: pip install polars")
        import polars as pl
        
        payload = {k: (self[k].raw if raw else self[k].value) for k in self.keys()}
        return pl.DataFrame(payload)

    def tensors(self, requires_grad: bool | None = None) -> TensorLikeDict:
        """Mass-extracts all columns directly into PyTorch-backed Tensors."""
        res = {}
        for k in self.keys():
            t = self[k].tensor
            if requires_grad is not None and not self._meta_store[k].get("is_naked", False):
                t.requires_grad_(requires_grad)
            res[k] = t
        return res

    @property
    def iloc(self) -> _IlocIndexer:
        """
        2D integer-location based indexing for selection by position.
        """
        return _IlocIndexer(self)
    
    def info(self) -> None:
        """Prints a comprehensive structural and physical schema of the Dataset."""
        if not self._meta_store:
            print(f"<Dataset: 0 columns, 0 rows>")
            return

        max_k = max(15, max((len(k) for k in self._meta_store.keys()), default=0))
        max_d = max(18, max((len(str(m.get('dimension', 'dimensionless'))) for m in self._meta_store.values()), default=0))
        max_s = max(12, max((len(str(tuple(m.get('shape', [])))) for m in self._meta_store.values()), default=0))
        
        print(f"<Dataset: {len(self)} columns, {self._length:,} rows>")
        
        header = f"| {'Key':<{max_k}} | {'Dimension':<{max_d}} | {'Engine':<8} | {'Shape':<{max_s}} | {'SHA-256':<10} |"
        sep = "-" * len(header)
        
        print(sep)
        print(header)
        print(sep)
        
        for k, meta in self._meta_store.items():
            dim = meta.get('dimension', 'dimensionless')
            eng = meta.get('engine', 'numpy')
            shp = str(tuple(meta.get('shape', [])))
            sha = meta.get('sha256_checksum', 'None')[:8]
            print(f"| {k:<{max_k}} | {dim:<{max_d}} | {eng:<8} | {shp:<{max_s}} | {sha:<10} |")
        print(sep)

    def _render_table(self, indices: list[int]) -> str:
        keys = list(self.keys())
        if not keys: return "Empty Dataset"

        col_widths = {"__index__": 6}
        display_data = {k: [] for k in keys}
        
        for k in keys:
            unit_sym = self._meta_store[k].get('symbol', '')
            title = f"{k} ({unit_sym})" if unit_sym else k
            max_w = len(title)
            
            arr = self._mag_store[k]
            is_scalar = arr.ndim == 0
            
            for idx in indices:
                if idx == -1: # Signal for "..."
                    val_str = "..."
                elif is_scalar:
                    val = arr.item()
                    val_str = f"{val:.4f}" if isinstance(val, (float, np.floating)) else str(val)
                else:
                    if idx < arr.shape[0]:
                        if arr.ndim == 1:
                            val = arr[idx]
                            val_str = f"{val:.4f}" if isinstance(val, (float, np.floating)) else str(val)
                        else:
                            eng_type = "Tensor" if self._meta_store[k].get("engine") == "torch" else "Array"
                            val_str = f"<{eng_type} {arr[idx].shape}>"
                    else:
                        val_str = "NaN"
                        
                display_data[k].append(val_str)
                max_w = max(max_w, len(val_str))
                
            col_widths[k] = min(max_w + 2, 28)

        lines = []
        header_parts = [f"| {'Index':<{col_widths['__index__']}} "]
        for k in keys:
            unit_sym = self._meta_store[k].get('symbol', '')
            title = f"{k} ({unit_sym})" if unit_sym else k
            if len(title) > col_widths[k]: title = title[:col_widths[k]-3] + "..."
            header_parts.append(f"| {title:<{col_widths[k]}} ")
        header_parts.append("|")
        
        header_str = "".join(header_parts)
        lines.append(f"<Dataset: {len(self)} columns, {self._length:,} rows>")
        lines.append("-" * len(header_str))
        lines.append(header_str)
        lines.append("-" * len(header_str))

        for i, raw_idx in enumerate(indices):
            idx_display = "..." if raw_idx == -1 else str(raw_idx)
            row_parts = [f"| {idx_display:<{col_widths['__index__']}} "]
            for k in keys:
                val_str = display_data[k][i]
                if len(val_str) > col_widths[k]: val_str = val_str[:col_widths[k]-3] + "..."
                row_parts.append(f"| {val_str:<{col_widths[k]}} ")
            row_parts.append("|")
            lines.append("".join(row_parts))
        lines.append("-" * len(header_str))
        
        return "\n".join(lines)

    def head(self, n: int = 5) -> 'Dataset':
        """Returns the first n rows as a new Dataset."""
        return self.iloc[:n]

    def tail(self, n: int = 5) -> 'Dataset':
        """Returns the last n rows as a new Dataset."""
        return self.iloc[-n:]
        
    def __repr__(self) -> str:
        """Called automatically when the object is evaluated or printed."""
        if self._length <= 10:
            return self._render_table(list(range(self._length)))
        else:
            idx = list(range(5)) + [-1] + list(range(self._length - 5, self._length))
            return self._render_table(idx)

    def __str__(self) -> str:
        return self.__repr__()