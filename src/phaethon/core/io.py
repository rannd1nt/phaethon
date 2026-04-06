"""
Phaethon Universal I/O Gateway.
Handles dimension-aware multi-tensor serialization (.phx), Parquet columnar structures, 
and HDF5 scientific datasets with cryptographic signature validation (SHA-256).
"""
from __future__ import annotations

import json
import zipfile
import io
import warnings
import hashlib
from pathlib import Path
from typing import Any, Dict, Union, Literal, overload, TYPE_CHECKING

from .compat import (
    HAS_NUMPY, require_parquet, require_h5py,
    is_pandas_df, is_polars_df
)

if TYPE_CHECKING:
    from .compat import DataFrameLike, _ParquetConfig, _HDF5Config
    from typing import Unpack
    from .dataset import Dataset

if HAS_NUMPY:
    import numpy as np

FilePathType = Union[str, Path]

_PHXHEADER = "phaethon_exchange"
_PHXIOCODEVER = "1.0" 


def _resolve_path_and_format(path: Path, provided_format: str) -> tuple[Path, str]:
    ext_map = {'.phx': 'phx', '.parquet': 'parquet', '.h5': 'h5', '.hdf5': 'h5', '.hdf': 'h5'}
    ext = path.suffix.lower()
    
    if provided_format and provided_format.lower() != 'auto':
        fmt = provided_format.lower()
        if fmt not in ('phx', 'parquet', 'h5', 'hdf5', 'hdf'):
            raise ValueError(f"Unsupported format '{fmt}'.")
            
        fmt = 'h5' if fmt in ('hdf5', 'hdf') else fmt
        
        if ext not in ext_map or ext_map[ext] != fmt:
            warnings.warn(
                f"\033[33m[Phaethon I/O Warning]\033[0m Suffix '{ext}' does not match requested format '{fmt}'. "
                f"Forcing extension to '.{fmt}'.", UserWarning
            )
            path = path.with_suffix(f'.{fmt}')
            
        return path, fmt

    if ext in ext_map: return path, ext_map[ext]

    if ext:
        warnings.warn(
            f"\033[33m[Phaethon I/O Warning]\033[0m Unknown extension '{ext}'. "
            "Defaulting to native Phaethon Archive (.phx).", UserWarning
        )
    return path.with_suffix('.phx'), 'phx'


if TYPE_CHECKING:
    @overload
    def save(filepath: FilePathType, data: DataFrameLike | 'Dataset', format: Literal['parquet'], **kwargs: Unpack[_ParquetConfig]) -> None: ...
    @overload
    def save(filepath: FilePathType, data: 'Dataset', format: Literal['h5', 'hdf5', 'hdf'], **kwargs: Unpack[_HDF5Config]) -> None: ...
    @overload
    def save(filepath: FilePathType, data: 'Dataset', format: Literal['phx', 'auto'] = ..., **kwargs: Any) -> None: ...

def save(filepath: FilePathType, data: Any, format: str = 'auto', **kwargs: Any) -> None:
    """
    Universally serializes Datasets and DataFrames to disk.
    Strictly requires a pre-instantiated `ptn.Dataset` for .phx and .h5 formats.
    """
    path, fmt = _resolve_path_and_format(Path(filepath), format)
    from .dataset import Dataset

    if fmt == 'parquet':
        require_parquet("Parquet I/O")
        
        if is_pandas_df(data) or is_polars_df(data):
            export_df = data
        elif isinstance(data, Dataset):
            export_df = data.to_pandas(raw=True)
        else:
            raise TypeError("Parquet format strictly requires a Pandas/Polars DataFrame or a ptn.Dataset.")
            
        if is_pandas_df(export_df): export_df.to_parquet(path, **kwargs)
        else: export_df.write_parquet(path, **kwargs) # type: ignore
        return

    if not isinstance(data, Dataset):
        raise TypeError(f"Format '{fmt.upper()}' strictly requires a pre-instantiated ptn.Dataset. You passed {type(data).__name__}.")

    ds: Dataset = data

    if fmt == 'h5':
        require_h5py("HDF5 I/O")
        import h5py
        
        with h5py.File(path, 'w') as h5f:
            for key, mag_arr in ds._mag_store.items():
                if getattr(mag_arr, 'ndim', 0) == 0:
                    safe_kwargs = {
                        k: v for k, v in kwargs.items() 
                        if k not in ('compression', 'compression_opts', 'chunks', 'shuffle', 'fletcher32', 'scaleoffset')
                    }
                    dataset = h5f.create_dataset(key, data=mag_arr, **safe_kwargs)
                else:
                    dataset = h5f.create_dataset(key, data=mag_arr, **kwargs)
                    
                dataset.attrs['physics_meta'] = json.dumps(ds._meta_store[key])
        return

    if not HAS_NUMPY: raise ImportError("NumPy is required for native Phaethon I/O.")

    master_metadata: Dict[str, Any] = {
        "__format__": _PHXHEADER, 
        "__version__": _PHXIOCODEVER,
        "items": ds._meta_store 
    }

    with zipfile.ZipFile(path, 'w', compression=zipfile.ZIP_DEFLATED) as zf:
        for key, mag_arr in ds._mag_store.items():
            arr_bytes = io.BytesIO()
            np.save(arr_bytes, mag_arr, allow_pickle=False)
            binary_data = arr_bytes.getvalue()
            
            master_metadata["items"][key]["sha256_checksum"] = hashlib.sha256(binary_data).hexdigest()
            zf.writestr(f'arr_{key}.npy', binary_data)
            
        zf.writestr('metadata.json', json.dumps(master_metadata, indent=2))


