from __future__ import annotations

import math
from decimal import Decimal, getcontext
from typing import Any, TYPE_CHECKING, overload

from .registry import ureg
from ..exceptions import DimensionMismatchError
from .axioms import _normalize_types
from .compat import _T_Unit, ContextDict, NumericLike, UnitLike

if TYPE_CHECKING:
    import numpy as np

try:
    import numpy as np
    HAS_NUMPY = True
except ImportError:
    HAS_NUMPY = False

def _combine_signatures(sig1: frozenset[Any], sig2: frozenset[Any], operation: str) -> frozenset[Any]:
    c1 = dict(sig1) if sig1 else {}
    c2 = dict(sig2) if sig2 else {}
    
    all_dims = set(c1.keys()).union(c2.keys())
    new_sig = {}
    
    for dim in all_dims:
        exp1 = c1.get(dim, 0)
        exp2 = c2.get(dim, 0)
        
        if operation == 'mul':
            new_exp = exp1 + exp2
        elif operation == 'div':
            new_exp = exp1 - exp2
        
        if new_exp != 0:
            new_sig[dim] = new_exp
            
    return frozenset(new_sig.items())

def _find_existing_class(signature: frozenset[Any], target_multiplier: float) -> type[BaseUnit] | None:
    resolved_dim = ureg().resolve_signature(signature)
    
    if resolved_dim == 'anonymous':
        return None
        
    if math.isclose(target_multiplier, 1.0, rel_tol=1e-9):
        try:
            base_cls = ureg().baseof(resolved_dim)
            if float(getattr(base_cls, 'base_offset', 0.0)) == 0.0:
                return base_cls
        except ValueError:
            pass
            
    candidates = ureg().unitsin(resolved_dim, ascls=True)
    valid_matches = []
    
    for cls in candidates:
        if math.isclose(float(getattr(cls, 'base_multiplier', 0)), target_multiplier, rel_tol=1e-9):
            if float(getattr(cls, 'base_offset', 0.0)) == 0.0:
                valid_matches.append(cls)
                
    if not valid_matches:
        return None
        
    return valid_matches[0]

