from __future__ import annotations

from math import log10, floor
from typing import Literal, Any, overload, Generic

from ..exceptions import ConversionError, AmbiguousUnitError, UnitNotFoundError
from .registry import UnitRegistry, ureg
from .compat import UnitLike, ConvertibleInput, _ReturnT, ContextDict, NumericLike, NumDtype, TYPE_CHECKING

try:
    from .base import BaseUnit
except ImportError:
    pass

try:
    import numpy as np
    HAS_NUMPY = True
except ImportError:
    HAS_NUMPY = False

if TYPE_CHECKING:
    class _UnboundBuilder(Generic[_ReturnT]):
        def to(self, unit: UnitLike) -> _BoundBuilder[_ReturnT]:
            """
            Sets the target unit for the conversion.

            Args:
                unit: The symbol, alias, or BaseUnit class of the destination unit.
                
            Returns:
                The bound builder instance to allow method chaining.
            """
            ...
            
        def context(self, ctx: ContextDict | None = None, **kwargs: Any) -> _UnboundBuilder[_ReturnT]:
            """
            Dynamically injects physical variables or environmental conditions required 
            for context-dependent dimensional conversions (e.g., temperature for Mach speed).

            Args:
                ctx: A dictionary of context variables.
                **kwargs: Arbitrary keyword arguments representing physical conditions 
                    (e.g., temperature=25, atm_pressure_pa=101325).

            Returns:
                The current builder instance to allow method chaining.
            """
            ...

        # --- SCALAR OVERLOADS ---
        @overload
        def use(self: _UnboundBuilder[float], dtype: NumDtype | None = ..., out: Literal["raw"] = ..., prec: int | None = ..., sigfigs: int | None = ..., scinote: bool | None = ..., delim: bool | str | None = ..., **kwargs: Any) -> _UnboundBuilder[float]: ...
        @overload
        def use(self: _UnboundBuilder[float], dtype: NumDtype | None = ..., out: Literal["obj"] = ..., prec: int | None = ..., sigfigs: int | None = ..., scinote: bool | None = ..., delim: bool | str | None = ..., **kwargs: Any) -> _UnboundBuilder['BaseUnit']: ...
        @overload
        def use(self: _UnboundBuilder[float], dtype: NumDtype | None = ..., out: Literal["str", "tag", "verbose"] = ..., prec: int | None = ..., sigfigs: int | None = ..., scinote: bool | None = ..., delim: bool | str | None = ..., **kwargs: Any) -> _UnboundBuilder[str]: ...
        @overload
        def use(self: _UnboundBuilder[float], dtype: NumDtype | None = ..., out: None = ..., prec: int | None = ..., sigfigs: int | None = ..., scinote: bool | None = ..., delim: bool | str | None = ..., **kwargs: Any) -> _UnboundBuilder[float]: ...

        # --- NDARRAY OVERLOADS ---
        @overload
        def use(self: _UnboundBuilder['np.ndarray'], dtype: NumDtype | None = ..., out: Literal["obj"] = ..., prec: int | None = ..., sigfigs: int | None = ..., scinote: bool | None = ..., delim: bool | str | None = ..., **kwargs: Any) -> _UnboundBuilder['np.ndarray']: ...
        @overload
        def use(self: _UnboundBuilder['np.ndarray'], dtype: NumDtype | None = ..., out: Literal["str", "tag", "verbose"] = ..., prec: int | None = ..., sigfigs: int | None = ..., scinote: bool | None = ..., delim: bool | str | None = ..., **kwargs: Any) -> _UnboundBuilder['np.ndarray']: ...
        @overload
        def use(self: _UnboundBuilder['np.ndarray'], dtype: NumDtype | None = ..., out: Literal["raw"] = ..., prec: int | None = ..., sigfigs: int | None = ..., scinote: bool | None = ..., delim: bool | str | None = ..., **kwargs: Any) -> _UnboundBuilder['np.ndarray']: ...
        @overload
        def use(self: _UnboundBuilder['np.ndarray'], dtype: NumDtype | None = ..., out: None = ..., prec: int | None = ..., sigfigs: int | None = ..., scinote: bool | None = ..., delim: bool | str | None = ..., **kwargs: Any) -> _UnboundBuilder['np.ndarray']: ...

        def use(self, **kwargs: Any) -> _UnboundBuilder[Any]:
            """
            Configures the calculation engine, output structure, and precision.

            Args:
                dtype: NumPy engine dtype ('float64', 'float32', etc.).
                out: Return type structure ('raw', 'obj', 'str', 'tag', 'verbose').
                prec: Decimal places precision.
                sigfigs: Significant figures precision.
                scinote: Format output in scientific notation.
                delim: Adds thousands separators.

            Returns:
                The current builder instance to allow method chaining.
            """
            ...

    class _BoundBuilder(Generic[_ReturnT]):
        def to(self, unit: UnitLike) -> _BoundBuilder[_ReturnT]:
            """Sets the target unit for the conversion."""
            ...
            
        def context(self, ctx: ContextDict | None = None, **kwargs: Any) -> _BoundBuilder[_ReturnT]:
            """
            Dynamically injects physical variables or environmental conditions required 
            for context-dependent dimensional conversions (e.g., temperature for Mach speed).

            Args:
                ctx: A dictionary of context variables.
                **kwargs: Arbitrary keyword arguments representing physical conditions 
                    (e.g., temperature=25, atm_pressure_pa=101325).

            Returns:
                The current builder instance to allow method chaining.
            """
            ...

        # --- SCALAR OVERLOADS ---
        @overload
        def use(self: _BoundBuilder[float], dtype: NumDtype | None = ..., out: Literal["raw"] = ..., prec: int | None = ..., sigfigs: int | None = ..., scinote: bool | None = ..., delim: bool | str | None = ..., **kwargs: Any) -> _BoundBuilder[float]: ...
        @overload
        def use(self: _BoundBuilder[float], dtype: NumDtype | None = ..., out: Literal["obj"] = ..., prec: int | None = ..., sigfigs: int | None = ..., scinote: bool | None = ..., delim: bool | str | None = ..., **kwargs: Any) -> _BoundBuilder['BaseUnit']: ...
        @overload
        def use(self: _BoundBuilder[float], dtype: NumDtype | None = ..., out: Literal["str", "tag", "verbose"] = ..., prec: int | None = ..., sigfigs: int | None = ..., scinote: bool | None = ..., delim: bool | str | None = ..., **kwargs: Any) -> _BoundBuilder[str]: ...
        @overload
        def use(self: _BoundBuilder[float], dtype: NumDtype | None = ..., out: None = ..., prec: int | None = ..., sigfigs: int | None = ..., scinote: bool | None = ..., delim: bool | str | None = ..., **kwargs: Any) -> _BoundBuilder[float]: ...

        # --- NDARRAY OVERLOADS ---
        @overload
        def use(self: _BoundBuilder['np.ndarray'], dtype: NumDtype | None = ..., out: Literal["obj"] = ..., prec: int | None = ..., sigfigs: int | None = ..., scinote: bool | None = ..., delim: bool | str | None = ..., **kwargs: Any) -> _BoundBuilder['np.ndarray']: ...
        @overload
        def use(self: _BoundBuilder['np.ndarray'], dtype: NumDtype | None = ..., out: Literal["str", "tag", "verbose"] = ..., prec: int | None = ..., sigfigs: int | None = ..., scinote: bool | None = ..., delim: bool | str | None = ..., **kwargs: Any) -> _BoundBuilder['np.ndarray']: ...
        @overload
        def use(self: _BoundBuilder['np.ndarray'], dtype: NumDtype | None = ..., out: Literal["raw"] = ..., prec: int | None = ..., sigfigs: int | None = ..., scinote: bool | None = ..., delim: bool | str | None = ..., **kwargs: Any) -> _BoundBuilder['np.ndarray']: ...
        @overload
        def use(self: _BoundBuilder['np.ndarray'], dtype: NumDtype | None = ..., out: None = ..., prec: int | None = ..., sigfigs: int | None = ..., scinote: bool | None = ..., delim: bool | str | None = ..., **kwargs: Any) -> _BoundBuilder['np.ndarray']: ...

        def use(self, **kwargs: Any) -> _BoundBuilder[Any]:
            """Configures the calculation engine, output structure, and precision."""
            ...

        def resolve(self) -> _ReturnT:
            """
            Executes the conversion pipeline and finalizes the output.
            
            Returns:
                The final converted magnitude, vectorized array, formatted string, 
                or BaseUnit instance depending on the applied configuration.
                
            Raises:
                ConversionError: 
                    - If the target unit was not defined prior to resolution.
                    - If an invalid NumPy dtype or precision is requested.
                    - If there is a physical dimension mismatch
                AmbiguousUnitError: If the provided unit alias (e.g., 'm') matches multiple physical 
                  dimensions and cannot be resolved from context.
                UnitNotFoundError: If the source or target unit alias is not recognized by the Registry.
            """
            ...
            
        def flex(self, range: tuple[str | None, str | None] = (None, None), delim: bool | str = True) -> str:
            """
            Deconstructs the total time duration into a natural language format.
            Exclusive to units within the time dimension.
            
            Args:
                range: A tuple defining the upper and lower bounds for the output units (e.g., ('year', 'day')).
                delim: The separator string to use between time segments, or a boolean to use defaults.

            Returns:
                The human-readable formatted time string.
                
            Raises:
                ConversionError: If applied to a non-time dimension or a NumPy array.
            """
            ...

