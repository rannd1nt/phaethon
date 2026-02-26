import math
from decimal import Decimal, getcontext
from typing import Union, Optional, List, Any, Type, Dict
from .registry import default_ureg
from ..exceptions import DimensionMismatchError
from .axioms import _normalize_types

try:
    import numpy as np
    HAS_NUMPY = True
except ImportError:
    HAS_NUMPY = False

# =========================================================================
# THE METACLASS ENGINE (v0.2.0)
# =========================================================================
def _combine_signatures(sig1: frozenset, sig2: frozenset, operation: str) -> frozenset:
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

def _find_existing_class(signature: frozenset, target_multiplier: float) -> Optional[Type]:
    from .registry import default_ureg
    resolved_dim = default_ureg.resolve_signature(signature)
    
    if resolved_dim == 'anonymous':
        return None
        
    if math.isclose(target_multiplier, 1.0, rel_tol=1e-9):
        try:
            base_cls = default_ureg.baseof(resolved_dim)
            if float(getattr(base_cls, 'base_offset', 0.0)) == 0.0:
                return base_cls
        except ValueError:
            pass
            
    candidates = default_ureg.unitsin(resolved_dim, ascls=True)
    valid_matches = []
    
    for cls in candidates:
        if math.isclose(float(getattr(cls, 'base_multiplier', 0)), target_multiplier, rel_tol=1e-9):
            if float(getattr(cls, 'base_offset', 0.0)) == 0.0:
                valid_matches.append(cls)
                
    if not valid_matches:
        return None
        
    return valid_matches[0]

class ChisaUnitMeta(type):
    """
    Metaclass that tracks dimensional signatures and dynamically generates 
    new derived unit classes during cross-unit algebra (e.g., u.Meter / u.Second).
    """
    def __new__(mcs, name, bases, namespace):
        cls = super().__new__(mcs, name, bases, namespace)
        if '_signature' not in namespace:
            dim = getattr(cls, 'dimension', None)
            if dim and dim != 'anonymous':
                from .registry import default_ureg
                cls._signature = default_ureg.get_signature_for_dim(dim)
            else:
                cls._signature = frozenset()
        return cls

    def _create_derived_class(cls, new_name, new_sig, new_mult, new_symbol):
        existing_cls = _find_existing_class(new_sig, float(new_mult))
        if existing_cls:
            return existing_cls

        from .registry import default_ureg
        resolved_dim = default_ureg.resolve_signature(new_sig)
        
        attrs = {
            '_signature': new_sig,
            'base_multiplier': float(new_mult),
            'base_offset': 0.0,
            'dimension': resolved_dim,
            'symbol': new_symbol,
            'is_anonymous': (resolved_dim == 'anonymous')
        }
        
        base_unit_cls = next((c for c in cls.__mro__ if c.__name__ == 'BaseUnit'), cls.__bases__[0])
        return type(new_name, (base_unit_cls,), attrs)

    def __mul__(cls, other) -> Type['BaseUnit']:
        """Synthesizes a new class by multiplying dimensions and base multipliers."""
        if isinstance(other, ChisaUnitMeta):
            new_sig = _combine_signatures(getattr(cls, '_signature', frozenset()), 
                                          getattr(other, '_signature', frozenset()), 'mul')
            new_mult = Decimal(str(cls.base_multiplier)) * Decimal(str(other.base_multiplier))
            new_name = f"Derived_{cls.__name__}_mul_{other.__name__}"
            new_symbol = f"{getattr(cls, 'symbol', '')}*{getattr(other, 'symbol', '')}"
            return cls._create_derived_class(new_name, new_sig, new_mult, new_symbol)
            
        elif isinstance(other, (int, float, Decimal)):
            new_sig = getattr(cls, '_signature', frozenset())
            new_mult = Decimal(str(cls.base_multiplier)) * Decimal(str(other))
            new_name = f"Derived_{cls.__name__}_mul_scalar"
            new_symbol = f"{other}*{getattr(cls, 'symbol', '')}"
            return cls._create_derived_class(new_name, new_sig, new_mult, new_symbol)
        return NotImplemented

    def __rmul__(cls, other):
        """Synthesizes a new class by multiplying dimensions and base multipliers (reverse)."""
        return ChisaUnitMeta.__mul__(cls, other)

    def __truediv__(cls, other) -> Type['BaseUnit']:
        """Synthesizes a new class by dividing dimensions and base multipliers."""
        if isinstance(other, ChisaUnitMeta):
            new_sig = _combine_signatures(getattr(cls, '_signature', frozenset()), 
                                          getattr(other, '_signature', frozenset()), 'div')
            if getattr(other, 'base_multiplier', 0) == 0:
                raise ZeroDivisionError()
            new_mult = Decimal(str(cls.base_multiplier)) / Decimal(str(other.base_multiplier))
            new_name = f"Derived_{cls.__name__}_div_{other.__name__}"
            new_symbol = f"{getattr(cls, 'symbol', '')}/{getattr(other, 'symbol', '')}"
            return cls._create_derived_class(new_name, new_sig, new_mult, new_symbol)
            
        elif isinstance(other, (int, float, Decimal)):
            if other == 0: raise ZeroDivisionError()
            new_sig = getattr(cls, '_signature', frozenset())
            new_mult = Decimal(str(cls.base_multiplier)) / Decimal(str(other))
            new_name = f"Derived_{cls.__name__}_div_scalar"
            new_symbol = f"{getattr(cls, 'symbol', '')}/{other}"
            return cls._create_derived_class(new_name, new_sig, new_mult, new_symbol)
        return NotImplemented

    def __pow__(cls, power) -> Type['BaseUnit']:
        """Synthesizes a new class by exponentiating dimensions and base multipliers."""
        if not isinstance(power, (int, float)): return NotImplemented
        current_sig = dict(getattr(cls, '_signature', frozenset()))
        new_sig = frozenset({dim: exp * power for dim, exp in current_sig.items()}.items())
        new_mult = float(cls.base_multiplier) ** float(power)
        new_name = f"Derived_{cls.__name__}_pow_{power}"
        new_symbol = f"{getattr(cls, 'symbol', '')}^{power}"
        return cls._create_derived_class(new_name, new_sig, new_mult, new_symbol)