class _PhaethonUnitMeta(type):
    """
    Metaclass that tracks dimensional signatures and dynamically generates 
    new derived unit classes during cross-unit algebra (e.g., u.Meter / u.Second).
    """
    def __new__(mcs, name: str, bases: tuple[type, ...], namespace: dict[str, Any]) -> _PhaethonUnitMeta:
        cls = super().__new__(mcs, name, bases, namespace)
        if '_signature' not in namespace:
            dim = getattr(cls, 'dimension', None)
            if dim and dim != 'anonymous':
                cls._signature = ureg().get_signature_for_dim(dim)
            else:
                cls._signature = frozenset()
        return cls

    def _create_derived_class(cls, new_name: str, new_sig: frozenset[Any], new_mult: float | Decimal, new_symbol: str) -> type[BaseUnit]:
        existing_cls = _find_existing_class(new_sig, float(new_mult))
        if existing_cls:
            return existing_cls

        resolved_dim = ureg().resolve_signature(new_sig)
        
        ddoc = (
            f"Dynamically synthesized Phaethon Unit.\n\n"
            f"Dimension: {resolved_dim}\n"
            f"Symbol: {new_symbol}\n"
            f"Base Multiplier: {new_mult}\n"
            f"Algebraic Origin: {new_name}"
        )

        attrs = {
            '_signature': new_sig,
            '__doc__': ddoc,
            'base_multiplier': float(new_mult),
            'base_offset': 0.0,
            'dimension': resolved_dim,
            'symbol': new_symbol,
            'is_anonymous': (resolved_dim == 'anonymous')
        }
        
        base_unit_cls = next((c for c in cls.__mro__ if c.__name__ == 'BaseUnit'), cls.__bases__[0])
        return type(new_name, (base_unit_cls,), attrs)

    @staticmethod
    def _get_dynamic_multiplier(cls_or_scalar: Any, context: dict[str, Any], is_array: bool) -> Any:
        if isinstance(cls_or_scalar, type) and hasattr(cls_or_scalar, '_to_base_value'):
            m1 = cls_or_scalar(1.0, context=context)._to_base_value()
            m0 = cls_or_scalar(0.0, context=context)._to_base_value()
            mult = m1 - m0
        else:
            mult = cls_or_scalar

        if is_array:
            return float(mult)
        return Decimal(str(mult)) if not isinstance(mult, Decimal) else mult
    
    def __mul__(cls, other: type[BaseUnit] | int | float | Decimal) -> type[BaseUnit]:
        """Synthesizes a new class by multiplying dimensions and dynamically evaluating base multipliers."""
        if isinstance(other, _PhaethonUnitMeta):
            new_sig = _combine_signatures(getattr(cls, '_signature', frozenset()), 
                                          getattr(other, '_signature', frozenset()), 'mul')
            new_mult = Decimal(str(cls.base_multiplier)) * Decimal(str(other.base_multiplier))
            new_name = f"Derived_{cls.__name__}_mul_{other.__name__}"
            new_symbol = f"{getattr(cls, 'symbol', '')}*{getattr(other, 'symbol', '')}"
            new_cls = cls._create_derived_class(new_name, new_sig, new_mult, new_symbol)
        elif isinstance(other, (int, float, Decimal)):
            new_sig = getattr(cls, '_signature', frozenset())
            new_mult = Decimal(str(cls.base_multiplier)) * Decimal(str(other))
            new_name = f"Derived_{cls.__name__}_mul_scalar"
            new_symbol = f"{other}*{getattr(cls, 'symbol', '')}"
            new_cls = cls._create_derived_class(new_name, new_sig, new_mult, new_symbol)
        else:
            return NotImplemented # type: ignore

        if new_cls.__name__.startswith('Derived_'):
            left_cls, right_cls = cls, other
            def new_to_base(self_obj: Any) -> Any:
                is_arr = HAS_NUMPY and isinstance(self_obj._value, (np.ndarray, np.generic))
                v1 = _PhaethonUnitMeta._get_dynamic_multiplier(left_cls, self_obj.context, is_arr)
                v2 = _PhaethonUnitMeta._get_dynamic_multiplier(right_cls, self_obj.context, is_arr)
                val = self_obj._value if is_arr else Decimal(str(self_obj._value)) if not isinstance(self_obj._value, Decimal) else self_obj._value
                return val * v1 * v2

            @classmethod
            def new_from_base(cls_obj: type, base_val: Any, context: dict[str, Any]) -> Any:
                is_arr = HAS_NUMPY and isinstance(base_val, (np.ndarray, np.generic))
                v1 = _PhaethonUnitMeta._get_dynamic_multiplier(left_cls, context, is_arr)
                v2 = _PhaethonUnitMeta._get_dynamic_multiplier(right_cls, context, is_arr)
                val = base_val if is_arr else Decimal(str(base_val)) if not isinstance(base_val, Decimal) else base_val
                return val / (v1 * v2)

            new_cls._to_base_value = new_to_base
            new_cls._from_base_value = new_from_base # type: ignore
        return new_cls

    def __rmul__(cls, other: type[BaseUnit] | int | float | Decimal) -> type[BaseUnit]:
        """Synthesizes a new class by multiplying dimensions and base multipliers (reverse)."""
        return _PhaethonUnitMeta.__mul__(cls, other)

    def __truediv__(cls, other: type[BaseUnit] | int | float | Decimal) -> type[BaseUnit]:
        """Synthesizes a new class by dividing dimensions and dynamically evaluating base multipliers."""
        if isinstance(other, _PhaethonUnitMeta):
            new_sig = _combine_signatures(getattr(cls, '_signature', frozenset()), 
                                          getattr(other, '_signature', frozenset()), 'div')
            if getattr(other, 'base_multiplier', 0) == 0:
                raise ZeroDivisionError()
            new_mult = Decimal(str(cls.base_multiplier)) / Decimal(str(other.base_multiplier))
            new_name = f"Derived_{cls.__name__}_div_{other.__name__}"
            new_symbol = f"{getattr(cls, 'symbol', '')}/{getattr(other, 'symbol', '')}"
            new_cls = cls._create_derived_class(new_name, new_sig, new_mult, new_symbol)
        elif isinstance(other, (int, float, Decimal)):
            if other == 0: raise ZeroDivisionError()
            new_sig = getattr(cls, '_signature', frozenset())
            new_mult = Decimal(str(cls.base_multiplier)) / Decimal(str(other))
            new_name = f"Derived_{cls.__name__}_div_scalar"
            new_symbol = f"{getattr(cls, 'symbol', '')}/{other}"
            new_cls = cls._create_derived_class(new_name, new_sig, new_mult, new_symbol)
        else:
            return NotImplemented

        if new_cls.__name__.startswith('Derived_'):
            left_cls, right_cls = cls, other
            def new_to_base(self_obj: Any) -> Any:
                is_arr = HAS_NUMPY and isinstance(self_obj._value, (np.ndarray, np.generic))
                v1 = _PhaethonUnitMeta._get_dynamic_multiplier(left_cls, self_obj.context, is_arr)
                v2 = _PhaethonUnitMeta._get_dynamic_multiplier(right_cls, self_obj.context, is_arr)
                val = self_obj._value if is_arr else Decimal(str(self_obj._value)) if not isinstance(self_obj._value, Decimal) else self_obj._value
                return (val * v1) / v2

            @classmethod
            def new_from_base(cls_obj: type, base_val: Any, context: dict[str, Any]) -> Any:
                is_arr = HAS_NUMPY and isinstance(base_val, (np.ndarray, np.generic))
                v1 = _PhaethonUnitMeta._get_dynamic_multiplier(left_cls, context, is_arr)
                v2 = _PhaethonUnitMeta._get_dynamic_multiplier(right_cls, context, is_arr)
                val = base_val if is_arr else Decimal(str(base_val)) if not isinstance(base_val, Decimal) else base_val
                return (val * v2) / v1

            new_cls._to_base_value = new_to_base
            new_cls._from_base_value = new_from_base # type: ignore
        return new_cls

    def __pow__(cls, power: int | float) -> type[BaseUnit]:
        """Synthesizes a new class by exponentiating dimensions and dynamically evaluating multipliers."""
        if not isinstance(power, (int, float)): return NotImplemented # type: ignore
        current_sig = dict(getattr(cls, '_signature', frozenset()))
        new_sig = frozenset({dim: exp * power for dim, exp in current_sig.items()}.items())
        new_mult = float(cls.base_multiplier) ** float(power)
        
        sym = getattr(cls, 'symbol', '')
        new_symbol = f"({sym})^{power}" if '/' in sym or '*' in sym else f"{sym}^{power}"
        new_name = f"Derived_{cls.__name__}_pow_{power}"
        new_cls = cls._create_derived_class(new_name, new_sig, new_mult, new_symbol)
        
        if new_cls.__name__.startswith('Derived_'):
            left_cls = cls
            def new_to_base(self_obj: Any) -> Any:
                is_arr = HAS_NUMPY and isinstance(self_obj._value, (np.ndarray, np.generic))
                v1 = _PhaethonUnitMeta._get_dynamic_multiplier(left_cls, self_obj.context, is_arr)
                val = self_obj._value if is_arr else Decimal(str(self_obj._value)) if not isinstance(self_obj._value, Decimal) else self_obj._value
                pow_val = float(power) if is_arr else Decimal(str(power))
                return val * (v1 ** pow_val)

            @classmethod
            def new_from_base(cls_obj: type, base_val: Any, context: dict[str, Any]) -> Any:
                is_arr = HAS_NUMPY and isinstance(base_val, (np.ndarray, np.generic))
                v1 = _PhaethonUnitMeta._get_dynamic_multiplier(left_cls, context, is_arr)
                val = base_val if is_arr else Decimal(str(base_val)) if not isinstance(base_val, Decimal) else base_val
                pow_val = float(power) if is_arr else Decimal(str(power))
                return val / (v1 ** pow_val)

            new_cls._to_base_value = new_to_base
            new_cls._from_base_value = new_from_base # type: ignore
        return new_cls
    
    def __matmul__(cls, other: type[BaseUnit]) -> type[BaseUnit]:
        """Permits matrix multiplication operator (@) for dimensional synthesis."""
        return cls.__mul__(other)

    def __rmatmul__(cls, other: type[BaseUnit]) -> type[BaseUnit]:
        """Reverse matrix multiplication synthesis."""
        return cls.__mul__(other)
    
    def __lt__(cls, other: Any) -> bool:
        if not isinstance(other, type) or not hasattr(other, 'base_multiplier'):
            return NotImplemented
        if getattr(cls, 'dimension', None) != getattr(other, 'dimension', None):
            raise DimensionMismatchError(
                str(getattr(cls, 'dimension', None)), 
                str(getattr(other, 'dimension', None)), 
                "Unit Class Comparison (<)"
            )
        return float(cls.base_multiplier) < float(other.base_multiplier)

    def __le__(cls, other: Any) -> bool:
        if not isinstance(other, type) or not hasattr(other, 'base_multiplier'):
            return NotImplemented
        if getattr(cls, 'dimension', None) != getattr(other, 'dimension', None):
            raise DimensionMismatchError(
                str(getattr(cls, 'dimension', None)), 
                str(getattr(other, 'dimension', None)), 
                "Class Comparison (<=)"
            )
        return float(cls.base_multiplier) <= float(other.base_multiplier)

    def __gt__(cls, other: Any) -> bool:
        if not isinstance(other, type) or not hasattr(other, 'base_multiplier'):
            return NotImplemented
        if getattr(cls, 'dimension', None) != getattr(other, 'dimension', None):
            raise DimensionMismatchError(
                str(getattr(cls, 'dimension', None)), 
                str(getattr(other, 'dimension', None)), 
                "Class Comparison (>)"
            )
        return float(cls.base_multiplier) > float(other.base_multiplier)

    def __ge__(cls, other: Any) -> bool:
        if not isinstance(other, type) or not hasattr(other, 'base_multiplier'):
            return NotImplemented
        if getattr(cls, 'dimension', None) != getattr(other, 'dimension', None):
            raise DimensionMismatchError(
                str(getattr(cls, 'dimension', None)), 
                str(getattr(other, 'dimension', None)), 
                "Class Comparison (>=)"
            )
        return float(cls.base_multiplier) >= float(other.base_multiplier)

