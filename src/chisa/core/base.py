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


class BaseUnit:
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

    def __init_subclass__(cls, **kwargs) -> None:
        """
        Automatically triggered when a subclass of BaseUnit is created.
        Injects the new class directly into the global UnitRegistry.
        """
        super().__init_subclass__(**kwargs)
        default_ureg._register(cls)

    def __init__(self, value: Union[int, float, str, Decimal, Any], context: Optional[Dict[str, Any]] = None) -> None:
        """
        A unit object, handling both scalar and vectorized inputs.

        Args:
            value (Union[int, float, str, Decimal, Any]): The magnitude of the unit. 
                Accepts pure scalars, lists, tuples, or NumPy arrays.
            context (Optional[Dict[str, Any]]): Contextual physical properties 
                required for dynamic scaling (e.g., {'temp_c': 30}).
                
        Raises:
            TypeError: If the input value is not a recognized numeric or iterable type.
        """
        if HAS_NUMPY and isinstance(value, (np.ndarray, np.generic)):
            self._value = value
        elif HAS_NUMPY and isinstance(value, (list, tuple)):
            self._value = np.array(value, dtype=float)
        elif isinstance(value, (int, float, str, Decimal)):
            self._value = Decimal(str(value))
        else:
            raise TypeError(f"Value must be numeric or array, got {type(value).__name__}")
            
        self.context = context or {}

    # =========================================================================
    # PUBLIC PROPERTIES (THE DX INTERFACE)
    # =========================================================================
    @property
    def exact(self) -> Union[Decimal, Any]:
        """
        Returns the exact, unadulterated internal representation of the unit.
        
        - For scalars: Returns a `decimal.Decimal` to preserve absolute mathematical 
          precision (avoiding floating-point drift).
        - For vectors: Returns the original `numpy.ndarray`.
        
        WARNING: Do not mix `.exact` scalar outputs with external NumPy arrays 
        in manual calculations, as Python forbids multiplying Decimals with floats/arrays. 
        Use `.magnitude` instead for general cross-dimensional math.
        """
        return self._value

    @property
    def mag(self) -> Any:
        """
        Returns the numeric magnitude as a standard, math-safe Python primitive.
        
        - For scalars: Automatically casts internal Decimals down to standard `float` or `int`.
        - For vectors: Returns the `numpy.ndarray` intact.
        
        Always use `.magnitude` when extracting values to perform 
        external physics calculations, plotting (Matplotlib), or machine learning.
        """
        if HAS_NUMPY and isinstance(self._value, (np.ndarray, np.generic)):
            return self._value
            
        if isinstance(self._value, Decimal) and self._value == int(self._value):
            return int(self._value)
            
        return float(self._value)

    # =========================================================================
    # INTERNAL CORE LOGIC
    # =========================================================================
    def _to_base_value(self) -> Union[Decimal, Any]:
        """Converts the current magnitude to the dimension's absolute base point."""
        if HAS_NUMPY and isinstance(self._value, (np.ndarray, np.generic)):
            val_with_offset = self._value + float(self.base_offset)
            return val_with_offset * float(self.base_multiplier)
        
        val_with_offset = self._value + Decimal(str(self.base_offset))
        return val_with_offset * Decimal(str(self.base_multiplier))

    @classmethod
    def _from_base_value(cls, base_val: Union[Decimal, Any], context: Dict[str, Any]) -> Union[Decimal, Any]:
        """Converts a magnitude from the dimension's absolute base point to this specific unit."""
        if HAS_NUMPY and isinstance(base_val, (np.ndarray, np.generic, float)):
            val = base_val / float(cls.base_multiplier)
            return val - float(cls.base_offset)
            
        val = base_val / Decimal(str(cls.base_multiplier))
        return val - Decimal(str(cls.base_offset))

    # Whitelisted NumPy Operations
    _ALLOWED_UFUNCS = {
        'add', 'subtract', 'maximum', 'minimum', 'fmax', 'fmin', 
        'absolute', 'negative', 'positive', 'rint'
    }
    
    _ALLOWED_FUNCTIONS = {
        'sum', 'max', 'min', 'mean', 'median', 'std', 'round', 'ptp'
    }

    def __array_ufunc__(self, ufunc, method, *inputs, **kwargs):
        """Portal for low-level element-wise operations (e.g., np.add)."""
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
        """Portal for high-level reduction/statistical operations (e.g., np.mean, np.max)."""
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
        Converts the current OOP unit object into another unit within the same dimension.
        Elegantly resolves string aliases via the global registry.

        Args:
            unit: The target destination class or string alias.

        Returns:
            A new instance of the target unit class maintaining the original context.
            
        Raises:
            TypeError: If the target is not a valid Chisa BaseUnit or recognized string.
            DimensionMismatchError: If the target belongs to a different physical dimension.
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
        """
        Formats the object's scalar value into a structured, human-readable string.
        Safely applies string manipulation for vectorized NumPy arrays.

        Args:
            prec: Number of decimal places to display. Defaults to 4.
            sigfigs: Number of significant figures to enforce.
            scinote: If True, forces scientific notation (e.g., 1.5E3).
            delim: If True, applies thousands separators. Can be a custom string character.
            tag: If True, appends the unit's symbol to the end of the string.

        Returns:
            str: The formatted cosmetic string representing the unit.
        """
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
            val_str = val_str.rstrip('0').rstrip('.')

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
        if not isinstance(other, BaseUnit):
            return NotImplemented
        if self.dimension != getattr(other, "dimension", None):
            raise DimensionMismatchError(str(self.dimension), str(getattr(other, 'dimension', None)), "Equality (==)")
            
        v1, v2 = self._to_base_value(), other._to_base_value()
        v1, v2 = _normalize_types(v1, v2)
            
        return v1 == v2

    def __lt__(self, other: Any) -> Union[bool, Any]:
        if not isinstance(other, BaseUnit):
            return NotImplemented
        if self.dimension != getattr(other, "dimension", None):
            raise DimensionMismatchError(str(self.dimension), str(getattr(other, 'dimension', None)), "Less-than (<)")
            
        v1, v2 = self._to_base_value(), other._to_base_value()
        v1, v2 = _normalize_types(v1, v2)
            
        return v1 < v2

    def __le__(self, other: Any) -> Union[bool, Any]:
        if not isinstance(other, BaseUnit):
            return NotImplemented
        if self.dimension != getattr(other, "dimension", None):
            raise DimensionMismatchError(str(self.dimension), str(getattr(other, 'dimension', None)), "Less-than-or-equal (<=)")
            
        v1, v2 = self._to_base_value(), other._to_base_value()
        v1, v2 = _normalize_types(v1, v2)
            
        return v1 <= v2

    def __ge__(self, other: Any) -> Union[bool, Any]:
        if not isinstance(other, BaseUnit):
            return NotImplemented
        if self.dimension != getattr(other, "dimension", None):
            raise DimensionMismatchError(str(self.dimension), str(getattr(other, 'dimension', None)), "Greater-than-or-equal (>=)")
            
        v1, v2 = self._to_base_value(), other._to_base_value()
        v1, v2 = _normalize_types(v1, v2)
            
        return v1 >= v2

    def __ne__(self, other: Any) -> Union[bool, Any]:
        if not isinstance(other, BaseUnit):
            return NotImplemented
        if self.dimension != getattr(other, "dimension", None):
            raise DimensionMismatchError(str(self.dimension), str(getattr(other, 'dimension', None)), "Not-Equal (!=)")
            
        v1, v2 = self._to_base_value(), other._to_base_value()
        v1, v2 = _normalize_types(v1, v2)
            
        return v1 != v2
    
    def __add__(self, other: Any) -> 'BaseUnit':
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
        """Permits multiplication of a unit strictly by a pure scalar or array."""
        if isinstance(other, (int, float, Decimal)) or (HAS_NUMPY and isinstance(other, (np.ndarray, np.generic))):
            new_val = self._value * other
            return self.__class__(new_val, context=self.context)
        
        if isinstance(other, BaseUnit):
            raise NotImplementedError(
                "Cross-dimensional multiplication (e.g., Meter * Meter) is restricted "
                "in this version to preserve dimensional integrity."
            )
        return NotImplemented

    def __rmul__(self, other: Any) -> 'BaseUnit':
        """Supports reverse scalar multiplication (e.g., 3 * Meter(5))."""
        return self.__mul__(other)

    def __truediv__(self, other: Any) -> 'BaseUnit':
        """Permits division of a unit strictly by a pure scalar or array."""
        if isinstance(other, (int, float, Decimal)) or (HAS_NUMPY and isinstance(other, (np.ndarray, np.generic))):
            new_val = self._value / other
            return self.__class__(new_val, context=self.context)
            
        if isinstance(other, BaseUnit):
            raise NotImplementedError(
                "Cross-dimensional division (e.g., Meter / Second) is restricted "
                "in this version to preserve dimensional integrity."
            )
        return NotImplemented

    def __array__(self, dtype=None) -> Any:
        """
        NumPy standard dunder method to expose the raw array.
        Allows Chisa objects to be natively ingested by Matplotlib, Scikit-Learn, pandas, or SymPy.
        """
        if HAS_NUMPY:
            return np.asarray(self._value, dtype=dtype)
        return np.array([self._value], dtype=dtype)