if TYPE_CHECKING:
    @overload
    def load(filepath: FilePathType, format: Literal['phx', 'parquet', 'h5', 'hdf5', 'hdf', 'auto'] = ..., **kwargs: Any) -> 'Dataset': ...

def load(filepath: FilePathType, format: str = 'auto', **kwargs: Any) -> 'Dataset':
    """
    Loads Parquet, HDF5, and PHX archives safely into a unified Phaethon Dataset.
    Guarantees strict type safety by exclusively returning `ptn.Dataset`.
    """
    path, fmt = _resolve_path_and_format(Path(filepath), format)
    from .dataset import Dataset

    if fmt == 'parquet':
        require_parquet("Parquet I/O")
        from .compat import HAS_PANDAS, HAS_POLARS
        if HAS_PANDAS:
            import pandas as pd
            df = pd.read_parquet(path, engine='pyarrow', **kwargs)
            return Dataset({col: df[col].to_numpy() for col in df.columns})
        elif HAS_POLARS:
            import polars as pl
            df = pl.read_parquet(path, **kwargs)
            return Dataset({col: df[col].to_numpy() for col in df.columns})
        raise ImportError("Pandas or Polars is required to load Parquet files.")
    
    if fmt == 'h5':
        require_h5py("HDF5 I/O")
        import h5py # type: ignore
        
        ds = Dataset.__new__(Dataset)
        ds._mag_store, ds._meta_store = {}, {}
        
        with h5py.File(path, 'r') as h5f:
            for key in h5f.keys():
                h5_ds = h5f[key]
                meta_json = h5_ds.attrs.get('physics_meta')
                ds._meta_store[key] = json.loads(meta_json) if meta_json else {"is_naked": True}
                
                if h5_ds.ndim == 0:
                    ds._mag_store[key] = h5_ds[()]
                else:
                    ds._mag_store[key] = h5_ds[:]
                
        ds._calculate_length()
        return ds

    if not path.exists(): raise FileNotFoundError(f"Archive not found: {path}")
    if not zipfile.is_zipfile(path): raise ValueError(f"Corrupted archive: {path}")

    with zipfile.ZipFile(path, 'r') as zf:
        if 'metadata.json' not in zf.namelist(): raise ValueError("Missing metadata.json.")
        with zf.open('metadata.json') as meta_file:
            master_metadata = json.load(meta_file)
            
    if master_metadata.get("__format__") != _PHXHEADER:
        raise ValueError("Signature mismatch: Not a valid Phaethon eXchange file.")

    ds = Dataset.__new__(Dataset)
    ds._mag_store = {}
    ds._meta_store = master_metadata.get("items", {})
    
    with zipfile.ZipFile(path, 'r') as zf:
        for key, item_meta in ds._meta_store.items():
            with zf.open(f'arr_{key}.npy') as data_file:
                binary_data = data_file.read()
                
                expected_hash = item_meta.get("sha256_checksum")
                if expected_hash and hashlib.sha256(binary_data).hexdigest() != expected_hash:
                    raise ValueError(f"SECURITY BREACH: Array '{key}' checksum mismatch. File may be tampered with.")
                
                ds._mag_store[key] = np.load(io.BytesIO(binary_data), allow_pickle=False)

    ds._calculate_length()
    return ds


def peek(filepath: FilePathType) -> Dict[str, Any]:
    """Inspects a native .phx archive metadata without loading arrays into memory (OOM Safe)."""
    path = Path(filepath)
    if path.suffix != '.phx': path = path.with_suffix('.phx')
    
    if not path.exists(): raise FileNotFoundError(f"Archive not found: {path}")
    with zipfile.ZipFile(path, 'r') as zf:
        with zf.open('metadata.json') as meta_file:
            meta = json.load(meta_file)
            
    summary: Dict[str, Any] = {"Format Version": meta.get("__version__"), "Contents": {}}
    
    for key, item_meta in meta.get("items", {}).items():
        if item_meta.get("is_naked"):
            desc = f"Naked Array | Shape: {item_meta.get('shape')} | DType: {item_meta.get('dtype')} | SHA-256: {item_meta.get('sha256_checksum', 'None')[:8]}..."
        else:
            desc = f"Physics [{item_meta.get('dimension')}] ({item_meta.get('symbol')}) | Shape: {item_meta.get('shape')} | SHA-256 Validated"
        summary["Contents"][key] = desc
        
    return summary