class BaseUnit(metaclass=_PhaethonUnitMeta):
    """
    The foundational core class for all physical and digital units in Phaethon.
    Provides the standard interface for dimensional algebra, scalar conversions,
    NumPy vectorization, and fluent formatting.
    """
    dimension: str | None = None
    symbol: str | None = None
    aliases: list[str] | None = None
    base_multiplier: float | Decimal = 1.0
    base_offset: float | Decimal = 0.0
    is_anonymous: bool = False

    def __init_subclass__(cls, **kwargs: Any) -> None:
        """
        Automatically triggered when a subclass of BaseUnit is created.
        Injects the new class directly into the global UnitRegistry.
        """
        super().__init_subclass__(**kwargs)
        if not getattr(cls, 'is_anonymous', False) and getattr(cls, 'dimension', 'anonymous') != 'anonymous':
            ureg()._register(cls)
            
            sig = getattr(cls, '_signature', None)
            if sig:
                ureg().inject_dna(sig, cls.dimension)

    def __init__(self, value: NumericLike, context: ContextDict | None = None) -> None:
        if HAS_NUMPY and isinstance(value, (np.ndarray, np.generic)):
            self._value = value
        elif HAS_NUMPY and isinstance(value, (list, tuple)):
            self._value = np.array(value, dtype=float)
        elif isinstance(value, Decimal):
            self._value = value
        elif isinstance(value, (int, float, str)):
            self._value = float(value)
        else:
            raise TypeError(f"Value must be numeric or array, got {type(value).__name__}")
            
        self.context = context or {}

    # =========================================================================
    # PUBLIC PROPERTIES (THE DX INTERFACE)
    # =========================================================================
    @property
    def exact(self) -> float | Decimal | np.ndarray:
        """Returns the exact raw magnitude, preserving high-precision Decimals if used."""
        return self._value

    @property
    def mag(self) -> float | np.ndarray:
        """Returns the magnitude safely downcasted to a standard Python float or NumPy array."""
        if HAS_NUMPY and isinstance(self._value, (np.ndarray, np.generic)):
            return self._value
            
        if isinstance(self._value, Decimal):
            return float(self._value)
            
        return self._value

    @property
    def shape(self) -> tuple[int, ...]:
        """Returns the shape of the underlying array."""
        if HAS_NUMPY and isinstance(self._value, (np.ndarray, np.generic)):
            return self._value.shape # type: ignore
        return ()

    @property
    def ndim(self) -> int:
        """Returns the number of dimensions of the underlying array."""
        if HAS_NUMPY and isinstance(self._value, (np.ndarray, np.generic)):
            return self._value.ndim # type: ignore
        return 0

    @property
    def T(self) -> BaseUnit:
        """Returns the transposed physical array."""
        if HAS_NUMPY and isinstance(self._value, (np.ndarray, np.generic)):
            return self.__class__(self._value.T, context=self.context)
        return self

    def sum(self, axis: int | tuple[int, ...] | None = None, keepdims: bool = False, **kwargs: Any) -> BaseUnit:
        """Sums array elements over a given axis, preserving physical dimensions."""
        if HAS_NUMPY and isinstance(self._value, (np.ndarray, np.generic)):
            new_val = self._value.sum(axis=axis, keepdims=keepdims, **kwargs)
            return self.__class__(new_val, context=self.context)
        return self

    def mean(self, axis: int | tuple[int, ...] | None = None, keepdims: bool = False, **kwargs: Any) -> BaseUnit:
        """Computes the arithmetic mean, preserving physical dimensions."""
        if HAS_NUMPY and isinstance(self._value, (np.ndarray, np.generic)):
            new_val = self._value.mean(axis=axis, keepdims=keepdims, **kwargs)
            return self.__class__(new_val, context=self.context)
        return self

    def max(self, axis: int | tuple[int, ...] | None = None, keepdims: bool = False, **kwargs: Any) -> BaseUnit:
        """Returns the maximum of an array or maximum along an axis."""
        if HAS_NUMPY and isinstance(self._value, (np.ndarray, np.generic)):
            new_val = self._value.max(axis=axis, keepdims=keepdims, **kwargs)
            return self.__class__(new_val, context=self.context)
        return self

    def min(self, axis: int | tuple[int, ...] | None = None, keepdims: bool = False, **kwargs: Any) -> BaseUnit:
        """Returns the minimum of an array or minimum along an axis."""
        if HAS_NUMPY and isinstance(self._value, (np.ndarray, np.generic)):
            new_val = self._value.min(axis=axis, keepdims=keepdims, **kwargs)
            return self.__class__(new_val, context=self.context)
        return self

    def reshape(self, shape: tuple[int, ...] | int, *args: Any, order: str = 'C') -> BaseUnit:
        """Gives a new shape to the physical array without changing its data."""
        if HAS_NUMPY and isinstance(self._value, (np.ndarray, np.generic)):
            new_val = self._value.reshape(shape, *args, order=order)
            return self.__class__(new_val, context=self.context)
        return self

    def flatten(self, order: str = 'C') -> BaseUnit:
        """Return a copy of the array collapsed into one dimension."""
        if HAS_NUMPY and isinstance(self._value, (np.ndarray, np.generic)):
            new_val = self._value.flatten(order=order)
            return self.__class__(new_val, context=self.context)
        return self
    
    # =========================================================================
    # INTERNAL CORE LOGIC
    # =========================================================================
    def _to_base_value(self) -> float | Decimal | Any:
        from .config import using
        
        with using(context=self.context):
            if isinstance(self._value, Decimal):
                val_with_offset = self._value + Decimal(str(self.base_offset))
                return val_with_offset * Decimal(str(self.base_multiplier))
                
            val_with_offset = self._value + float(self.base_offset)
            return val_with_offset * float(self.base_multiplier)

    @classmethod
    def _from_base_value(cls, base_val: float | Decimal | Any, context: dict[str, Any]) -> float | Decimal | Any:
        from .config import using
        
        with using(context=context):
            if isinstance(base_val, Decimal):
                val = base_val / Decimal(str(cls.base_multiplier))
                return val - Decimal(str(cls.base_offset))
                
            val = base_val / float(cls.base_multiplier)
            return val - float(cls.base_offset)

    _ALLOWED_UFUNCS = {
        'add', 'subtract', 'maximum', 'minimum', 'fmax', 'fmin', 
        'absolute', 'negative', 'positive', 'rint'
    }
    
    _ALLOWED_FUNCTIONS = {
        'sum', 'max', 'min', 'mean', 'median', 'std', 'round', 'ptp'
    }

    _ROUTED_UFUNCS = {
        'multiply': ('__mul__', '__rmul__'),
        'divide': ('__truediv__', '__rtruediv__'),
        'true_divide': ('__truediv__', '__rtruediv__'),
        'floor_divide': ('__floordiv__', '__rfloordiv__'),
        'matmul': ('__matmul__', '__rmatmul__'),
        'power': ('__pow__', None),
        'remainder': ('__mod__', '__rmod__'),
        'mod': ('__mod__', '__rmod__')
    }

    __array_priority__ = 10000

    def __array_ufunc__(self, ufunc: Any, method: str, *inputs: Any, **kwargs: Any) -> BaseUnit | Any:
        if ufunc.__name__ in self._ROUTED_UFUNCS:
            if method != '__call__':
                return NotImplemented
                
            dunder, rdunder = self._ROUTED_UFUNCS[ufunc.__name__]
            
            if len(inputs) == 2:
                if inputs[0] is self:
                    return getattr(self, dunder)(inputs[1])
                elif inputs[1] is self and rdunder:
                    return getattr(self, rdunder)(inputs[0])
            return NotImplemented

        if ufunc.__name__ not in self._ALLOWED_UFUNCS:
            raise TypeError(
                f"Phaethon Dimensional Guard: Operation 'np.{ufunc.__name__}' is "
                f"blocked because it mutates physical dimensions in an unhandled way."
            )

        raw_inputs = []
        for inp in inputs:
            if isinstance(inp, BaseUnit):
                if self.dimension != getattr(inp, 'dimension', None):
                    raise DimensionMismatchError(str(self.dimension), str(getattr(inp, 'dimension', None)), f"NumPy ufunc {ufunc.__name__}")
                raw_inputs.append(inp._to_base_value())
            else:
                raw_inputs.append(inp)

        raw_result = getattr(ufunc, method)(*raw_inputs, **kwargs)
        final_value = self.__class__._from_base_value(raw_result, self.context)
        return self.__class__(final_value, context=self.context)
    
    def __array_function__(self, func: Any, types: Any, args: Any, kwargs: Any) -> BaseUnit:
        if func.__name__ not in self._ALLOWED_FUNCTIONS:
            raise TypeError(
                f"Phaethon Dimensional Guard: Function 'np.{func.__name__}' is "
                f"blocked to preserve dimensional integrity."
            )

        def _extract_raw(obj: Any) -> Any:
            if isinstance(obj, BaseUnit):
                return obj._to_base_value()
            if isinstance(obj, (list, tuple)):
                return [_extract_raw(o) for o in obj]
            return obj

        raw_args = tuple(_extract_raw(arg) for arg in args)
        raw_result = func(*raw_args, **kwargs)

        final_value = self.__class__._from_base_value(raw_result, self.context)
        return self.__class__(final_value, context=self.context)
    
    def __getattr__(self, name: str) -> Any:
        if name.startswith('_'):
            raise AttributeError(f"'{self.__class__.__name__}' object has no attribute '{name}'")
            
        if HAS_NUMPY and isinstance(self._value, (np.ndarray, np.generic)):
            if hasattr(self._value, name):
                attr = getattr(self._value, name)
                
                if callable(attr):
                    import functools
                    @functools.wraps(attr)
                    def wrapper(*args: Any, **kwargs: Any) -> Any:
                        if hasattr(np, name):
                            np_func = getattr(np, name)
                            return np_func(self, *args, **kwargs)
                        return attr(*args, **kwargs)
                    return wrapper
                
                return attr
                
        raise AttributeError(f"'{self.__class__.__name__}' object has no attribute '{name}'")

    def __getitem__(self, key: Any) -> Any:
        if HAS_NUMPY and isinstance(self._value, (np.ndarray, np.generic)):
            new_val = self._value[key]
            return self.__class__(new_val, context=self.context)
            
        if isinstance(self._value, (list, tuple)):
            new_val = self._value[key]
            return self.__class__(new_val, context=self.context)
            
        raise TypeError(f"'{self.__class__.__name__}' object is not subscriptable")
    
    def __str__(self) -> str:
        if HAS_NUMPY and isinstance(self._value, np.ndarray):
            return f"<{self.__class__.__name__} Array: {self.format(tag=False)}>"
        elif (HAS_NUMPY and isinstance(self._value, np.generic)) or isinstance(self._value, float):
            return self.format(tag=True)
            
        return self.format(tag=True)

    def __repr__(self) -> str:
        if HAS_NUMPY and isinstance(self._value, np.ndarray):
            return f"<{self.__class__.__name__} Array of shape {self._value.shape}>"
        return f"<{self.__class__.__name__}: {self._value} {self.symbol}>"

    def __float__(self) -> float:
        return float(self._value)

    def __int__(self) -> int:
        return int(self._value)

    @overload
    def to(self, unit: type[_T_Unit], context: ContextDict | None = ...) -> _T_Unit: ...
    
    @overload
    def to(self, unit: str, context: ContextDict | None = ...) -> BaseUnit: ...

    def to(self, unit: UnitLike | str, context: ContextDict | None = None) -> _T_Unit | BaseUnit:
        """
        Transforms the current unit instance into a new target unit within the same dimension.
        
        This method bridges identical dimensions (e.g., length to length, currency to currency)
        and allows on-the-fly context injection for volatile environments like financial markets.
        
        Args:
            unit: The target physical class (e.g., u.Kilometer) or registered string alias (e.g., 'km').
            context: Optional dynamic runtime context (e.g., real-time FX rates) applied specifically 
                     for this conversion operation.

        Returns:
            A new instantiated BaseUnit representing the converted magnitude.
            
        Raises:
            TypeError: If the provided target unit is unrecognizable.
            DimensionMismatchError: If attempting to convert across incompatible dimensions.
        """
        if isinstance(unit, str):
            try:
                TargetClass = ureg().get_unit_class(unit, expected_dim=self.dimension)
            except Exception:
                raise TypeError(
                    f"Invalid target in .to() method: '{unit}'. "
                    f"Please provide a valid BaseUnit class or a recognized string alias for dimension '{self.dimension}'."
                ) from None
        else:
            TargetClass = unit

        if not (isinstance(TargetClass, type) and issubclass(TargetClass, BaseUnit)):
            raise TypeError(
                f"The .to() method expects a BaseUnit class or a valid string alias, "
                f"but got {type(unit).__name__} instead."
            )
        if self.dimension != getattr(TargetClass, "dimension", None):
            raise DimensionMismatchError(str(self.dimension), str(getattr(TargetClass, 'dimension', None)), "Conversion")
            
        merged_context = {**self.context}
        if context:
            merged_context.update(context)

        original_context = self.context
        self.context = merged_context
        try:
            base_val = self._to_base_value()
        finally:
            self.context = original_context
            
        new_val = TargetClass._from_base_value(base_val, merged_context)
        return TargetClass(new_val, context=merged_context)

    def format(
        self,
        prec: int = 4,
        sigfigs: int | None = None,
        scinote: bool = False,
        delim: bool | str = False,
        tag: bool = True
    ) -> str:
        """Applies precise structural and numeric formatting to the magnitude."""
        val = self._value
        
        if HAS_NUMPY and isinstance(val, (np.ndarray, np.generic)):
            def format_elem(x: Any) -> str:
                if scinote:
                    digits = sigfigs - 1 if sigfigs is not None else prec
                    return f"{x:.{digits}E}"
                
                s = f"{float(x):.{prec}f}"
                if '.' in s:
                    s = s.rstrip('0').rstrip('.')
                    if s.endswith('-'): s = s + "0"
                    if not s: s = "0"
                
                if delim:
                    separator = "," if delim is True or str(delim).lower() == "default" else str(delim)
                    parts = s.split('.')
                    parts[0] = f"{int(parts[0]):,}".replace(",", separator)
                    s = '.'.join(parts) if len(parts) > 1 else parts[0]
                    
                return s

            val_str = np.array2string(
                val, 
                formatter={'float_kind': format_elem, 'int': format_elem},
                separator=', ',
                suppress_small=not scinote 
            )
            
            if tag:
                return f"{val_str} {self.symbol}"
            return val_str

        if sigfigs is not None:
            if val == 0:
                val = Decimal(0)
            else:
                shift = sigfigs - val.adjusted() - 1
                quantizer = Decimal('1e{}'.format(-shift))
                val = val.quantize(quantizer, rounding=getcontext().rounding)

        if scinote:
            digits = sigfigs - 1 if sigfigs is not None else prec
            val_str = f"{val:.{digits}E}"
        else:
            if sigfigs:
                decimal_places = max(sigfigs - (val.adjusted() + 1), 0)
                val_str = f"{val:.{decimal_places}f}"
            else:
                try:
                    quant = Decimal(f"1e-{prec}")
                    val = val.quantize(quant, rounding=getcontext().rounding)
                except Exception:
                    pass
                val_str = format(val, 'f')

        if not scinote and '.' in val_str:
            val_str = val_str.rstrip('0')
            if val_str.endswith('.'):
                val_str += '0'

        if delim:
            separator = "," if delim is True or str(delim).lower() == "default" else str(delim)
            if not scinote:
                parts = val_str.split('.')
                parts[0] = f"{int(parts[0]):,}".replace(",", separator)
                val_str = '.'.join(parts) if len(parts) > 1 else parts[0]

        if tag:
            return f"{val_str} {self.symbol}"
        return val_str

    def __eq__(self, other: object) -> bool:
        """Evaluates equality after cross-unit normalization."""
        if not isinstance(other, BaseUnit):
            return NotImplemented
        if self.dimension != getattr(other, "dimension", None):
            raise DimensionMismatchError(str(self.dimension), str(getattr(other, 'dimension', None)), "Equality (==)")
            
        v1, v2 = self._to_base_value(), other._to_base_value()
        v1, v2 = _normalize_types(v1, v2)
            
        return v1 == v2

    def __lt__(self, other: BaseUnit) -> bool:
        """Evaluates less-than after cross-unit normalization."""
        if not isinstance(other, BaseUnit):
            return NotImplemented
        if self.dimension != getattr(other, "dimension", None):
            raise DimensionMismatchError(str(self.dimension), str(getattr(other, 'dimension', None)), "Less-than (<)")
            
        v1, v2 = self._to_base_value(), other._to_base_value()
        v1, v2 = _normalize_types(v1, v2)
            
        return v1 < v2

    def __le__(self, other: BaseUnit) -> bool:
        """Evaluates less-than-or-equal after cross-unit normalization."""
        if not isinstance(other, BaseUnit):
            return NotImplemented
        if self.dimension != getattr(other, "dimension", None):
            raise DimensionMismatchError(str(self.dimension), str(getattr(other, 'dimension', None)), "Less-than-or-equal (<=)")
            
        v1, v2 = self._to_base_value(), other._to_base_value()
        v1, v2 = _normalize_types(v1, v2)
            
        return v1 <= v2

    def __ge__(self, other: BaseUnit) -> bool:
        """Evaluates greater-than-or-equal after cross-unit normalization."""
        if not isinstance(other, BaseUnit):
            return NotImplemented
        if self.dimension != getattr(other, "dimension", None):
            raise DimensionMismatchError(str(self.dimension), str(getattr(other, 'dimension', None)), "Greater-than-or-equal (>=)")
            
        v1, v2 = self._to_base_value(), other._to_base_value()
        v1, v2 = _normalize_types(v1, v2)
            
        return v1 >= v2

    def __gt__(self, other: BaseUnit) -> bool:
        """Evaluates greater-than after cross-unit normalization."""
        if not isinstance(other, BaseUnit):
            return NotImplemented
        if self.dimension != getattr(other, "dimension", None):
            raise DimensionMismatchError(str(self.dimension), str(getattr(other, 'dimension', None)), "Greater-than (>)")
            
        v1, v2 = self._to_base_value(), other._to_base_value()
        v1, v2 = _normalize_types(v1, v2)
            
        return v1 > v2
    
    def __ne__(self, other: object) -> bool:
        """Evaluates not-equal after cross-unit normalization."""
        if not isinstance(other, BaseUnit):
            return NotImplemented
        if self.dimension != getattr(other, "dimension", None):
            raise DimensionMismatchError(str(self.dimension), str(getattr(other, 'dimension', None)), "Not-Equal (!=)")
            
        v1, v2 = self._to_base_value(), other._to_base_value()
        v1, v2 = _normalize_types(v1, v2)
            
        return v1 != v2
    
    def __add__(self, other: BaseUnit) -> BaseUnit | Any:
        """Adds another unit of the same dimension, returning the caller's unit."""
        if not isinstance(other, BaseUnit):
            return NotImplemented
        if self.dimension != getattr(other, "dimension", None):
            raise DimensionMismatchError(str(self.dimension), str(getattr(other, 'dimension', None)), "Addition (+)")
        
        v1, v2 = self._to_base_value(), other._to_base_value()
        v1, v2 = _normalize_types(v1, v2)
        
        total_base = v1 + v2
        merged_context = {**other.context, **self.context}
        final_value = self.__class__._from_base_value(total_base, merged_context)
        return self.__class__(final_value, context=merged_context)

    def __sub__(self, other: BaseUnit) -> BaseUnit | Any:
        """Subtracts another unit of the same dimension, returning the caller's unit."""
        if not isinstance(other, BaseUnit):
            return NotImplemented
        if self.dimension != getattr(other, "dimension", None):
            raise DimensionMismatchError(str(self.dimension), str(getattr(other, 'dimension', None)), "Subtraction (-)")
        
        v1, v2 = self._to_base_value(), other._to_base_value()
        v1, v2 = _normalize_types(v1, v2)
            
        total_base = v1 - v2
        merged_context = {**other.context, **self.context}
        final_value = self.__class__._from_base_value(total_base, merged_context)
        return self.__class__(final_value, context=merged_context)
    
    def __mul__(self, other: NumericLike | BaseUnit) -> BaseUnit | Any:
        """Permits multiplication of a unit by a scalar, array, or another unit."""
        if isinstance(other, (int, float, Decimal)) or (HAS_NUMPY and isinstance(other, (np.ndarray, np.generic))):
            v1, v2 = _normalize_types(self._value, other)
            new_val = v1 * v2
            return self.__class__(new_val, context=self.context)
        
        if isinstance(other, BaseUnit):
            ResultClass = self.__class__ * other.__class__
            merged_context = {**self.context, **other.context}
            
            if getattr(ResultClass, 'dimension', None) == 'dimensionless':
                v1, v2 = self._to_base_value(), other._to_base_value()
                v1, v2 = _normalize_types(v1, v2)
                return BaseUnit(v1 * v2, context=merged_context)
                
            v1, v2 = _normalize_types(self._value, other._value)
            new_val = v1 * v2
            return ResultClass(new_val, context=merged_context)
            
        return NotImplemented

    def __rmul__(self, other: NumericLike | BaseUnit) -> BaseUnit | Any:
        """Permits reverse scalar multiplication."""
        return self.__mul__(other)

    def __matmul__(self, other: NumericLike | BaseUnit) -> BaseUnit | Any:
        """Matrix multiplication (Dot Product). Synthesizes new dimensions."""
        if not HAS_NUMPY:
            raise TypeError("Matrix multiplication (@) requires NumPy.")
            
        if isinstance(other, (np.ndarray, np.generic)):
            new_val = np.matmul(self._value, other)
            return self.__class__(new_val, context=self.context)
            
        if isinstance(other, BaseUnit):
            ResultClass = self.__class__ * other.__class__
            v1, v2 = _normalize_types(self._value, other._value)
            new_val = np.matmul(v1, v2)
            merged_context = {**self.context, **other.context}
            return ResultClass(new_val, context=merged_context)
            
        return NotImplemented

    def __rmatmul__(self, other: NumericLike | BaseUnit) -> BaseUnit | Any:
        """Reverse matrix multiplication."""
        if not HAS_NUMPY:
            raise TypeError("Matrix multiplication (@) requires NumPy.")
            
        if isinstance(other, (np.ndarray, np.generic)):
            new_val = np.matmul(other, self._value)
            return self.__class__(new_val, context=self.context)
            
        return NotImplemented

    def __neg__(self: _T_Unit) -> _T_Unit:
        """Reverses the direction/polarity of a physical vector (e.g., -10 Volt)."""
        return self.__class__(-self._value, context=self.context)

    def __pos__(self: _T_Unit) -> _T_Unit:
        """Unary plus operator."""
        return self.__class__(+self._value, context=self.context)

    def __abs__(self: _T_Unit) -> _T_Unit:
        """Returns the absolute magnitude of a physical vector."""
        if HAS_NUMPY and isinstance(self._value, (np.ndarray, np.generic)):
            return self.__class__(np.abs(self._value), context=self.context)
        return self.__class__(abs(self._value), context=self.context)

    def __round__(self: _T_Unit, ndigits: int | None = None) -> _T_Unit:
        """Rounds the physical magnitude while retaining dimensions."""
        if HAS_NUMPY and isinstance(self._value, (np.ndarray, np.generic)):
            return self.__class__(np.round(self._value, ndigits), context=self.context)
        return self.__class__(round(self._value, ndigits), context=self.context)

    def __floordiv__(self, other: NumericLike | BaseUnit) -> BaseUnit | Any:
        """Floor division for discrete physical quantization."""
        if isinstance(other, (int, float, Decimal)) or (HAS_NUMPY and isinstance(other, (np.ndarray, np.generic))):
            v1, v2 = _normalize_types(self._value, other)
            new_val = v1 // v2
            return self.__class__(new_val, context=self.context)
            
        if isinstance(other, BaseUnit):
            if self.dimension != getattr(other, "dimension", None):
                raise DimensionMismatchError(str(self.dimension), str(getattr(other, 'dimension', None)), "Floor Division (//)")
            
            v1, v2 = self._to_base_value(), other._to_base_value()
            v1, v2 = _normalize_types(v1, v2)
            total_base = v1 // v2
            merged_context = {**self.context, **other.context}
            
            return BaseUnit(total_base, context=merged_context)
            
        return NotImplemented

    def __mod__(self, other: NumericLike | BaseUnit) -> BaseUnit | Any:
        """
        Modulo operator. Essential for phase, angles, and time loops.
        Unit % Scalar = Unit.
        Unit % Unit (same dimension) = Unit.
        """
        if isinstance(other, (int, float, Decimal)) or (HAS_NUMPY and isinstance(other, (np.ndarray, np.generic))):
            v1, v2 = _normalize_types(self._value, other)
            new_val = v1 % v2
            return self.__class__(new_val, context=self.context)
            
        if isinstance(other, BaseUnit):
            if self.dimension != getattr(other, "dimension", None):
                raise DimensionMismatchError(str(self.dimension), str(getattr(other, 'dimension', None)), "Modulo (%)")
            
            v1, v2 = self._to_base_value(), other._to_base_value()
            v1, v2 = _normalize_types(v1, v2)
            
            total_base = v1 % v2
            merged_context = {**other.context, **self.context}
            final_value = self.__class__._from_base_value(total_base, merged_context)
            return self.__class__(final_value, context=merged_context)
            
        return NotImplemented
    
    def __truediv__(self, other: NumericLike | BaseUnit) -> BaseUnit | Any:
        """Permits division of a unit by a scalar, array, or another unit."""
        if isinstance(other, (int, float, Decimal)) or (HAS_NUMPY and isinstance(other, (np.ndarray, np.generic))):
            v1, v2 = _normalize_types(self._value, other)
            new_val = v1 / v2
            return self.__class__(new_val, context=self.context)
            
        if isinstance(other, BaseUnit):
            ResultClass = self.__class__ / other.__class__
            merged_context = {**self.context, **other.context}
            
            if getattr(ResultClass, 'dimension', None) == 'dimensionless':
                v1, v2 = self._to_base_value(), other._to_base_value()
                v1, v2 = _normalize_types(v1, v2)
                return BaseUnit(v1 / v2, context=merged_context)
                
            v1, v2 = _normalize_types(self._value, other._value)
            new_val = v1 / v2
            return ResultClass(new_val, context=merged_context)
            
        return NotImplemented
    
    def __pow__(self, power: int | float) -> BaseUnit | Any:
        """Permits exponentiation of a unit instance."""
        if isinstance(power, (int, float)):
            ResultClass = self.__class__ ** power
            new_val = self._value ** power
            return ResultClass(new_val, context=self.context)
        return NotImplemented

    def __array__(self, dtype: Any = None) -> Any:
        if HAS_NUMPY:
            return np.asarray(self._value, dtype=dtype)
        return np.array([self._value], dtype=dtype)