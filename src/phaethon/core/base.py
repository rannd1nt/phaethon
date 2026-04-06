from __future__ import annotations

import math
import threading
import functools
from typing import Any, TYPE_CHECKING, overload

from .registry import ureg
from .config import get_config, using
from ..exceptions import DimensionMismatchError, PhysicalAlgebraError
from .compat import _UnitT, ContextDict, NumericLike, UnitLike

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
        
    atol = get_config("atol")
    rtol = get_config("rtol")
        
    if math.isclose(target_multiplier, 1.0, rel_tol=rtol, abs_tol=0.0):
        try:
            base_cls = ureg().baseof(resolved_dim)
            if math.isclose(float(getattr(base_cls, 'base_offset', 0.0)), 0.0, rel_tol=rtol, abs_tol=atol):
                return base_cls
        except ValueError:
            pass
            
    candidates = ureg().unitsin(resolved_dim, ascls=True)
    valid_matches = []
    
    for cls in candidates:
        cls_mult = float(getattr(cls, 'base_multiplier', 0.0))
        cls_offset = float(getattr(cls, 'base_offset', 0.0))
        
        if math.isclose(cls_mult, target_multiplier, rel_tol=rtol, abs_tol=0.0):
            if math.isclose(cls_offset, 0.0, rel_tol=rtol, abs_tol=atol):
                valid_matches.append(cls)
                
    if not valid_matches:
        return None
    
    valid_matches.sort(key=lambda c: (c.__name__.startswith('Derived_'), len(c.__name__)))
    return valid_matches[0]

def _compact_name(op: str, name1: str, name2: str) -> str:
    n1 = name1.replace('Derived_', '')
    n2 = name2.replace('Derived_', '')
    res = f"Derived_{n1}_{op}_{n2}"
    if len(res) > 40:
        return f"Derived_{abs(hash(res)):x}"
    return res

def _fmtdim(u_cls: Any) -> str:
    if u_cls is None: 
        return "unknown"
    
    dim = getattr(u_cls, 'dimension', 'unknown')
    if dim == 'anonymous':
        if hasattr(u_cls, '_get_unit_string'):
            sym = u_cls._get_unit_string()
        else:
            sym = getattr(u_cls, 'symbol', '???')
        return f"Unregistered DNA [{sym}]"
    
    sym = getattr(u_cls, 'symbol', '')
    sym_str = f" [{sym}]" if sym else ""
    return f"{dim}{sym_str}"