class _ConversionBuilder(Generic[_ReturnT]):
    def __init__(self, value: ConvertibleInput, source_unit: UnitLike) -> None:
        self.raw_value = value
        self.source_unit = source_unit
        self._registry = ureg()
        self._target_unit: str | Any | None = None 
        
        self._options: dict[str, Any] = {
            "dtype": "float64",
            "prec": None,
            "output": "raw", 
            "sigfigs": None,
            "scinote": False,
            "delim": False
        }

        self._context: dict[str, Any] = {}
        self._is_single_unit = False
        self._is_unit_list = False
        
        if hasattr(value, 'dimension') and hasattr(value, 'mag'):
            self._is_single_unit = True
            self.is_array = False
            self._internal_val = value
            return
            
        if HAS_NUMPY and isinstance(value, np.ndarray) and value.size > 0:
            if hasattr(value.flat[0], 'dimension') and hasattr(value.flat[0], 'mag'):
                self._is_unit_list = True
                self.is_array = True
                self._internal_val = value
                return
                
        if isinstance(value, (list, tuple, set)) and len(value) > 0:
            first_elem = next(iter(value))
            if hasattr(first_elem, 'dimension') and hasattr(first_elem, 'mag'):
                self._is_unit_list = True
                self.is_array = False
                self._internal_val = value
                return
                
        if source_unit is None:
            raise TypeError("source_unit must be provided if value is a raw number or array.")
            
        if HAS_NUMPY and isinstance(value, (np.ndarray, np.generic, list, tuple)):
            self._internal_val = value if isinstance(value, (np.ndarray, np.generic)) else np.array(value, dtype=np.float64)
            self.is_array = True
        else:
            self.is_array = False
            try:
                self._internal_val = float(value) # type: ignore
            except (TypeError, ValueError):
                raise TypeError(f"Invalid input: '{value}' cannot be converted to a numeric type.")
            
    def to(self, unit: UnitLike) -> _ConversionBuilder[_ReturnT]:
        self._target_unit = unit
        return self

    
    # --- SCALAR OVERLOADS ---
    @overload
    def use(self: _ConversionBuilder[float], dtype: NumDtype | None = ..., out: Literal["obj"] = ..., prec: int | None = ..., sigfigs: int | None = ..., scinote: bool | None = ..., delim: bool | str | None = ..., **kwargs: Any) -> _ConversionBuilder['BaseUnit']: ...

    @overload
    def use(self: _ConversionBuilder[float], dtype: NumDtype | None = ..., out: Literal["str", "tag", "verbose"] = ..., prec: int | None = ..., sigfigs: int | None = ..., scinote: bool | None = ..., delim: bool | str | None = ..., **kwargs: Any) -> _ConversionBuilder[str]: ...

    @overload
    def use(self: _ConversionBuilder[float], dtype: NumDtype | None = ..., out: Literal["raw"] = ..., prec: int | None = ..., sigfigs: int | None = ..., scinote: bool | None = ..., delim: bool | str | None = ..., **kwargs: Any) -> _ConversionBuilder[float]: ...

    @overload
    def use(self: _ConversionBuilder[float], dtype: NumDtype | None = ..., out: None = ..., prec: int | None = ..., sigfigs: int | None = ..., scinote: bool | None = ..., delim: bool | str | None = ..., **kwargs: Any) -> _ConversionBuilder[float]: ...

    # --- LIST OVERLOADS ---
    @overload
    def use(self: _ConversionBuilder[list[float]], dtype: NumDtype | None = ..., out: Literal["obj"] = ..., prec: int | None = ..., sigfigs: int | None = ..., scinote: bool | None = ..., delim: bool | str | None = ..., **kwargs: Any) -> _ConversionBuilder[list['BaseUnit']]: ...

    @overload
    def use(self: _ConversionBuilder[list[float]], dtype: NumDtype | None = ..., out: Literal["str", "tag", "verbose"] = ..., prec: int | None = ..., sigfigs: int | None = ..., scinote: bool | None = ..., delim: bool | str | None = ..., **kwargs: Any) -> _ConversionBuilder[list[str]]: ...

    @overload
    def use(self: _ConversionBuilder[list[float]], dtype: NumDtype | None = ..., out: Literal["raw"] = ..., prec: int | None = ..., sigfigs: int | None = ..., scinote: bool | None = ..., delim: bool | str | None = ..., **kwargs: Any) -> _ConversionBuilder[list[float]]: ...

    @overload
    def use(self: _ConversionBuilder[list[float]], dtype: NumDtype | None = ..., out: None = ..., prec: int | None = ..., sigfigs: int | None = ..., scinote: bool | None = ..., delim: bool | str | None = ..., **kwargs: Any) -> _ConversionBuilder[list[float]]: ...

    # --- NDARRAY OVERLOADS ---
    @overload
    def use(self: _ConversionBuilder['np.ndarray'], dtype: NumDtype | None = ..., out: Literal["obj"] = ..., prec: int | None = ..., sigfigs: int | None = ..., scinote: bool | None = ..., delim: bool | str | None = ..., **kwargs: Any) -> _ConversionBuilder['np.ndarray']: ...

    @overload
    def use(self: _ConversionBuilder['np.ndarray'], dtype: NumDtype | None = ..., out: Literal["str", "tag", "verbose"] = ..., prec: int | None = ..., sigfigs: int | None = ..., scinote: bool | None = ..., delim: bool | str | None = ..., **kwargs: Any) -> _ConversionBuilder['np.ndarray']: ...

    @overload
    def use(self: _ConversionBuilder['np.ndarray'], dtype: NumDtype | None = ..., out: Literal["raw"] = ..., prec: int | None = ..., sigfigs: int | None = ..., scinote: bool | None = ..., delim: bool | str | None = ..., **kwargs: Any) -> _ConversionBuilder['np.ndarray']: ...

    @overload
    def use(self: _ConversionBuilder['np.ndarray'], dtype: NumDtype | None = ..., out: None = ..., prec: int | None = ..., sigfigs: int | None = ..., scinote: bool | None = ..., delim: bool | str | None = ..., **kwargs: Any) -> _ConversionBuilder['np.ndarray']: ...

    def use(
        self, 
        dtype: NumDtype | None = None, 
        out: Literal["raw", "str", "obj", "tag", "verbose"] | None = None, 
        prec: int | None = None, 
        sigfigs: int | None = None, 
        scinote: bool | None = None, 
        delim: bool | str | None = None, 
        **kwargs: Any
    ) -> _ConversionBuilder[Any]:
        if dtype is not None: self._options["dtype"] = dtype
        if out is not None: self._options["output"] = out
        if prec is not None: self._options["prec"] = prec
        if sigfigs is not None: self._options["sigfigs"] = sigfigs
        if scinote is not None: self._options["scinote"] = scinote
        if delim is not None: self._options["delim"] = delim

        aliases_map = {
            'dtype': ['mode', 'type', 'engine'],
            'prec': ['precision'],
            'delim': ['delimiter'],
            'sigfigs': ['significant_figures'],
            'scinote': ['scientific_notation', 'sci_note'],
            'output': ['fmt', 'format', 'out']
        }
        for main_key, aliases in aliases_map.items():
            for alias in aliases:
                if alias in kwargs:
                    self._options[main_key] = kwargs[alias]
                    
        return self

    def context(self, ctx: ContextDict | None = None, **kwargs: NumericLike | 'BaseUnit') -> _ConversionBuilder[_ReturnT]:
        if ctx is not None:
            self._context.update(ctx)
        if kwargs:
            self._context.update(kwargs)
        return self

    def _round_sigfigs(self, num: float, sigfigs: int) -> float:
        if num == 0.0: return 0.0
        return round(num, -int(floor(log10(abs(num)))) + (sigfigs - 1))

    def _compute(self) -> float | Any:
        """Executes the dimensional algebra and returns the raw scalar/vector."""
        if not self._target_unit:
            raise ConversionError("Target unit missing. You must call .to('unit') before computing.")

        SourceClass = self.source_unit if hasattr(self.source_unit, 'dimension') else None
        TargetClass = self._target_unit if hasattr(self._target_unit, 'dimension') else None

        expected_dimension = getattr(SourceClass, 'dimension', None) or getattr(TargetClass, 'dimension', None)

        if expected_dimension is None:
            target_ambiguous = source_ambiguous = False
            try:
                TargetClass = self._registry.get_unit_class(self._target_unit)
                expected_dimension = TargetClass.dimension
            except AmbiguousUnitError: target_ambiguous = True
            except UnitNotFoundError: pass
                
            if expected_dimension is None:
                try:
                    SourceClass = self._registry.get_unit_class(self.source_unit)
                    expected_dimension = SourceClass.dimension
                except AmbiguousUnitError: source_ambiguous = True
                except UnitNotFoundError: pass

            if expected_dimension is None:
                if target_ambiguous and source_ambiguous: self._registry.get_unit_class(self.source_unit)
                elif source_ambiguous: self._registry.get_unit_class(self.source_unit)
                elif target_ambiguous: self._registry.get_unit_class(self._target_unit)
                else: raise ConversionError(f"Cannot resolve dimension for conversion from '{self.source_unit}' to '{self._target_unit}'.")

        if SourceClass is None: SourceClass = self._registry.get_unit_class(self.source_unit, expected_dim=expected_dimension)
        if TargetClass is None: TargetClass = self._registry.get_unit_class(self._target_unit, expected_dim=expected_dimension)

        if getattr(TargetClass, 'dimension', None) != getattr(SourceClass, 'dimension', None):
            raise ConversionError(f"Dimension mismatch! Expected '{getattr(SourceClass, 'dimension', None)}', got '{getattr(TargetClass, 'dimension', None)}'")

        self._src_symbol = getattr(SourceClass, 'symbol', getattr(SourceClass, '__name__', str(self.source_unit)))
        self._tgt_symbol = getattr(TargetClass, 'symbol', getattr(TargetClass, '__name__', str(self._target_unit)))
        
        self._resolved_target_class = TargetClass

        source_obj = SourceClass(self._internal_val, context=self._context)
        target_obj = source_obj.to(TargetClass)
        
        converted_value = target_obj.mag
        
        req_dtype = str(self._options.get("dtype", "float64")).lower().strip()
        prec = self._options["prec"]
        sigfigs = self._options["sigfigs"]

        if HAS_NUMPY and isinstance(converted_value, (np.ndarray, np.generic)):
            if prec is not None: converted_value = np.round(converted_value, prec)
            
            if req_dtype != "float64":
                try:
                    converted_value = converted_value.astype(getattr(np, req_dtype))
                except AttributeError:
                    raise ConversionError(f"Invalid NumPy dtype requested: '{req_dtype}'")
        else:
            if prec is not None: converted_value = round(converted_value, prec)
            
            if HAS_NUMPY and req_dtype != "float64":
                try:
                    converted_value = getattr(np, req_dtype)(converted_value).item()
                except AttributeError:
                    raise ConversionError(f"Invalid NumPy dtype requested: '{req_dtype}'")
            elif "int" in req_dtype:
                converted_value = int(converted_value)

        if sigfigs:
            try:
                sigfigs = int(sigfigs)
                if sigfigs <= 0: raise ValueError()
            except Exception:
                raise ConversionError("Significant figures (sigfigs) must be a positive integer!")
            
            if not (HAS_NUMPY and isinstance(converted_value, (np.ndarray, np.generic))):
                converted_value = self._round_sigfigs(float(converted_value), sigfigs)

        return converted_value
    
    def resolve(self) -> _ReturnT:
        if not self._target_unit:
            raise ConversionError(
                "Attempted to resolve an unbound conversion pipeline. "
                "You must call .to('target_unit') to bind the dimensions before resolution."
            )

        output_fmt = str(self._options.get("output", "raw")).lower().strip()
        
        fmt_kwargs = {
            "sigfigs": self._options.get("sigfigs"),
            "scinote": self._options.get("scinote", False),
            "delim": self._options.get("delim", False),
            "tag": (output_fmt in ("tag", "str", "verbose"))
        }
        if self._options.get("prec") is not None:
            fmt_kwargs["prec"] = self._options.get("prec")

        if getattr(self, '_is_single_unit', False):
            expected_dim = getattr(self.raw_value, 'dimension', None)
            TargetClass = self._target_unit if hasattr(self._target_unit, 'dimension') else self._registry.get_unit_class(str(self._target_unit), expected_dim=expected_dim)
            
            converted_obj = self.raw_value.to(TargetClass)
            
            if output_fmt == "obj": return converted_obj
            if output_fmt in ("raw", "exact"): return converted_obj.mag
            
            tgt_str = converted_obj.format(**fmt_kwargs)
            if output_fmt == "verbose":
                src_str = self.raw_value.format(**fmt_kwargs)
                return f"{src_str} = {tgt_str}"
            return tgt_str

        if getattr(self, '_is_unit_list', False):
            results = []
            iterable_val = self.raw_value.flatten() if (HAS_NUMPY and isinstance(self.raw_value, np.ndarray)) else self.raw_value
            
            first_item = next(iter(iterable_val)) if len(iterable_val) > 0 else None # type: ignore
            expected_dim = getattr(first_item, 'dimension', None)
            TargetClass = self._target_unit if hasattr(self._target_unit, 'dimension') else self._registry.get_unit_class(str(self._target_unit), expected_dim=expected_dim)

            for item in iterable_val: # type: ignore
                converted_obj = item.to(TargetClass)
                
                if output_fmt == "obj":
                    results.append(converted_obj)
                elif output_fmt in ("raw", "exact"):
                    results.append(converted_obj.mag)
                else:
                    tgt_str = converted_obj.format(**fmt_kwargs)
                    if output_fmt == "verbose":
                        src_str = item.format(**fmt_kwargs)
                        results.append(f"{src_str} = {tgt_str}")
                    else:
                        results.append(tgt_str)
                    
            if HAS_NUMPY and isinstance(self.raw_value, np.ndarray):
                return np.array(results, dtype=object).reshape(self.raw_value.shape)
            return results

        final_val = self._compute()
        TargetClass = self._resolved_target_class
        
        if output_fmt == "obj": return TargetClass(final_val, context=self._context)
        
        if output_fmt in ("str", "tag", "verbose"):
            src_name = getattr(self, '_src_symbol', str(self.source_unit))
            tgt_name = getattr(self, '_tgt_symbol', str(self._target_unit))
            
            scinote = self._options.get("scinote", False)
            delim = self._options.get("delim", False)
            sigfigs = self._options.get("sigfigs")
            prec = self._options.get("prec")

            if HAS_NUMPY and isinstance(final_val, (np.ndarray, np.generic)):
                def format_elem(x: Any) -> str:
                    xf = float(x)
                    if scinote:
                        digits = sigfigs - 1 if sigfigs is not None else (prec or 4)
                        return f"{xf:.{digits}E}"
                    s = f"{xf:.{prec or 4}f}" if sigfigs is None else f"{xf:.{sigfigs}g}"
                    if '.' in s and 'e' not in s.lower():
                        s = s.rstrip('0')
                        if s.endswith('.'): s += '0'
                    if delim:
                        separator = "," if delim is True or str(delim).lower() == "default" else str(delim)
                        parts = s.split('.')
                        parts[0] = f"{int(parts[0]):,}".replace(",", separator)
                        s = '.'.join(parts) if len(parts) > 1 else parts[0]
                    return s

                val_str = np.array2string(
                    final_val, 
                    formatter={'float_kind': format_elem, 'int': format_elem},
                    separator=', ',
                    suppress_small=not scinote 
                )
                
                if output_fmt == "verbose":
                    raw_str = np.array2string(
                        np.asarray(self.raw_value), 
                        formatter={'float_kind': format_elem, 'int': format_elem},
                        separator=', ', suppress_small=not scinote
                    )
                    return f"{raw_str} {src_name} = {val_str} {tgt_name}"
                
                if output_fmt == "tag": return f"{val_str} {tgt_name}"
                return val_str

            xf = float(final_val)
            if scinote:
                digits = sigfigs - 1 if sigfigs is not None else (prec or 4)
                val_str = f"{xf:.{digits}E}"
            else:
                val_str = f"{xf:.{prec or 4}f}" if sigfigs is None else f"{xf:.{sigfigs}g}"

            if not scinote and '.' in val_str and 'e' not in val_str.lower():
                val_str = val_str.rstrip('0')
                if val_str.endswith('.'): val_str += '0'

            if delim:
                separator = "," if delim is True or str(delim).lower() == "default" else str(delim)
                if not scinote and 'e' not in val_str.lower():
                    parts = val_str.split('.')
                    parts[0] = f"{int(parts[0]):,}".replace(",", separator)
                    val_str = '.'.join(parts) if len(parts) > 1 else parts[0]
                
                raw_str = str(self.raw_value)
                if '.' in raw_str:
                    raw_parts = raw_str.split('.')
                    raw_parts[0] = f"{int(raw_parts[0]):,}".replace(",", separator)
                    raw_str_formatted = '.'.join(raw_parts)
                else:
                    try: raw_str_formatted = f"{int(self.raw_value):,}".replace(",", separator)
                    except ValueError: raw_str_formatted = str(self.raw_value)
            else:
                raw_str_formatted = str(self.raw_value)

            if output_fmt == "verbose": return f"{raw_str_formatted} {src_name} = {val_str} {tgt_name}"
            if output_fmt == "tag": return f"{val_str} {tgt_name}"
                
            return val_str

        return final_val

    def flex(self, range: tuple[str | None, str | None] = (None, None), delim: bool | str = True) -> str:
        if self.is_array: raise ConversionError(".flex() method cannot be applied to NumPy arrays.")
        SourceClass = self._registry.get_unit_class(self.source_unit) if isinstance(self.source_unit, str) else self.source_unit
        source_obj = SourceClass(self._internal_val, context=self._context)

        if not hasattr(source_obj, 'flex'):
            raise ConversionError(f"Unit '{getattr(SourceClass, 'symbol', self.source_unit)}' does not support the .flex() method.")
        return source_obj.flex(range=range, delim=delim) # type: ignore
    
    def __str__(self) -> str:
        if not self._target_unit:
            src_name = getattr(self.source_unit, 'symbol', getattr(self.source_unit, '__name__', str(self.source_unit)))
            return f"<Phaethon Pending: {self._internal_val} {src_name} -> Call .to()>"
        return str(self.resolve())

    def __repr__(self) -> str:
        target = getattr(self._target_unit, 'symbol', getattr(self._target_unit, '__name__', str(self._target_unit))) if self._target_unit else "???"
        src = getattr(self.source_unit, 'symbol', getattr(self.source_unit, '__name__', str(self.source_unit)))
        return f"<_ConversionBuilder: {self._internal_val} {src} -> {target}>"