class BaseUnit(metaclass=ChisaUnitMeta):
    """
    The foundational core class for all physical and digital units in Chisa.
    Provides the standard interface for dimensional algebra, scalar conversions,
    NumPy vectorization, and fluent formatting.
    """
    dimension: Optional[str] = None
    symbol: Optional[str] = None
    aliases: Optional[List[str]] = None
    base_multiplier: Union[float, Decimal] = 1.0
    base_offset: Union[float, Decimal] = 0.0
    is_anonymous: bool = False

    def __init_subclass__(cls, **kwargs) -> None:
        """
        Automatically triggered when a subclass of BaseUnit is created.
        Injects the new class directly into the global UnitRegistry.
        """
        super().__init_subclass__(**kwargs)
        if not getattr(cls, 'is_anonymous', False) and getattr(cls, 'dimension', 'anonymous') != 'anonymous':
            default_ureg._register(cls)
            
            sig = getattr(cls, '_signature', None)
            if sig:
                default_ureg.inject_dna(sig, cls.dimension)

    def __init__(self, value: Union[int, float, str, Decimal, Any], context: Optional[Dict[str, Any]] = None) -> None:
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
    def exact(self) -> Union[Decimal, Any]:
        """Returns the exact raw magnitude, preserving high-precision Decimals if used."""
        return self._value

    @property
    def mag(self) -> Any:
        """Returns the magnitude safely downcasted to a standard Python float or NumPy array."""
        if HAS_NUMPY and isinstance(self._value, (np.ndarray, np.generic)):
            return self._value
            
        if isinstance(self._value, Decimal):
            return float(self._value)
            
        return self._value

    # =========================================================================
    # INTERNAL CORE LOGIC
    # =========================================================================
    def _to_base_value(self) -> Union[float, Decimal, Any]:
        if isinstance(self._value, Decimal):
            val_with_offset = self._value + Decimal(str(self.base_offset))
            return val_with_offset * Decimal(str(self.base_multiplier))
            
        val_with_offset = self._value + float(self.base_offset)
        return val_with_offset * float(self.base_multiplier)

    @classmethod
    def _from_base_value(cls, base_val: Union[float, Decimal, Any], context: Dict[str, Any]) -> Union[float, Decimal, Any]:
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

    def __array_ufunc__(self, ufunc, method, *inputs, **kwargs):
        if ufunc.__name__ not in self._ALLOWED_UFUNCS:
            raise TypeError(
                f"Chisa Dimensional Guard: Operation 'np.{ufunc.__name__}' is "
                f"blocked because it mutates physical dimensions."
            )

        raw_inputs = []
        for inp in inputs:
            if isinstance(inp, BaseUnit):
                if self.dimension != inp.dimension:
                    raise DimensionMismatchError(str(self.dimension), str(inp.dimension), f"NumPy ufunc {ufunc.__name__}")
                raw_inputs.append(inp._to_base_value())
            else:
                raw_inputs.append(inp)

        raw_result = getattr(ufunc, method)(*raw_inputs, **kwargs)
        final_value = self.__class__._from_base_value(raw_result, self.context)
        return self.__class__(final_value, context=self.context)
    
    def __array_function__(self, func, types, args, kwargs):
        if func.__name__ not in self._ALLOWED_FUNCTIONS:
            raise TypeError(
                f"Chisa Dimensional Guard: Function 'np.{func.__name__}' is "
                f"blocked to preserve dimensional integrity."
            )

        def _extract_raw(obj):
            if isinstance(obj, BaseUnit):
                return obj._to_base_value()
            if isinstance(obj, (list, tuple)):
                return [_extract_raw(o) for o in obj]
            return obj

        raw_args = tuple(_extract_raw(arg) for arg in args)
        raw_result = func(*raw_args, **kwargs)

        final_value = self.__class__._from_base_value(raw_result, self.context)
        return self.__class__(final_value, context=self.context)
    
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

    def to(self, unit: Union[Type['BaseUnit'], str]) -> 'BaseUnit':
        """
        Converts the instance to another unit within the same dimension.
        Supports both string aliases ('km') and explicit classes (u.Kilometer).
        """
        if isinstance(unit, str):
            try:
                from .registry import default_ureg 
                TargetClass = default_ureg.get_unit_class(unit, expected_dim=self.dimension)
            except Exception as e:
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
            
        base_val = self._to_base_value()
        new_val = TargetClass._from_base_value(base_val, self.context)
        return TargetClass(new_val, context=self.context)

    def format(
        self,
        prec: int = 4,
        sigfigs: Optional[int] = None,
        scinote: bool = False,
        delim: Union[bool, str] = False,
        tag: bool = True
    ) -> str:
        """Applies precise structural and numeric formatting to the magnitude."""
        val = self._value
        
        if HAS_NUMPY and isinstance(val, (np.ndarray, np.generic)):
            def format_elem(x):
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

    def __eq__(self, other: Any) -> Union[bool, Any]:
        """Evaluates equality after cross-unit normalization."""
        if not isinstance(other, BaseUnit):
            return NotImplemented
        if self.dimension != getattr(other, "dimension", None):
            raise DimensionMismatchError(str(self.dimension), str(getattr(other, 'dimension', None)), "Equality (==)")
            
        v1, v2 = self._to_base_value(), other._to_base_value()
        v1, v2 = _normalize_types(v1, v2)
            
        return v1 == v2

    def __lt__(self, other: Any) -> Union[bool, Any]:
        """Evaluates less-than after cross-unit normalization."""
        if not isinstance(other, BaseUnit):
            return NotImplemented
        if self.dimension != getattr(other, "dimension", None):
            raise DimensionMismatchError(str(self.dimension), str(getattr(other, 'dimension', None)), "Less-than (<)")
            
        v1, v2 = self._to_base_value(), other._to_base_value()
        v1, v2 = _normalize_types(v1, v2)
            
        return v1 < v2

    def __le__(self, other: Any) -> Union[bool, Any]:
        """Evaluates less-than-or-equal after cross-unit normalization."""
        if not isinstance(other, BaseUnit):
            return NotImplemented
        if self.dimension != getattr(other, "dimension", None):
            raise DimensionMismatchError(str(self.dimension), str(getattr(other, 'dimension', None)), "Less-than-or-equal (<=)")
            
        v1, v2 = self._to_base_value(), other._to_base_value()
        v1, v2 = _normalize_types(v1, v2)
            
        return v1 <= v2

    def __ge__(self, other: Any) -> Union[bool, Any]:
        """Evaluates greater-than-or-equal after cross-unit normalization."""
        if not isinstance(other, BaseUnit):
            return NotImplemented
        if self.dimension != getattr(other, "dimension", None):
            raise DimensionMismatchError(str(self.dimension), str(getattr(other, 'dimension', None)), "Greater-than-or-equal (>=)")
            
        v1, v2 = self._to_base_value(), other._to_base_value()
        v1, v2 = _normalize_types(v1, v2)
            
        return v1 >= v2

    def __ne__(self, other: Any) -> Union[bool, Any]:
        """Evaluates not-equal after cross-unit normalization."""
        if not isinstance(other, BaseUnit):
            return NotImplemented
        if self.dimension != getattr(other, "dimension", None):
            raise DimensionMismatchError(str(self.dimension), str(getattr(other, 'dimension', None)), "Not-Equal (!=)")
            
        v1, v2 = self._to_base_value(), other._to_base_value()
        v1, v2 = _normalize_types(v1, v2)
            
        return v1 != v2
    
    def __add__(self, other: Any) -> 'BaseUnit':
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

    def __sub__(self, other: Any) -> 'BaseUnit':
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
    
    def __mul__(self, other: Any) -> 'BaseUnit':
        """Permits multiplication of a unit by a scalar, array, or another unit."""
        if isinstance(other, (int, float, Decimal)) or (HAS_NUMPY and isinstance(other, (np.ndarray, np.generic))):
            new_val = self._value * other
            return self.__class__(new_val, context=self.context)
        
        if isinstance(other, BaseUnit):
            ResultClass = self.__class__ * other.__class__
            v1, v2 = _normalize_types(self._value, other._value)
            new_val = v1 * v2
            merged_context = {**self.context, **other.context}
            return ResultClass(new_val, context=merged_context)
            
        return NotImplemented

    def __rmul__(self, other: Any) -> 'BaseUnit':
        """Permits reverse scalar multiplication."""
        return self.__mul__(other)

    def __truediv__(self, other: Any) -> 'BaseUnit':
        """Permits division of a unit by a scalar, array, or another unit."""
        if isinstance(other, (int, float, Decimal)) or (HAS_NUMPY and isinstance(other, (np.ndarray, np.generic))):
            new_val = self._value / other
            return self.__class__(new_val, context=self.context)
            
        if isinstance(other, BaseUnit):
            ResultClass = self.__class__ / other.__class__
            v1, v2 = _normalize_types(self._value, other._value)
            new_val = v1 / v2
            merged_context = {**self.context, **other.context}
            return ResultClass(new_val, context=merged_context)
            
        return NotImplemented

    def __pow__(self, power: Any) -> 'BaseUnit':
        """Permits exponentiation of a unit instance."""
        if isinstance(power, (int, float)):
            ResultClass = self.__class__ ** power
            new_val = self._value ** power
            return ResultClass(new_val, context=self.context)
        return NotImplemented

    def __array__(self, dtype=None) -> Any:
        if HAS_NUMPY:
            return np.asarray(self._value, dtype=dtype)
        return np.array([self._value], dtype=dtype)