class _PhaethonUnitMeta(type):
    _algebra_lock = threading.RLock()
    
    def __new__(mcs, name: str, bases: tuple[type, ...], namespace: dict[str, Any]) -> _PhaethonUnitMeta:
        cls = super().__new__(mcs, name, bases, namespace)
        if '_signature' not in namespace:
            dim = getattr(cls, 'dimension', None)
            if dim and dim != 'anonymous':
                cls._signature = ureg().get_signature_for_dim(dim)
            else:
                cls._signature = frozenset()
        return cls

    def _create_derived_class(cls, new_name: str, new_sig: frozenset[Any], new_mult: float, new_symbol: str) -> type[BaseUnit]:
        with _PhaethonUnitMeta._algebra_lock:
            existing_cls = _find_existing_class(new_sig, new_mult)
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
                'base_multiplier': new_mult,
                'base_offset': 0.0,
                'dimension': resolved_dim,
                'symbol': new_symbol,
                'is_anonymous': (resolved_dim == 'anonymous')
            }
            
            base_unit_cls = next((c for c in cls.__mro__ if c.__name__ == 'BaseUnit'), cls.__bases__[0])
            return type(new_name, (base_unit_cls,), attrs)

    @staticmethod
    def _get_dynamic_multiplier(cls_or_scalar: Any, context: dict[str, Any], is_array: bool) -> float:
        if isinstance(cls_or_scalar, type) and hasattr(cls_or_scalar, '_to_base_value'):
            m1 = cls_or_scalar(1.0, context=context)._to_base_value()
            m0 = cls_or_scalar(0.0, context=context)._to_base_value()
            mult = m1 - m0
        else:
            mult = cls_or_scalar
        return float(mult)
    
    @functools.lru_cache(maxsize=2048)
    def _cached_mul(cls, other: type[BaseUnit] | NumericLike) -> type[BaseUnit]:
        with _PhaethonUnitMeta._algebra_lock:
            if isinstance(other, _PhaethonUnitMeta):
                new_sig = _combine_signatures(getattr(cls, '_signature', frozenset()), 
                                            getattr(other, '_signature', frozenset()), 'mul')
                new_mult = float(cls.base_multiplier) * float(other.base_multiplier)
                new_name = _compact_name('mul', cls.__name__, other.__name__)
                new_symbol = f"{getattr(cls, 'symbol', '')}*{getattr(other, 'symbol', '')}"
                new_cls = cls._create_derived_class(new_name, new_sig, new_mult, new_symbol)
            elif isinstance(other, (int, float)):
                new_sig = getattr(cls, '_signature', frozenset())
                new_mult = float(cls.base_multiplier) * float(other)
                new_name = _compact_name('mul', cls.__name__, 'scalar')
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
                    return self_obj._value * v1 * v2

                @classmethod
                def new_from_base(cls_obj: type, base_val: Any, context: dict[str, Any]) -> Any:
                    is_arr = HAS_NUMPY and isinstance(base_val, (np.ndarray, np.generic))
                    v1 = _PhaethonUnitMeta._get_dynamic_multiplier(left_cls, context, is_arr)
                    v2 = _PhaethonUnitMeta._get_dynamic_multiplier(right_cls, context, is_arr)
                    return base_val / (v1 * v2)

                new_cls._to_base_value = new_to_base
                new_cls._from_base_value = new_from_base # type: ignore
            
            return new_cls

    def __mul__(cls, other: Any) -> type['BaseUnit']:
        if not isinstance(other, (type, int, float, str)):
            return NotImplemented
        return cls._cached_mul(other)

    def __rmul__(cls, other: Any) -> type['BaseUnit']:
        return _PhaethonUnitMeta.__mul__(cls, other)
    
    @functools.lru_cache(maxsize=2048)
    def _cached_truediv(cls, other: type[BaseUnit] | NumericLike) -> type[BaseUnit]:
        with _PhaethonUnitMeta._algebra_lock:
            if isinstance(other, _PhaethonUnitMeta):
                new_sig = _combine_signatures(getattr(cls, '_signature', frozenset()), 
                                            getattr(other, '_signature', frozenset()), 'div')
                if getattr(other, 'base_multiplier', 0.0) == 0.0:
                    raise ZeroDivisionError()
                new_mult = float(cls.base_multiplier) / float(other.base_multiplier)
                new_name = _compact_name('div', cls.__name__, other.__name__)
                new_symbol = f"{getattr(cls, 'symbol', '')}/{getattr(other, 'symbol', '')}"
                new_cls = cls._create_derived_class(new_name, new_sig, new_mult, new_symbol)
            elif isinstance(other, (int, float)):
                if other == 0: raise ZeroDivisionError()
                new_sig = getattr(cls, '_signature', frozenset())
                new_mult = float(cls.base_multiplier) / float(other)
                new_name = _compact_name('div', cls.__name__, 'scalar')
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
                    return (self_obj._value * v1) / v2

                @classmethod
                def new_from_base(cls_obj: type, base_val: Any, context: dict[str, Any]) -> Any:
                    is_arr = HAS_NUMPY and isinstance(base_val, (np.ndarray, np.generic))
                    v1 = _PhaethonUnitMeta._get_dynamic_multiplier(left_cls, context, is_arr)
                    v2 = _PhaethonUnitMeta._get_dynamic_multiplier(right_cls, context, is_arr)
                    return (base_val * v2) / v1

                new_cls._to_base_value = new_to_base
                new_cls._from_base_value = new_from_base

            return new_cls

    def __truediv__(cls, other: Any) -> type['BaseUnit']:
        if not isinstance(other, (type, int, float, str)):
            return NotImplemented
        return cls._cached_truediv(other)

    @functools.lru_cache(maxsize=2048)
    def _cached_pow(cls, power: int | float) -> type[BaseUnit]:
        if not isinstance(power, (int, float)): return NotImplemented # type: ignore
        
        with _PhaethonUnitMeta._algebra_lock:
            current_sig = dict(getattr(cls, '_signature', frozenset()))
            new_sig = frozenset({dim: exp * power for dim, exp in current_sig.items()}.items())
            new_mult = float(cls.base_multiplier) ** float(power)
            
            sym = getattr(cls, 'symbol', '')
            new_symbol = f"({sym})^{power}" if '/' in sym or '*' in sym else f"{sym}^{power}"
            new_name = _compact_name('pow', cls.__name__, str(power).replace('.', '_'))
            new_cls = cls._create_derived_class(new_name, new_sig, new_mult, new_symbol)
            
            if new_cls.__name__.startswith('Derived_'):
                left_cls = cls
                def new_to_base(self_obj: Any) -> Any:
                    is_arr = HAS_NUMPY and isinstance(self_obj._value, (np.ndarray, np.generic))
                    v1 = _PhaethonUnitMeta._get_dynamic_multiplier(left_cls, self_obj.context, is_arr)
                    return self_obj._value * (v1 ** float(power))

                @classmethod
                def new_from_base(cls_obj: type, base_val: Any, context: dict[str, Any]) -> Any:
                    is_arr = HAS_NUMPY and isinstance(base_val, (np.ndarray, np.generic))
                    v1 = _PhaethonUnitMeta._get_dynamic_multiplier(left_cls, context, is_arr)
                    return base_val / (v1 ** float(power))

                new_cls._to_base_value = new_to_base
                new_cls._from_base_value = new_from_base
            
            return new_cls

    def __pow__(cls, power: Any) -> type['BaseUnit']:
        if not isinstance(power, (int, float, str)):
            return NotImplemented
        return cls._cached_pow(power)
    
    def __matmul__(cls, other: type[BaseUnit]) -> type[BaseUnit]:
        return _PhaethonUnitMeta.__mul__(cls, other)

    def __rmatmul__(cls, other: type[BaseUnit]) -> type[BaseUnit]:
        return _PhaethonUnitMeta.__mul__(cls, other)
    
    @functools.lru_cache(maxsize=2048)
    def _cached_rtruediv(cls, other: NumericLike) -> type[BaseUnit]:
        if not isinstance(other, (int, float)):
            return NotImplemented
            
        with _PhaethonUnitMeta._algebra_lock:
            if getattr(cls, 'base_multiplier', 0.0) == 0.0: raise ZeroDivisionError()

            current_sig = dict(getattr(cls, '_signature', frozenset()))
            new_sig = frozenset({dim: -exp for dim, exp in current_sig.items()}.items())
            
            new_mult = float(other) / float(cls.base_multiplier)
            new_name = _compact_name('rdiv', 'scalar', cls.__name__)
            new_symbol = f"{other}/{getattr(cls, 'symbol', '')}"
            
            new_cls = cls._create_derived_class(new_name, new_sig, new_mult, new_symbol)
            
            if new_cls.__name__.startswith('Derived_'):
                right_cls = cls
                def new_to_base(self_obj: Any) -> Any:
                    is_arr = HAS_NUMPY and isinstance(self_obj._value, (np.ndarray, np.generic))
                    v2 = _PhaethonUnitMeta._get_dynamic_multiplier(right_cls, self_obj.context, is_arr)
                    return self_obj._value * (float(other) / v2)

                @classmethod
                def new_from_base(cls_obj: type, base_val: Any, context: dict[str, Any]) -> Any:
                    is_arr = HAS_NUMPY and isinstance(base_val, (np.ndarray, np.generic))
                    v2 = _PhaethonUnitMeta._get_dynamic_multiplier(right_cls, context, is_arr)
                    return base_val / (float(other) / v2)

                new_cls._to_base_value = new_to_base
                new_cls._from_base_value = new_from_base # type: ignore

            return new_cls

    def __rtruediv__(cls, other: Any) -> type['BaseUnit']:
        if not isinstance(other, (int, float, str)):
            return NotImplemented
        return cls._cached_rtruediv(other)

    def __lt__(cls, other: Any) -> bool:
        if not isinstance(other, type) or not hasattr(other, 'base_multiplier'): return NotImplemented
        if getattr(cls, 'dimension', None) != getattr(other, 'dimension', None):
            raise PhysicalAlgebraError("<", _fmtdim(cls), _fmtdim(other))
        return float(cls.base_multiplier) < float(other.base_multiplier)

    def __le__(cls, other: Any) -> bool:
        if not isinstance(other, type) or not hasattr(other, 'base_multiplier'): return NotImplemented
        if getattr(cls, 'dimension', None) != getattr(other, 'dimension', None):
            raise PhysicalAlgebraError("<=", _fmtdim(cls), _fmtdim(other))
        return float(cls.base_multiplier) <= float(other.base_multiplier)

    def __gt__(cls, other: Any) -> bool:
        if not isinstance(other, type) or not hasattr(other, 'base_multiplier'): return NotImplemented
        if getattr(cls, 'dimension', None) != getattr(other, 'dimension', None):
            raise PhysicalAlgebraError(">", _fmtdim(cls), _fmtdim(other))
        return float(cls.base_multiplier) > float(other.base_multiplier)

    def __ge__(cls, other: Any) -> bool:
        if not isinstance(other, type) or not hasattr(other, 'base_multiplier'): return NotImplemented
        if getattr(cls, 'dimension', None) != getattr(other, 'dimension', None):
            raise PhysicalAlgebraError(">=", _fmtdim(cls), _fmtdim(other))
        return float(cls.base_multiplier) >= float(other.base_multiplier)

    def _get_unit_string(cls) -> str:
        if not getattr(cls, '_signature', None):
            return "dimensionless"

        sup_map = {
            '0': '⁰', '1': '¹', '2': '²', '3': '³', '4': '⁴', 
            '5': '⁵', '6': '⁶', '7': '⁷', '8': '⁸', '9': '⁹',
            '.': '·', '-': '⁻'
        }
        dim_order = {
            'mass': 1, 'length': 2, 'time': 3, 'electric_current': 4,
            'temperature': 5, 'amount_of_substance': 6, 'luminous_intensity': 7
        }

        sorted_sig = sorted(cls._signature, key=lambda x: (dim_order.get(x[0], 99), x[0]))

        num, den = [], []
        for dim, exp in sorted_sig:
            sym = getattr(ureg().baseof(dim), 'symbol', dim)
            abs_exp = abs(exp)
            exp_str = ""
            if abs_exp != 1:
                if isinstance(abs_exp, float) and abs_exp.is_integer(): abs_exp = int(abs_exp)
                raw_exp_str = str(abs_exp)
                try: exp_str = "".join(sup_map[c] for c in raw_exp_str)
                except KeyError: exp_str = f"^{raw_exp_str}"
            part = f"{sym}{exp_str}"
            if exp > 0: num.append(part)
            else: den.append(part)

        num_str = "·".join(num) if num else "1"
        if not den: return num_str
        den_str = "·".join(den)
        if len(den) > 1: return f"{num_str}/({den_str})"
        return f"{num_str}/{den_str}"

