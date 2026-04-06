"""
Phaethon Visual Analytics Adapter.
Provides 'Ghost Integrations' with plotting libraries (Matplotlib, etc.)
and the universal `unwrap()` function to strip physical and computational metadata.
"""
from __future__ import annotations

from typing import Any, TYPE_CHECKING, overload, Mapping
import numpy as np

from .compat import HAS_NUMPY, _KeyT, Extractable, UnwrappedArray

if TYPE_CHECKING:
    from .base import BaseUnit


from collections.abc import Mapping
from typing import Any, TYPE_CHECKING, overload

from .compat import HAS_NUMPY, _KeyT, Extractable, UnwrappedArray

if TYPE_CHECKING:
    from .base import BaseUnit

@overload
def unwrap(obj: Mapping[_KeyT, Extractable]) -> dict[_KeyT, UnwrappedArray]: ...

@overload
def unwrap(obj: Extractable) -> UnwrappedArray: ...

@overload
def unwrap(obj1: Extractable, obj2: Extractable) -> tuple[UnwrappedArray, UnwrappedArray]: ...

@overload
def unwrap(obj1: Extractable, obj2: Extractable, obj3: Extractable) -> tuple[UnwrappedArray, UnwrappedArray, UnwrappedArray]: ...

@overload
def unwrap(*args: Extractable) -> tuple[UnwrappedArray, ...]: ...

def unwrap(*args: Extractable) -> Any:
    """
    Universally extracts numerical payloads (NumPy arrays or primitives) from any 
    Phaethon or PyTorch object, making them safe for visualization tools 
    like Matplotlib, Plotly, or PyVista.

    It safely detaches PyTorch computational graphs, unwraps BaseUnits, converts 
    Decimals, strips Pandas/Polars indices, and natively unpacks Phaethon Datasets/Series.

    Args:
        *args: One or more Phaethon BaseUnits, PTensors, PyTorch Tensors, 
               Pandas Series, Phaethon Datasets, Phaethon Series, or Mappings containing them.

    Returns:
        A single NumPy array, a tuple of arrays, or a dictionary of arrays.

    Examples:
            >>> # 1. Unwrapping a single PTensor or BaseUnit:
            >>> v_tensor = PTensor([10., 20.], unit=u.MeterPerSecond, requires_grad=True)
            >>> v_np = ptn.unwrap(v_tensor)
            >>> type(v_np)
            <class 'numpy.ndarray'>
        
            >>> # 2. Unwrapping multiple objects for X-Y plotting:
            >>> x_np, y_np = ptn.unwrap(time_ptensor, velocity_baseunit)
            >>> plt.plot(x_np, y_np)

            >>> # 3. Unwrapping a Phaethon Dataset (.astensor output):
            >>> dataset = MySchema.astensor(df)
            >>> numpy_dict = ptn.unwrap(dataset)
            >>> plt.scatter(numpy_dict['time'], numpy_dict['velocity'])

            >>> # 4. Unwrapping a single Phaethon Series:
            >>> raw_vel = ptn.unwrap(dataset['velocity'])
            
            >>> # 5. Mixing heterogeneous data types safely:
            >>> a, b, c = ptn.unwrap(u.Kilogram(10), pnn.PTensor([1, 2]), [3, 4, 5])
            # a -> 10.0 (float)
            # b -> array([1, 2])
            # c -> array([3, 4, 5])
    """
    def _extract_single(item: Any) -> UnwrappedArray:
        if item is None:
            return None
            
        if type(item).__name__ == "Series" and hasattr(item, "raw"):
            return item.raw
        
        mag = getattr(item, 'mag', item)
        
        if hasattr(mag, 'detach'):
            mag = mag.detach().cpu().numpy()
            
        elif hasattr(mag, 'quantize') and not isinstance(mag, type(item)):
            mag = float(mag)
            
        elif hasattr(mag, 'to_numpy') and not isinstance(mag, type(item)):
            mag = mag.to_numpy()
            
        elif isinstance(mag, (list, tuple)) and HAS_NUMPY:
            import numpy as np
            mag = np.asarray(mag)
            
        return mag

    if not args:
        return None

    if len(args) == 1 and isinstance(args[0], Mapping):
        return {k: _extract_single(v) for k, v in args[0].items()}

    extracted = [_extract_single(arg) for arg in args]
    return extracted[0] if len(extracted) == 1 else tuple(extracted)


def symtag(label: str | None, obj: Any, auto_unit: bool = True) -> str:
    """
    Generates a scientifically formatted axis label (e.g., "Velocity (m/s)").
    Intelligently extracts dimensions safely from PTensors, BaseUnits, or standard inputs.
    
    Args:
        label: The base text for the axis (e.g., 'Time'). If None, only the unit is returned.
        obj: The source object to extract the unit symbol from.
        auto_unit: If False, ignores the physical unit and returns the label as-is.

    Returns:
        A formatted string ready for `plt.xlabel()` or Plotly `xaxis_title`.

    Examples:
            >>> # 1. Standard Physics Labeling:
            >>> ptn.symtag("Velocity", PTensor([10], unit=u.MeterPerSecond))
            'Velocity (m/s)'

            >>> # 2. Ignoring Unit for Semantic/Dimensionless Tensors:
            >>> ptn.symtag("Status ID", torch.tensor([0, 1]))
            'Status ID'

            >>> # 3. Unit Only (No base label):
            >>> ptn.symtag(None, u.Kilogram(10))
            '(kg)'
    """
    if not auto_unit:
        return str(label) if label else ""
        
    sym = ""
    if hasattr(obj, 'unit'): 
        sym = getattr(obj.unit, 'symbol', '')
    elif hasattr(obj, 'symbol'): 
        sym = getattr(obj, 'symbol', '')
    elif hasattr(obj, 'dimension') and hasattr(obj.__class__, 'symbol'): 
        sym = getattr(obj.__class__, 'symbol', '')
        
    if not sym:
        return str(label) if label else ""
        
    return f"{label} ({sym})" if label else f"({sym})"