class _FluentOrchestrator:
    def __init__(self, registry: UnitRegistry) -> None:
        self._registry = registry

    def convert(self, value: ConvertibleInput, unit: UnitLike) -> _ConversionBuilder:
        return _ConversionBuilder(value, unit)
    
_def_orchestrator = _FluentOrchestrator(registry=ureg())

@overload
def convert(value: 'BaseUnit') -> _UnboundBuilder[float]: ...

@overload
def convert(value: list[Any] | tuple[Any, ...] | set[Any]) -> _UnboundBuilder['np.ndarray']: ...

@overload
def convert(value: int | float | str, unit: UnitLike) -> _UnboundBuilder[float]: ...

@overload
def convert(value: list[Any] | tuple[Any, ...] | set[Any], unit: UnitLike) -> _UnboundBuilder['np.ndarray']: ...

@overload
def convert(value: 'np.ndarray', unit: UnitLike | None = ...) -> _UnboundBuilder['np.ndarray']: ...

def convert(value: Any, unit: Any = None) -> _UnboundBuilder[Any]:
    """
    Initializes a stateful, fluent conversion pipeline for physical and digital units.

    This method serves as the primary entry point for the Phaethon ecosystem, 
    constructing a 'Dimension-Aware' bridge between raw numerical data and 
    rigorous physical algebra. 

    The resulting pipeline is typestate-enforced: it remains 'Unbound' (locked) 
    until a target unit is specified via `.to()`, ensuring dimensional integrity 
    before any computation occurs.

    Args:
        value: The numerical magnitude (scalar, list, or NumPy array) to be 
               converted, or a collection of instantiated Phaethon BaseUnits.
        unit: The source unit class or string alias. Optional only if 'value' 
              is already an instantiated Phaethon unit/collection.

    Returns:
        _UnboundBuilder: A pending pipeline that unlocks terminal execution 
        methods (like `.resolve()`) only after a target unit is bound via `.to()`.

    Examples:
        >>> # Standard Conversion
        >>> ptn.convert(10, 'm').to('km').resolve()
        0.01

        >>> # Vectorized Conversion with Formatting
        >>> ptn.convert([1, 2], u.Meter).to(u.Centimeter).use(out='tag').resolve()
        ['100.0 cm', '200.0 cm']

        >>> # This will raise a ConversionError at runtime if .to() is omitted.
        >>> ptn.convert(10, 'kg').resolve()
        ConversionError: Unable to resolve...
    """
    return _def_orchestrator.convert(value, unit)