class _DecomposeDispatcher:
    def __init__(self, bind_target: Any = None) -> None:
        self._bind_target = bind_target

    def __get__(self, instance: Any, owner: type) -> '_DecomposeDispatcher':
        return _DecomposeDispatcher(instance if instance is not None else owner)

    def __call__(self) -> str:
        if self._bind_target is None:
            return "dimensionless"
            
        is_class = isinstance(self._bind_target, type)
        cls_ref = self._bind_target if is_class else type(self._bind_target)
        unit_str = cls_ref._get_unit_string() # type: ignore
        
        if is_class:
            return unit_str

        base_val = self._bind_target._to_base_value()

        if HAS_NUMPY and isinstance(base_val, np.ndarray):
            return f"{base_val} {unit_str}"
    
        return f"{base_val:g} {unit_str}"

class BaseUnit(metaclass=_PhaethonUnitMeta):
    """
    The foundational core class for all units in Phaethon.
    """
    dimension: str | None = None
    symbol: str | None = None
    aliases: list[str] | None = None
    base_multiplier: float = 1.0
    base_offset: float = 0.0
    is_anonymous: bool = False
    __semantic__: str | None = None

    def __init_subclass__(cls, **kwargs: Any) -> None:
        super().__init_subclass__(**kwargs)
        if not getattr(cls, 'is_anonymous', False) and getattr(cls, 'dimension', 'anonymous') != 'anonymous':
            ureg()._register(cls)
            
            sig = getattr(cls, '_signature', None)
            if sig:
                ureg().inject_dna(sig, cls.dimension)

            _PhaethonUnitMeta._cached_mul.cache_clear()
            _PhaethonUnitMeta._cached_truediv.cache_clear()
            _PhaethonUnitMeta._cached_pow.cache_clear()
            _PhaethonUnitMeta._cached_rtruediv.cache_clear()

    def __init__(self, value: NumericLike, context: ContextDict | None = None) -> None:
        if type(self) is BaseUnit:
            raise TypeError("'BaseUnit' is an abstract class and cannot be instantiated directly.")
        
        if HAS_NUMPY and isinstance(value, (np.ndarray, np.generic)):
            self._value = value
        elif HAS_NUMPY and isinstance(value, (list, tuple)):
            self._value = np.array(value, dtype=float)
        elif hasattr(value, '__float__') or isinstance(value, (int, float, str)):
            self._value = float(value)
        else:
            raise TypeError(f"Value must be numeric or array, got {type(value).__name__}")
            
        self.context = context or {}

    # =========================================================================
    # PUBLIC PROPERTIES (THE DX INTERFACE)
    # =========================================================================
    @property
    def mag(self) -> float | np.ndarray:
        """Returns the magnitude."""
        return self._value

    @property
    def si(self) -> BaseUnit | Any:
        """
        The SI Core Extractor (De-Phantomizer).
        Strips all phantom units and exclusive domain locks, 
        returning the pure SI base canvas (multiplier = 1.0).
        """
        phantoms = ureg().get_phantoms()
        core_sig = frozenset((d, e) for d, e in self._signature if d not in phantoms)
        CoreClass = _find_existing_class(core_sig, 1.0)
        
        if not CoreClass:
            CoreClass = self.__class__._create_derived_class(
                f"RawSI_{self.__class__.__name__}", core_sig, 1.0, "raw_si"
            )
            
        base_val = self._to_base_value()
        core_val = CoreClass._from_base_value(base_val, self.context)
        return CoreClass(core_val, context=self.context)
    
    @property
    def shape(self) -> tuple[int, ...]:
        if HAS_NUMPY and isinstance(self._value, (np.ndarray, np.generic)):
            return self._value.shape # type: ignore
        return ()

    @property
    def ndim(self) -> int:
        if HAS_NUMPY and isinstance(self._value, (np.ndarray, np.generic)):
            return self._value.ndim # type: ignore
        return 0

    @property
    def T(self) -> BaseUnit:
        if HAS_NUMPY and isinstance(self._value, (np.ndarray, np.generic)):
            return self.__class__(self._value.T, context=self.context)
        return self

    def sum(self, axis: int | tuple[int, ...] | None = None, keepdims: bool = False, **kwargs: Any) -> BaseUnit:
        if HAS_NUMPY and isinstance(self._value, (np.ndarray, np.generic)):
            new_val = self._value.sum(axis=axis, keepdims=keepdims, **kwargs)
            return self.__class__(new_val, context=self.context)
        return self

    def mean(self, axis: int | tuple[int, ...] | None = None, keepdims: bool = False, **kwargs: Any) -> BaseUnit:
        if HAS_NUMPY and isinstance(self._value, (np.ndarray, np.generic)):
            new_val = self._value.mean(axis=axis, keepdims=keepdims, **kwargs)
            return self.__class__(new_val, context=self.context)
        return self

    def max(self, axis: int | tuple[int, ...] | None = None, keepdims: bool = False, **kwargs: Any) -> BaseUnit:
        if HAS_NUMPY and isinstance(self._value, (np.ndarray, np.generic)):
            new_val = self._value.max(axis=axis, keepdims=keepdims, **kwargs)
            return self.__class__(new_val, context=self.context)
        return self

    def min(self, axis: int | tuple[int, ...] | None = None, keepdims: bool = False, **kwargs: Any) -> BaseUnit:
        if HAS_NUMPY and isinstance(self._value, (np.ndarray, np.generic)):
            new_val = self._value.min(axis=axis, keepdims=keepdims, **kwargs)
            return self.__class__(new_val, context=self.context)
        return self

    def reshape(self, shape: tuple[int, ...] | int, *args: Any, order: str = 'C') -> BaseUnit:
        if HAS_NUMPY and isinstance(self._value, (np.ndarray, np.generic)):
            new_val = self._value.reshape(shape, *args, order=order)
            return self.__class__(new_val, context=self.context)
        return self

    def flatten(self, order: str = 'C') -> BaseUnit:
        if HAS_NUMPY and isinstance(self._value, (np.ndarray, np.generic)):
            new_val = self._value.flatten(order=order)
            return self.__class__(new_val, context=self.context)
        return self
    
    # =========================================================================
    # INTERNAL CORE LOGIC
    # =========================================================================
    def _to_base_value(self) -> float | Any:
        with using(context=self.context):
            return (self._value + float(self.base_offset)) * float(self.base_multiplier)

    @classmethod
    def _from_base_value(cls, base_val: float | Any, context: dict[str, Any]) -> float | Any:
        with using(context=context):
            return (base_val / float(cls.base_multiplier)) - float(cls.base_offset)

    def _recover_canonical_unit(self) -> BaseUnit:
        canonical_cls = _find_existing_class(self._signature, float(self.base_multiplier))
        
        if canonical_cls and not canonical_cls.__name__.startswith('Derived_'):
            return canonical_cls(self.mag, context=self.context)
        return self


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
        'mod': ('__mod__', '__rmod__'),
        'sqrt': ('_numpy_sqrt', None),
        'square': ('_numpy_square', None),
        'cbrt': ('_numpy_cbrt', None)
    }

    __array_priority__ = 10000

    def __array_ufunc__(self, ufunc: Any, method: str, *inputs: Any, **kwargs: Any) -> BaseUnit | Any:
        if ufunc.__name__ in self._ROUTED_UFUNCS:
            if method != '__call__': return NotImplemented
            dunder, rdunder = self._ROUTED_UFUNCS[ufunc.__name__]
            if len(inputs) == 1:
                if inputs[0] is self: return getattr(self, dunder)()
            elif len(inputs) == 2:
                if inputs[0] is self: return getattr(self, dunder)(inputs[1])
                elif inputs[1] is self and rdunder: return getattr(self, rdunder)(inputs[0])
            return NotImplemented

        if ufunc.__name__ not in self._ALLOWED_UFUNCS:
            raise TypeError(f"Operation 'np.{ufunc.__name__}' is blocked.")

        raw_inputs = []
        for inp in inputs:
            if isinstance(inp, BaseUnit):
                if self.dimension != getattr(inp, 'dimension', None):
                    raise PhysicalAlgebraError(f"np.{ufunc.__name__}", _fmtdim(self.__class__), _fmtdim(inp.__class__))
                raw_inputs.append(inp._to_base_value())
            else:
                raw_inputs.append(inp)

        raw_result = getattr(ufunc, method)(*raw_inputs, **kwargs)
        merged_context = {**self.context, "__is_math_op__": True}
        final_value = self.__class__._from_base_value(raw_result, merged_context)
        return self.__class__(final_value, context=merged_context)
    
    def __array_function__(self, func: Any, types: Any, args: Any, kwargs: Any) -> BaseUnit:
        if func.__name__ not in self._ALLOWED_FUNCTIONS:
            raise TypeError(f"Function 'np.{func.__name__}' is blocked to preserve dimensional integrity.")

        def _extract_raw(obj: Any) -> Any:
            if isinstance(obj, BaseUnit): return obj._to_base_value()
            if isinstance(obj, (list, tuple)): return [_extract_raw(o) for o in obj]
            return obj

        raw_args = tuple(_extract_raw(arg) for arg in args)
        raw_result = func(*raw_args, **kwargs)
        final_value = self.__class__._from_base_value(raw_result, self.context)
        return self.__class__(final_value, context=self.context)
    
    def _numpy_sqrt(self) -> BaseUnit | Any: return self ** 0.5
    def _numpy_square(self) -> BaseUnit | Any: return self ** 2
    def _numpy_cbrt(self) -> BaseUnit | Any: return self ** (1.0/3.0)

    def __getattr__(self, name: str) -> Any:
        if name.startswith('_'): raise AttributeError(f"'{self.__class__.__name__}' object has no attribute '{name}'")
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
        if HAS_NUMPY and isinstance(self._value, (np.ndarray, np.generic)): return self.__class__(self._value[key], context=self.context)
        if isinstance(self._value, (list, tuple)): return self.__class__(self._value[key], context=self.context)
        raise TypeError(f"'{self.__class__.__name__}' object is not subscriptable")
    
    def __str__(self) -> str:
        try:
            if HAS_NUMPY and isinstance(self._value, (np.ndarray, np.generic)):
                val_mag = float(np.max(np.abs(self._value))) if self._value.size > 0 else 0.0
            else:
                val_mag = abs(float(self._value))
        except Exception:
            val_mag = 1.0
            
        auto_sci = val_mag > 0 and (val_mag < 1e-4 or val_mag >= 1e7)
        if HAS_NUMPY and isinstance(self._value, np.ndarray):
            return f"<{self.__class__.__name__} Array: {self.format(scinote=auto_sci, tag=False)}>"
        return self.format(scinote=auto_sci, tag=True)

    def __repr__(self) -> str:
        if HAS_NUMPY and isinstance(self._value, np.ndarray):
            return f"<{self.__class__.__name__} Array of shape {self._value.shape}>"
        return f"<{self.__class__.__name__}: {self._value} {self.symbol}>"

    def __float__(self) -> float:
        return float(self._value)

    def __int__(self) -> int:
        return int(self._value)

    @overload
    def to(self, unit: type[_UnitT], context: ContextDict | None = ...) -> _UnitT: ...
    @overload
    def to(self, unit: str, context: ContextDict | None = ...) -> BaseUnit: ...

    def to(self, unit: UnitLike | str, context: ContextDict | None = None) -> _UnitT | BaseUnit:
        """
        Converts the current physical instance to a target unit within the same dimensional domain.

        This method safely applies the required linear transformations (multiplier and offset) 
        to convert the magnitude into the target unit's scale. It strictly enforces dimensional 
        homogeneity, Isomorphic Firewalls (Phantom Units), and Exclusive Domain Locks.

        Args:
            unit: The destination unit class (e.g., u.Kilometer) or registered string alias (e.g., 'km').
            context: An optional dictionary containing execution context (e.g., for dynamic/runtime scaling).

        Returns:
            A new BaseUnit instance rescaled and wrapped in the target unit's physical DNA.

        Raises:
            TypeError: If the provided target unit is not a string or a valid BaseUnit subclass.
            DimensionMismatchError: If attempting to cast to a unit belonging to a fundamentally 
                different physical dimension (e.g., casting Mass to Length).
            SemanticMismatchError: If the conversion violates an Exclusive Domain Lock or 
                triggers a Phantom Unit collision.

        Examples:
            >>> distance = u.Meter(1500)
            >>> dist_km = distance.to(u.Kilometer)
            >>> print(dist_km)
            <Kilometer: 1.5 km>
        """
        from ..exceptions import SemanticMismatchError
        if isinstance(unit, str):
            try: TargetClass = ureg().get_unit_class(unit, expected_dim=self.dimension)
            except DimensionMismatchError:
                try: TargetClass = ureg().get_unit_class(unit)
                except Exception: raise TypeError(f"Invalid target in .to() method: '{unit}'.") from None
            except Exception: raise TypeError(f"Invalid target in .to() method: '{unit}'.") from None
        else:
            TargetClass = unit

        if not (isinstance(TargetClass, type) and issubclass(TargetClass, BaseUnit)):
            raise TypeError(f"The to() method expects a class unit, but it received an instance unit named '{type(unit).__name__}'.")

        target_dim = getattr(TargetClass, "dimension", None)
        is_same_dimension = (self.dimension == target_dim)
        
        self_sig = getattr(self.__class__, '_signature', frozenset())
        target_sig = getattr(TargetClass, '_signature', frozenset())
        is_same_dna = (self_sig == target_sig)

        if not (is_same_dimension or is_same_dna):
            phantoms = ureg().get_phantoms()
            self_core = frozenset((d, e) for d, e in self_sig if d not in phantoms)
            target_core = frozenset((d, e) for d, e in target_sig if d not in phantoms)
            
            if self_core == target_core:
                self_phantoms = {d for d, e in self_sig if d in phantoms}
                target_phantoms = {d for d, e in target_sig if d in phantoms}
                
                if self_phantoms and target_phantoms and (self_phantoms != target_phantoms):
                    p1 = list(self_phantoms)[0]
                    p2 = list(target_phantoms)[0]
                    raise SemanticMismatchError(f"Phantom Collision: Cannot cast '{p1}' to '{p2}'. Expected '{target_dim}', but got '{self.dimension}'.")
                is_same_dna = True

        if not (is_same_dimension or is_same_dna):
            raise DimensionMismatchError(str(self.dimension), str(target_dim), "Conversion")

        this_semantic = getattr(self, '__semantic__', None)
        target_semantic = getattr(TargetClass, '__semantic__', None)
        if this_semantic and target_semantic and (this_semantic != target_semantic):
            raise SemanticMismatchError(f"Cannot convert '{self.__class__.__name__}' to '{TargetClass.__name__}'. Semantic domains are strictly isolated.")

        is_exclusive = (getattr(self.__class__, '__exclusive_domain__', False) or getattr(TargetClass, '__exclusive_domain__', False))
        if is_exclusive and not is_same_dimension:
            raise SemanticMismatchError(f"Exclusive Domain Locked: Cannot cast '{self.__class__.__name__}' directly to '{TargetClass.__name__}'.")

        merged_context = {**self.context}
        if context: merged_context.update(context)
        
        original_context = self.context
        self.context = merged_context
        try: base_val = self._to_base_value()
        finally: self.context = original_context
            
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
        """Applies precise structural and numeric formatting to the magnitude using pure float formatting."""
        val = self._value
        
        if HAS_NUMPY and isinstance(val, (np.ndarray, np.generic)):
            def format_elem(x: Any) -> str:
                xf = float(x)
                if scinote:
                    digits = sigfigs - 1 if sigfigs is not None else prec
                    return f"{xf:.{digits}E}"
                s = f"{xf:.{prec}f}" if sigfigs is None else f"{xf:.{sigfigs}g}"
                if '.' in s and 'e' not in s.lower():
                    s = s.rstrip('0').rstrip('.')
                    if not s: s = "0"
                if delim:
                    separator = "," if delim is True or str(delim).lower() == "default" else str(delim)
                    parts = s.split('.')
                    parts[0] = f"{int(parts[0]):,}".replace(",", separator)
                    s = '.'.join(parts) if len(parts) > 1 else parts[0]
                return s

            val_str = np.array2string(val, formatter={'float_kind': format_elem, 'int': format_elem}, separator=', ', suppress_small=not scinote)
            return f"{val_str} {self.symbol}" if tag else val_str

        xf = float(val)
        if scinote:
            digits = sigfigs - 1 if sigfigs is not None else prec
            val_str = f"{xf:.{digits}E}"
        else:
            val_str = f"{xf:.{prec}f}" if sigfigs is None else f"{xf:.{sigfigs}g}"
            if '.' in val_str and 'e' not in val_str.lower():
                val_str = val_str.rstrip('0').rstrip('.')
                if not val_str: val_str = "0"

        if delim:
            separator = "," if delim is True or str(delim).lower() == "default" else str(delim)
            if not scinote and 'e' not in val_str.lower():
                parts = val_str.split('.')
                parts[0] = f"{int(parts[0]):,}".replace(",", separator)
                val_str = '.'.join(parts) if len(parts) > 1 else parts[0]

        return f"{val_str} {self.symbol}" if tag else val_str

    decompose: _DecomposeDispatcher = _DecomposeDispatcher()

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, BaseUnit): return NotImplemented
        if self.dimension != getattr(other, "dimension", None):
            raise PhysicalAlgebraError("==", _fmtdim(self.__class__), _fmtdim(other.__class__))
            
        v1, v2 = self._to_base_value(), other._to_base_value()
        atol = get_config("atol")
        rtol = get_config("rtol")

        if HAS_NUMPY and (isinstance(v1, (np.ndarray, np.generic)) or isinstance(v2, (np.ndarray, np.generic))):
            return np.isclose(v1, v2, rtol=rtol, atol=atol) # type: ignore
            
        return math.isclose(float(v1), float(v2), rel_tol=rtol, abs_tol=atol)
        
    def __ne__(self, other: object) -> bool:
        if not isinstance(other, BaseUnit): return NotImplemented
        if self.dimension != getattr(other, "dimension", None):
            raise PhysicalAlgebraError("!=", _fmtdim(self.__class__), _fmtdim(other.__class__))
            
        v1, v2 = self._to_base_value(), other._to_base_value()
        atol = get_config("atol")
        rtol = get_config("rtol")

        if HAS_NUMPY and (isinstance(v1, (np.ndarray, np.generic)) or isinstance(v2, (np.ndarray, np.generic))):
            return ~np.isclose(v1, v2, rtol=rtol, atol=atol) # type: ignore
            
        return not math.isclose(float(v1), float(v2), rel_tol=rtol, abs_tol=atol)

    def __lt__(self, other: BaseUnit) -> bool | Any:
        if not isinstance(other, BaseUnit): return NotImplemented
        if self.dimension != getattr(other, "dimension", None):
            raise PhysicalAlgebraError("<", _fmtdim(self.__class__), _fmtdim(other.__class__))
        v1, v2 = self._to_base_value(), other._to_base_value()
        return v1 < v2

    def __le__(self, other: BaseUnit) -> bool | Any:
        if not isinstance(other, BaseUnit): return NotImplemented
        if self.dimension != getattr(other, "dimension", None):
            raise PhysicalAlgebraError("<=", _fmtdim(self.__class__), _fmtdim(other.__class__))
        v1, v2 = self._to_base_value(), other._to_base_value()
        
        atol = get_config("atol")
        rtol = get_config("rtol")

        if HAS_NUMPY and (isinstance(v1, (np.ndarray, np.generic)) or isinstance(v2, (np.ndarray, np.generic))):
            return (v1 < v2) | np.isclose(v1, v2, rtol=rtol, atol=atol) # type: ignore
            
        return v1 < v2 or math.isclose(float(v1), float(v2), rel_tol=rtol, abs_tol=atol)

    def __gt__(self, other: BaseUnit) -> bool | Any:
        if not isinstance(other, BaseUnit): return NotImplemented
        if self.dimension != getattr(other, "dimension", None):
            raise PhysicalAlgebraError(">", _fmtdim(self.__class__), _fmtdim(other.__class__))
        v1, v2 = self._to_base_value(), other._to_base_value()
        return v1 > v2

    def __ge__(self, other: BaseUnit) -> bool | Any:
        if not isinstance(other, BaseUnit): return NotImplemented
        if self.dimension != getattr(other, "dimension", None):
            raise PhysicalAlgebraError(">=", _fmtdim(self.__class__), _fmtdim(other.__class__))
        v1, v2 = self._to_base_value(), other._to_base_value()
        
        atol = get_config("atol")
        rtol = get_config("rtol")

        if HAS_NUMPY and (isinstance(v1, (np.ndarray, np.generic)) or isinstance(v2, (np.ndarray, np.generic))):
            return (v1 > v2) | np.isclose(v1, v2, rtol=rtol, atol=atol) # type: ignore
            
        return v1 > v2 or math.isclose(float(v1), float(v2), rel_tol=rtol, abs_tol=atol)
    
    def __add__(self, other: BaseUnit) -> BaseUnit | Any:
        if isinstance(other, type) and issubclass(other, BaseUnit):
            other = other(1.0, context=self.context)

        if not isinstance(other, BaseUnit):
            if isinstance(other, (int, float)) or (HAS_NUMPY and isinstance(other, (np.ndarray, np.generic))):
                raise TypeError(f"Cannot add a dimensionless scalar/array to a dimensioned unit '{self.__class__.__name__}'. ")
            return NotImplemented
            
        if self.dimension != getattr(other, "dimension", None):
            self_sig = getattr(self.__class__, '_signature', frozenset())
            other_sig = getattr(other.__class__, '_signature', frozenset())
            phantoms = ureg().get_phantoms()
            
            self_core = frozenset((d, e) for d, e in self_sig if d not in phantoms)
            other_core = frozenset((d, e) for d, e in other_sig if d not in phantoms)
            
            if self_core == other_core:
                from ..exceptions import SemanticMismatchError
                raise SemanticMismatchError(f"Phantom Collision! Cannot add '{self.dimension}' and '{getattr(other, 'dimension', None)}' despite sharing identical SI DNA.")
                
            raise PhysicalAlgebraError("+", _fmtdim(self.__class__), _fmtdim(other.__class__))

        if getattr(self, '__semantic__', None) != getattr(other, '__semantic__', None):
            from ..exceptions import SemanticMismatchError
            raise SemanticMismatchError(f"Semantic Collision! Cannot add '{getattr(self, '__semantic__', 'generic')}' with '{getattr(other, '__semantic__', 'generic')}'.")

        total_base = self._to_base_value() + other._to_base_value()
        merged_context = {**other.context, **self.context, "__is_math_op__": True}
        final_value = self.__class__._from_base_value(total_base, merged_context)
        return self.__class__(final_value, context=merged_context)

    def __sub__(self, other: BaseUnit) -> BaseUnit | Any:
        if isinstance(other, type) and issubclass(other, BaseUnit):
            other = other(1.0, context=self.context)

        if not isinstance(other, BaseUnit):
            if isinstance(other, (int, float)) or (HAS_NUMPY and isinstance(other, (np.ndarray, np.generic))):
                raise TypeError(f"Cannot subtrack a dimensionless scalar/array to a dimensioned unit '{self.__class__.__name__}'. ")
            return NotImplemented
            
        if self.dimension != getattr(other, "dimension", None):
            self_sig = getattr(self.__class__, '_signature', frozenset())
            other_sig = getattr(other.__class__, '_signature', frozenset())
            phantoms = ureg().get_phantoms()
            self_core = frozenset((d, e) for d, e in self_sig if d not in phantoms)
            other_core = frozenset((d, e) for d, e in other_sig if d not in phantoms)
            if self_core == other_core:
                from ..exceptions import SemanticMismatchError
                raise SemanticMismatchError(f"Phantom Collision! Cannot subtract '{getattr(other, 'dimension', None)}' from '{self.dimension}' despite sharing identical SI DNA.")

            raise PhysicalAlgebraError("-", _fmtdim(self.__class__), _fmtdim(other.__class__))

        if getattr(self, '__semantic__', None) != getattr(other, '__semantic__', None):
            from ..exceptions import SemanticMismatchError
            raise SemanticMismatchError(f"Semantic Collision: Cannot subtract '{getattr(other, '__semantic__', 'generic')}' from '{getattr(self, '__semantic__', 'generic')}'.")
    
        total_base = self._to_base_value() - other._to_base_value()
        merged_context = {**other.context, **self.context, "__is_math_op__": True}
        final_value = self.__class__._from_base_value(total_base, merged_context)
        return self.__class__(final_value, context=merged_context)
    
    def __mul__(self, other: NumericLike | BaseUnit | type[BaseUnit]) -> BaseUnit:
        if isinstance(other, type) and issubclass(other, BaseUnit):
            other = other(1.0, context=self.context)

        if isinstance(other, (int, float)) or (HAS_NUMPY and isinstance(other, (np.ndarray, np.generic))):
            new_val = self._value * other
            merged_context = {**self.context, "__is_math_op__": True}
            return self.__class__(new_val, context=merged_context)
        
        if isinstance(other, BaseUnit):
            if getattr(other.__class__, '__is_logarithmic__', False): return NotImplemented
            ResultClass = self.__class__ * other.__class__
            merged_context = {**other.context, **self.context, "__is_math_op__": True}
            
            if getattr(ResultClass, 'dimension', None) == 'dimensionless':
                from ..core.units.scalar import Dimensionless
                return Dimensionless(self._to_base_value() * other._to_base_value(), context=merged_context)
                
            new_val = self._value * other._value
            result = ResultClass(new_val, context=merged_context)
            return result._recover_canonical_unit()
            
        return NotImplemented

    def __rmul__(self, other: NumericLike | BaseUnit) -> BaseUnit | Any:
        return self.__mul__(other)

    def __matmul__(self, other: NumericLike | BaseUnit) -> BaseUnit | Any:
        if not HAS_NUMPY: raise TypeError("Matrix multiplication (@) requires NumPy.")
        if isinstance(other, (np.ndarray, np.generic)):
            new_val = np.matmul(self._value, other)
            merged_context = {**self.context, "__is_math_op__": True}
            return self.__class__(new_val, context=merged_context)
            
        if isinstance(other, BaseUnit):
            ResultClass = self.__class__ * other.__class__
            new_val = np.matmul(self._value, other._value)
            merged_context = {**other.context, **self.context, "__is_math_op__": True}
            return ResultClass(new_val, context=merged_context)
            
        return NotImplemented

    def __rmatmul__(self, other: NumericLike | BaseUnit) -> BaseUnit | Any:
        if not HAS_NUMPY: raise TypeError("Matrix multiplication (@) requires NumPy.")
        if isinstance(other, (np.ndarray, np.generic)):
            new_val = np.matmul(other, self._value)
            merged_context = {**self.context, "__is_math_op__": True}
            return self.__class__(new_val, context=merged_context)
            
        return NotImplemented

    def __neg__(self: _UnitT) -> _UnitT:
        merged_context = {**self.context, "__is_math_op__": True}
        return self.__class__(-self._value, context=merged_context)

    def __pos__(self: _UnitT) -> _UnitT:
        merged_context = {**self.context, "__is_math_op__": True}
        return self.__class__(+self._value, context=merged_context)

    def __abs__(self: _UnitT) -> _UnitT:
        merged_context = {**self.context, "__is_math_op__": True}
        if HAS_NUMPY and isinstance(self._value, (np.ndarray, np.generic)): return self.__class__(np.abs(self._value), context=merged_context)
        return self.__class__(abs(self._value), context=merged_context)

    def __round__(self: _UnitT, ndigits: int | None = None) -> _UnitT:
        merged_context = {**self.context, "__is_math_op__": True}
        if HAS_NUMPY and isinstance(self._value, (np.ndarray, np.generic)): return self.__class__(np.round(self._value, ndigits), context=merged_context)
        return self.__class__(round(self._value, ndigits), context=merged_context)

    def __floordiv__(self, other: NumericLike | BaseUnit) -> BaseUnit | Any:
        if isinstance(other, type) and issubclass(other, BaseUnit):
            other = other(1.0, context=self.context)

        if isinstance(other, (int, float)) or (HAS_NUMPY and isinstance(other, (np.ndarray, np.generic))):
            new_val = self._value // other
            merged_context = {**self.context, "__is_math_op__": True}
            return self.__class__(new_val, context=merged_context)
            
        if isinstance(other, BaseUnit):
            if self.dimension != getattr(other, "dimension", None):
                raise PhysicalAlgebraError("//", _fmtdim(self.__class__), _fmtdim(other.__class__))
            total_base = self._to_base_value() // other._to_base_value()
            merged_context = {**other.context, **self.context, "__is_math_op__": True}
            from .units.scalar import Dimensionless
            return Dimensionless(total_base, context=merged_context)
            
        return NotImplemented

    def __mod__(self, other: NumericLike | BaseUnit) -> BaseUnit | Any:
        if isinstance(other, type) and issubclass(other, BaseUnit):
            other = other(1.0, context=self.context)

        if isinstance(other, (int, float)) or (HAS_NUMPY and isinstance(other, (np.ndarray, np.generic))):
            new_val = self._value % other
            merged_context = {**self.context, "__is_math_op__": True}
            return self.__class__(new_val, context=merged_context)
            
        if isinstance(other, BaseUnit):
            if self.dimension != getattr(other, "dimension", None):
                raise PhysicalAlgebraError("%", _fmtdim(self.__class__), _fmtdim(other.__class__))
            total_base = self._to_base_value() % other._to_base_value()
            merged_context = {**other.context, **self.context, "__is_math_op__": True}
            final_value = self.__class__._from_base_value(total_base, merged_context)
            return self.__class__(final_value, context=merged_context)
            
        return NotImplemented
    
    def __truediv__(self, other: NumericLike | BaseUnit | type[BaseUnit]) -> BaseUnit:
        if isinstance(other, type) and issubclass(other, BaseUnit):
            other = other(1.0, context=self.context)

        if isinstance(other, (int, float)) or (HAS_NUMPY and isinstance(other, (np.ndarray, np.generic))):
            new_val = self._value / other
            merged_context = {**self.context, "__is_math_op__": True}
            return self.__class__(new_val, context=merged_context)
            
        if isinstance(other, BaseUnit):
            if getattr(other.__class__, '__is_logarithmic__', False): return NotImplemented
            ResultClass = self.__class__ / other.__class__
            merged_context = {**other.context, **self.context, "__is_math_op__": True}
            
            if getattr(ResultClass, 'dimension', None) == 'dimensionless':
                from .units.scalar import Dimensionless
                return Dimensionless(self._to_base_value() / other._to_base_value(), context=merged_context)
                
            new_val = self._value / other._value
            result = ResultClass(new_val, context=merged_context)
            return result._recover_canonical_unit()
            
        return NotImplemented
    
    def __rtruediv__(self, other: NumericLike | BaseUnit) -> BaseUnit | Any:
        if isinstance(other, type) and issubclass(other, BaseUnit):
            other = other(1.0, context=self.context)
            return other / self
        
        if isinstance(other, (int, float)) or (HAS_NUMPY and isinstance(other, (np.ndarray, np.generic))):
            ResultClass = 1 / self.__class__
            new_val = other / self._value
            merged_context = {**self.context, "__is_math_op__": True}
            return ResultClass(new_val, context=merged_context)
            
        return NotImplemented

    def __pow__(self, power: int | float) -> BaseUnit:
        if isinstance(power, (int, float)):
            ResultClass = self.__class__ ** power
            new_val = self._value ** power
            merged_context = {**self.context, "__is_math_op__": True}
            return ResultClass(new_val, context=merged_context)
        return NotImplemented

    def __radd__(self, other: Any) -> BaseUnit | Any:
        if isinstance(other, type) and issubclass(other, BaseUnit):
            other = other(1.0, context=self.context)
            return other + self
        return self.__add__(other)

    def __rsub__(self, other: Any) -> BaseUnit | Any:
        if isinstance(other, type) and issubclass(other, BaseUnit):
            other = other(1.0, context=self.context)
            return other - self
        return NotImplemented
    
    def __invert__(self) -> BaseUnit | Any:
        """
        The Base Unit Converter (~).
        """
        from .registry import ureg
        base_cls = ureg().baseof(self.dimension)
        return self.to(base_cls)
    
    def __array__(self, dtype: Any = None) -> Any:
        if HAS_NUMPY: return np.asarray(self._value, dtype=dtype)
        return np.array([self._value], dtype=dtype)