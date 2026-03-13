from __future__ import annotations

from decimal import Decimal, getcontext, ROUND_HALF_UP, ROUND_HALF_EVEN, InvalidOperation
from typing import Literal, Any, overload, Generic
from math import log10, floor

from ..exceptions import ConversionError, AmbiguousUnitError, UnitNotFoundError
from .registry import UnitRegistry, ureg
from .compat import UnitLike, ConvertibleInput, _T_Out, ContextDict, NumericLike

try:
    from .base import BaseUnit
except ImportError:
    pass

try:
    import numpy as np
    HAS_NUMPY = True
except ImportError:
    HAS_NUMPY = False


class _ConversionBuilder(Generic[_T_Out]):
    """
    A private builder class that handles the fluent API chaining for unit conversions.
    It lazily stores the state, options, and context until the conversion is resolved.
    """
    def __init__(self, value: ConvertibleInput, source_unit: UnitLike) -> None:
        """
        Initializes the conversion builder.

        Args:
            value: The magnitude to be converted (scalar, list, or NumPy array).
            source_unit: The source unit class or string alias.
            registry: The global unit registry instance.
            
        Raises:
            TypeError: If the input value cannot be converted to a numeric type.
        """
        self.raw_value = value
        self.source_unit = source_unit
        self._registry = ureg()
        self._target_unit: str | Any | None = None 
        
        self._options: dict[str, Any] = {
            "mode": "float64",
            "prec": None,
            "roundin": "half_even",
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
            self._internal_val = value if isinstance(value, (np.ndarray, np.generic)) else np.array(value, dtype=float)
            self.is_array = True
        else:
            self.is_array = False
            try:
                self._internal_val = value if isinstance(value, Decimal) else float(value) # type: ignore
            except (TypeError, ValueError):
                raise TypeError(f"Invalid input: '{value}' cannot be converted to a numeric type.")
            
    def to(self, unit: UnitLike) -> _ConversionBuilder[_T_Out]:
        """
        Sets the target unit for the conversion.

        Args:
            unit: The symbol, alias, or BaseUnit class of the destination unit.
            
        Returns:
            The current builder instance to allow method chaining.
        """
        self._target_unit = unit
        return self

    @overload
    def use(self: _ConversionBuilder[float], dtype: Literal["decimal", "float64"] | None = ..., out: Literal["obj"] = ..., roundin: Literal["half_even", "half_up"] | None = ..., prec: int | None = ..., sigfigs: int | None = ..., scinote: bool | None = ..., delim: bool | str | None = ..., **kwargs: Any) -> _ConversionBuilder['BaseUnit']: ...

    @overload
    def use(self: _ConversionBuilder[float], dtype: Literal["decimal", "float64"] | None = ..., out: Literal["str", "tag", "verbose"] = ..., roundin: Literal["half_even", "half_up"] | None = ..., prec: int | None = ..., sigfigs: int | None = ..., scinote: bool | None = ..., delim: bool | str | None = ..., **kwargs: Any) -> _ConversionBuilder[str]: ...

    # --- DECIMAL Scalar ---
    @overload
    def use(self: _ConversionBuilder[float], dtype: Literal["decimal"], out: Literal["raw"] = ..., roundin: Literal["half_even", "half_up"] | None = ..., prec: int | None = ..., sigfigs: int | None = ..., scinote: bool | None = ..., delim: bool | str | None = ..., **kwargs: Any) -> _ConversionBuilder[Decimal]: ...

    @overload
    def use(self: _ConversionBuilder[float], dtype: Literal["decimal"], out: None = ..., roundin: Literal["half_even", "half_up"] | None = ..., prec: int | None = ..., sigfigs: int | None = ..., scinote: bool | None = ..., delim: bool | str | None = ..., **kwargs: Any) -> _ConversionBuilder[Decimal]: ...

    # --- FLOAT64 Scalar ---
    @overload
    def use(self: _ConversionBuilder[float], dtype: Literal["float64"] | None = ..., out: Literal["raw"] = ..., roundin: Literal["half_even", "half_up"] | None = ..., prec: int | None = ..., sigfigs: int | None = ..., scinote: bool | None = ..., delim: bool | str | None = ..., **kwargs: Any) -> _ConversionBuilder[float]: ...

    @overload
    def use(self: _ConversionBuilder[float], dtype: Literal["float64"] | None = ..., out: None = ..., roundin: Literal["half_even", "half_up"] | None = ..., prec: int | None = ..., sigfigs: int | None = ..., scinote: bool | None = ..., delim: bool | str | None = ..., **kwargs: Any) -> _ConversionBuilder[float]: ...

    # Self-Typing Overloads for LIST (list[float] / list[Decimal])

    @overload
    def use(self: _ConversionBuilder[list[float]], dtype: Literal["decimal", "float64"] | None = ..., out: Literal["obj"] = ..., roundin: Literal["half_even", "half_up"] | None = ..., prec: int | None = ..., sigfigs: int | None = ..., scinote: bool | None = ..., delim: bool | str | None = ..., **kwargs: Any) -> _ConversionBuilder[list['BaseUnit']]: ...

    @overload
    def use(self: _ConversionBuilder[list[float]], dtype: Literal["decimal", "float64"] | None = ..., out: Literal["str", "tag", "verbose"] = ..., roundin: Literal["half_even", "half_up"] | None = ..., prec: int | None = ..., sigfigs: int | None = ..., scinote: bool | None = ..., delim: bool | str | None = ..., **kwargs: Any) -> _ConversionBuilder[list[str]]: ...

    # --- DECIMAL List ---
    @overload
    def use(self: _ConversionBuilder[list[float]], dtype: Literal["decimal"], out: Literal["raw"] = ..., roundin: Literal["half_even", "half_up"] | None = ..., prec: int | None = ..., sigfigs: int | None = ..., scinote: bool | None = ..., delim: bool | str | None = ..., **kwargs: Any) -> _ConversionBuilder[list[Decimal]]: ...

    @overload
    def use(self: _ConversionBuilder[list[float]], dtype: Literal["decimal"], out: None = ..., roundin: Literal["half_even", "half_up"] | None = ..., prec: int | None = ..., sigfigs: int | None = ..., scinote: bool | None = ..., delim: bool | str | None = ..., **kwargs: Any) -> _ConversionBuilder[list[Decimal]]: ...

    # --- FLOAT64 List ---
    @overload
    def use(self: _ConversionBuilder[list[float]], dtype: Literal["float64"] | None = ..., out: Literal["raw"] = ..., roundin: Literal["half_even", "half_up"] | None = ..., prec: int | None = ..., sigfigs: int | None = ..., scinote: bool | None = ..., delim: bool | str | None = ..., **kwargs: Any) -> _ConversionBuilder[list[float]]: ...

    @overload
    def use(self: _ConversionBuilder[list[float]], dtype: Literal["float64"] | None = ..., out: None = ..., roundin: Literal["half_even", "half_up"] | None = ..., prec: int | None = ..., sigfigs: int | None = ..., scinote: bool | None = ..., delim: bool | str | None = ..., **kwargs: Any) -> _ConversionBuilder[list[float]]: ...

    # Self-Typing Overloads for NDARRAY (np.ndarray)
    @overload
    def use(self: _ConversionBuilder['np.ndarray'], dtype: Literal["decimal", "float64"] | None = ..., out: Literal["obj"] = ..., roundin: Literal["half_even", "half_up"] | None = ..., prec: int | None = ..., sigfigs: int | None = ..., scinote: bool | None = ..., delim: bool | str | None = ..., **kwargs: Any) -> _ConversionBuilder['np.ndarray']: ...

    @overload
    def use(self: _ConversionBuilder['np.ndarray'], dtype: Literal["decimal", "float64"] | None = ..., out: Literal["str", "tag", "verbose"] = ..., roundin: Literal["half_even", "half_up"] | None = ..., prec: int | None = ..., sigfigs: int | None = ..., scinote: bool | None = ..., delim: bool | str | None = ..., **kwargs: Any) -> _ConversionBuilder['np.ndarray']: ...

    @overload
    def use(self: _ConversionBuilder['np.ndarray'], dtype: Literal["decimal", "float64"] | None = ..., out: Literal["raw"] = ..., roundin: Literal["half_even", "half_up"] | None = ..., prec: int | None = ..., sigfigs: int | None = ..., scinote: bool | None = ..., delim: bool | str | None = ..., **kwargs: Any) -> _ConversionBuilder['np.ndarray']: ...

    @overload
    def use(self: _ConversionBuilder['np.ndarray'], dtype: Literal["decimal", "float64"] | None = ..., out: None = ..., roundin: Literal["half_even", "half_up"] | None = ..., prec: int | None = ..., sigfigs: int | None = ..., scinote: bool | None = ..., delim: bool | str | None = ..., **kwargs: Any) -> _ConversionBuilder['np.ndarray']: ...

    def use(
        self, 
        dtype: Literal["decimal", "float64"] | None = None, 
        out: Literal["raw", "str", "obj", "tag", "verbose"] | None = None, 
        roundin: Literal["half_even", "half_up"] | None = None, 
        prec: int | None = None, 
        sigfigs: int | None = None, 
        scinote: bool | None = None, 
        delim: bool | str | None = None, 
        **kwargs: Any
    ) -> _ConversionBuilder[Any]:
        """
        Configures the calculation engine, output structure, and mathematical precision.

        This method acts as the control panel for the conversion pipeline, bridging 
        the gap between raw numerical calculation and presentation-ready data formatting.

        Args:
            dtype: The underlying mathematical engine to compute the conversion.
                - 'float64' (default): High-performance C-native floating point.
                - 'decimal': High-precision arithmetic (prevents floating-point errors, slower).
            out: Determines the structural data type of the resolved output:
                - 'raw' (default): Returns the bare magnitude (scalar, Decimal, or ndarray).
                - 'obj': Returns fully instantiated Phaethon BaseUnit object(s). 
                         (Returns a single object for scalars, or a collection/ndarray 
                         of objects for vectorized inputs).
                - 'str' / 'tag': Returns a formatted string with unit symbols (e.g., '10.5 kg').
                - 'verbose': Returns a complete equation string (e.g., '1000 g = 1 kg').
            roundin: The rounding strategy to apply ("half_even" or "half_up").
            prec: The exact number of decimal places to calculate or display.
            sigfigs: The number of significant figures to enforce on the final value.
            scinote: If True, formats the output string in scientific notation (e.g., 1.05E+01).
            delim: If True, adds thousands separators. Can also accept a custom delimiter string.
            **kwargs: Alternative aliases for convenience (e.g., `precision=2`, `sci_note=True`, `mode='decimal'`).

        Returns:
            The configured conversion pipeline, ready to be executed via `.resolve()`.
        """

        if dtype in {"decimal", "dec"} and getattr(self, 'is_array', False):
            raise ConversionError(
                "Decimal dtype is not supported for vectorized array operations. "
                "NumPy arrays natively use float64 for performance."
            )
        
        if dtype is not None: self._options["dtype"] = dtype
        if out is not None: self._options["output"] = out
        if roundin is not None: self._options["roundin"] = roundin
        if prec is not None: self._options["prec"] = prec
        if sigfigs is not None: self._options["sigfigs"] = sigfigs
        if scinote is not None: self._options["scinote"] = scinote
        if delim is not None: self._options["delim"] = delim

        aliases_map = {
            'dtype': ['mode', 'type', 'engine'],
            'prec': ['precision'],
            'delim': ['delimiter'],
            'roundin': ['rounding', 'round'],
            'sigfigs': ['significant_figures'],
            'scinote': ['scientific_notation', 'sci_note'],
            'output': ['fmt', 'format', 'out']
        }
        for main_key, aliases in aliases_map.items():
            for alias in aliases:
                if alias in kwargs:
                    self._options[main_key] = kwargs[alias]
                    
        return self

    def context(self, ctx: ContextDict | None = None, **kwargs: NumericLike | 'BaseUnit') -> _ConversionBuilder[_T_Out]:
        """
        Dynamically injects physical variables or environmental conditions required 
        for context-dependent dimensional conversions (e.g., temperature for Mach speed).

        Args:
            **kwargs: Arbitrary keyword arguments representing physical conditions 
                (e.g., temperature=25, atm_pressure_pa=101325).

        Returns:
            The current builder instance to allow method chaining.
        """
        if ctx is not None:
            self._context.update(ctx)
        if kwargs:
            self._context.update(kwargs)
        return self

    def _round_sigfigs(self, num: float | Decimal, sigfigs: int) -> float | Decimal:
        """Applies significant figures rounding."""
        if num == 0:
            return Decimal(0)
        elif isinstance(num, Decimal):
            shift = sigfigs - num.adjusted() - 1
            quantizer = Decimal('1e{}'.format(-shift))
            return num.quantize(quantizer, rounding=getcontext().rounding)
        else:
            return round(num, -int(floor(log10(abs(num)))) + (sigfigs - 1))

    def _compute(self) -> float | Decimal | Any:
        """Executes the dimensional algebra and returns the raw scalar/vector."""
        if not self._target_unit:
            raise ConversionError("Target unit missing. You must call .to('unit') before computing.")

        SourceClass = self.source_unit if hasattr(self.source_unit, 'dimension') else None
        TargetClass = self._target_unit if hasattr(self._target_unit, 'dimension') else None

        expected_dimension = getattr(SourceClass, 'dimension', None) or getattr(TargetClass, 'dimension', None)

        if expected_dimension is None:
            target_ambiguous = False
            source_ambiguous = False
            
            try:
                TargetClass = self._registry.get_unit_class(self._target_unit)
                expected_dimension = TargetClass.dimension
            except AmbiguousUnitError:
                target_ambiguous = True
            except UnitNotFoundError:
                pass
                
            if expected_dimension is None:
                try:
                    SourceClass = self._registry.get_unit_class(self.source_unit)
                    expected_dimension = SourceClass.dimension
                except AmbiguousUnitError:
                    source_ambiguous = True
                except UnitNotFoundError:
                    pass

            if expected_dimension is None:
                if target_ambiguous and source_ambiguous:
                    self._registry.get_unit_class(self.source_unit)
                elif source_ambiguous:
                    self._registry.get_unit_class(self.source_unit)
                elif target_ambiguous:
                    self._registry.get_unit_class(self._target_unit)
                else:
                    raise ConversionError(
                        f"Cannot resolve dimension for conversion from "
                        f"'{self.source_unit}' to '{self._target_unit}'."
                    )

        if SourceClass is None:
            SourceClass = self._registry.get_unit_class(self.source_unit, expected_dim=expected_dimension)
        if TargetClass is None:
            TargetClass = self._registry.get_unit_class(self._target_unit, expected_dim=expected_dimension)

        if getattr(TargetClass, 'dimension', None) != getattr(SourceClass, 'dimension', None):
            raise ConversionError(
                f"Dimension mismatch! Expected '{getattr(SourceClass, 'dimension', None)}', "
                f"got '{getattr(TargetClass, 'dimension', None)}'"
            )

        # Cache symbols for string formatting
        self._src_symbol = getattr(SourceClass, 'symbol', getattr(SourceClass, '__name__', str(self.source_unit)))
        self._tgt_symbol = getattr(TargetClass, 'symbol', getattr(TargetClass, '__name__', str(self._target_unit)))

        # ---------------------------------------------------------
        # Path A: Native Array Computation (Bypass scalar mechanics)
        # ---------------------------------------------------------
        if self.is_array and HAS_NUMPY:
            source_obj = SourceClass(self._internal_val, context=self._context)
            target_obj = source_obj.to(TargetClass)
            return target_obj.exact

        # ---------------------------------------------------------
        # Path B: Scalar Computation (Decimal / Float64)
        # ---------------------------------------------------------
        mode = str(self._options["mode"]).lower().strip()
        prec = self._options["prec"]
        roundin = str(self._options["roundin"]).lower().strip()

        if mode in {"decimal", "dec"}:
            getcontext().prec = prec * 2 if prec else 28
            getcontext().rounding = ROUND_HALF_EVEN if roundin == "half_even" else ROUND_HALF_UP

            safe_dec_val = Decimal(str(self._internal_val)) if not isinstance(self._internal_val, Decimal) else self._internal_val
            source_obj = SourceClass(safe_dec_val, context=self._context)
            target_obj = source_obj.to(TargetClass)
            
            converted_value = target_obj.exact

            if HAS_NUMPY and isinstance(converted_value, (np.ndarray, np.generic)):
                return converted_value

            digits = converted_value.adjusted() + 1
            decimal_places = prec - digits if prec else 0

            if prec is not None and 0 <= decimal_places <= 50:
                try:
                    quant = Decimal(f"1e-{decimal_places}")
                    final_value = converted_value.quantize(quant, rounding=getcontext().rounding)
                except (InvalidOperation, ValueError):
                    final_value = converted_value.normalize()
            else:
                final_value = converted_value.normalize()

        elif mode in {"float", "float64"}:
            source_obj = SourceClass(float(self.raw_value), context=self._context)
            target_obj = source_obj.to(TargetClass)
            
            converted_value = target_obj.exact
            
            if HAS_NUMPY and isinstance(converted_value, (np.ndarray, np.generic)):
                if prec is not None:
                    final_value = np.round(converted_value, prec)
                else:
                    final_value = converted_value
            else:
                if prec is not None:
                    final_value = round(converted_value, prec)
                else:
                    final_value = float(converted_value)
        else:
            raise ConversionError(f"Computation mode '{mode}' is not recognized. Use 'decimal' or 'float64'.")

        sigfigs = self._options["sigfigs"]
        if sigfigs:
            try:
                sigfigs = int(sigfigs)
                if sigfigs <= 0: raise ValueError()
            except Exception:
                raise ConversionError("Significant figures (sigfigs) must be a positive integer!")
            
            if mode in {"decimal", "dec"}:
                getcontext().prec = max(getcontext().prec, sigfigs * 2)
            
            if not (HAS_NUMPY and isinstance(final_value, (np.ndarray, np.generic))):
                final_value = self._round_sigfigs(final_value, sigfigs)

        return final_value
    
    def resolve(self) -> _T_Out:
        """
        Executes the conversion pipeline and finalizes the output.
        
        The structural type of the return value depends entirely on the `format` 
        configured via `.use(format=...)`. Defaults to returning raw numerics.
        
        Returns:
            The final converted magnitude, vectorized array, formatted string, 
            or BaseUnit instance depending on the applied configuration.
            
        Raises:
            ConversionError: If the target unit was not defined prior to resolution.
        """
        if not self._target_unit:
            raise ConversionError("Target unit missing. You must call .to('unit') before computing.")

        output_fmt = str(self._options.get("output", "raw")).lower().strip()
        req_dtype = str(self._options.get("dtype", self._options.get("mode", "float64"))).lower().strip()
        TargetClass = self._target_unit if hasattr(self._target_unit, 'dimension') else self._registry.get_unit_class(str(self._target_unit))

        if getattr(self, '_is_single_unit', False):
            if req_dtype in {"decimal", "dec"}:
                raw_val = self.raw_value.mag # type: ignore
                safe_val = Decimal(str(raw_val)) if not isinstance(raw_val, Decimal) else raw_val
                processing_obj = self.raw_value.__class__(safe_val, context=self.raw_value.context) # type: ignore
            elif req_dtype in {"float", "float64"}:
                processing_obj = self.raw_value.__class__(float(self.raw_value.mag), context=self.raw_value.context) # type: ignore
            else:
                processing_obj = self.raw_value # type: ignore

            converted_obj = processing_obj.to(TargetClass)
            
            if output_fmt == "obj": return converted_obj
            if output_fmt in ("raw", "exact"): return converted_obj.mag
            
            return converted_obj.format(
                prec=self._options.get("prec"),
                sigfigs=self._options.get("sigfigs"),
                scinote=self._options.get("scinote", False),
                delim=self._options.get("delim", False),
                tag=(output_fmt in ("tag", "str", "verbose"))
            )

        if getattr(self, '_is_unit_list', False):
            results = []
            iterable_val = self.raw_value.flatten() if (HAS_NUMPY and isinstance(self.raw_value, np.ndarray)) else self.raw_value
            
            for item in iterable_val: # type: ignore
                if req_dtype in {"decimal", "dec"}:
                    raw_val = item.mag
                    safe_val = Decimal(str(raw_val)) if not isinstance(raw_val, Decimal) else raw_val
                    processing_obj = item.__class__(safe_val, context=item.context)
                elif req_dtype in {"float", "float64"}:
                    processing_obj = item.__class__(float(item.mag), context=item.context)
                else:
                    processing_obj = item

                converted_obj = processing_obj.to(TargetClass)
                
                if output_fmt == "obj":
                    results.append(converted_obj)
                elif output_fmt in ("raw", "exact"):
                    results.append(converted_obj.mag)
                else:
                    results.append(converted_obj.format(
                        prec=self._options.get("prec"),
                        sigfigs=self._options.get("sigfigs"),
                        scinote=self._options.get("scinote", False),
                        delim=self._options.get("delim", False),
                        tag=(output_fmt in ("tag", "str", "verbose"))
                    ))
                    
            if HAS_NUMPY and isinstance(self.raw_value, np.ndarray):
                return np.array(results, dtype=object).reshape(self.raw_value.shape)
            return results


        final_value = self._compute()
        
        if output_fmt == "obj":
            return TargetClass(final_value, context=self._context) # type: ignore
        
        src_name = getattr(self, '_src_symbol', str(self.source_unit))
        tgt_name = getattr(self, '_tgt_symbol', str(self._target_unit))
        
        scinote = self._options.get("scinote", False)
        delim = self._options.get("delim", False)
        sigfigs = self._options.get("sigfigs")
        prec = self._options.get("prec")

        if HAS_NUMPY and isinstance(final_value, (np.ndarray, np.generic)):
            if output_fmt in ("exact", "raw"): return final_value

            def format_elem(x: Any) -> str:
                if scinote:
                    digits = sigfigs - 1 if sigfigs is not None else (prec or 4)
                    return f"{x:.{digits}E}"
                s = f"{float(x):.{prec or 4}f}"
                if '.' in s:
                    s = s.rstrip('0')
                    if s.endswith('.'): s += '0'
                if delim:
                    separator = "," if delim is True or str(delim).lower() == "default" else str(delim)
                    parts = s.split('.')
                    parts[0] = f"{int(parts[0]):,}".replace(",", separator)
                    s = '.'.join(parts) if len(parts) > 1 else parts[0]
                return s

            val_str = np.array2string(
                final_value, 
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

        if output_fmt == "raw": return final_value

        if scinote:
            digits = sigfigs - 1 if sigfigs is not None else (prec or 4)
            val_str = f"{final_value:.{digits}E}" if isinstance(final_value, Decimal) else format(final_value, 'e')
        else:
            if sigfigs and isinstance(final_value, Decimal):
                decimal_places = max(sigfigs - (final_value.adjusted() + 1), 0)
                val_str = f"{final_value:.{decimal_places}f}"
            elif prec is not None:
                val_str = format(final_value, f'.{prec}f')
            else:
                val_str = str(final_value)

        if not scinote and '.' in val_str:
            val_str = val_str.rstrip('0')
            if val_str.endswith('.'): val_str += '0'

        if delim:
            separator = "," if delim is True or str(delim).lower() == "default" else str(delim)
            if not scinote:
                parts = val_str.split('.')
                parts[0] = f"{int(parts[0]):,}".replace(",", separator)
                val_str = '.'.join(parts) if len(parts) > 1 else parts[0]
            
            raw_str = str(self.raw_value)
            if '.' in raw_str:
                raw_parts = raw_str.split('.')
                raw_parts[0] = f"{int(raw_parts[0]):,}".replace(",", separator)
                raw_str_formatted = '.'.join(raw_parts)
            else:
                try:
                    raw_str_formatted = f"{int(self.raw_value):,}".replace(",", separator)
                except ValueError:
                    raw_str_formatted = str(self.raw_value)
        else:
            raw_str_formatted = str(self.raw_value)

        if output_fmt == "verbose": return f"{raw_str_formatted} {src_name} = {val_str} {tgt_name}"
        if output_fmt == "tag": return f"{val_str} {tgt_name}"
            
        return val_str

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
        if self.is_array:
            raise ConversionError(".flex() method cannot be applied to NumPy arrays.")
            
        SourceClass = self._registry.get_unit_class(self.source_unit) if isinstance(self.source_unit, str) else self.source_unit
        source_obj = SourceClass(self._internal_val, context=self._context)

        if not hasattr(source_obj, 'flex'):
            raise ConversionError(
                f"Unit '{getattr(SourceClass, 'symbol', self.source_unit)}' (Dimension: {getattr(SourceClass, 'dimension', 'unknown')}) "
                f"does not support the .flex() method. This feature is exclusive to time dimensions."
            )
        
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


class _PhaethonEngine:
    """The core engine wrapper connecting the fluent API to the UnitRegistry."""
    def __init__(self, registry: UnitRegistry) -> None:
        """
        Initializes the Phaethon Unit-Safe Data Pipeline Schema and Semantic Data Transformation Engine.
        
        Args:
            registry: The global UnitRegistry instance containing loaded unit definitions.
        """
        self._registry = registry

    def convert(self, value: ConvertibleInput, unit: UnitLike) -> _ConversionBuilder:
        return _ConversionBuilder(value, unit)
    
_default_engine = _PhaethonEngine(registry=ureg())

@overload
def convert(value: 'BaseUnit') -> _ConversionBuilder[float]: ...

@overload
def convert(value: list[Any] | tuple[Any, ...] | set[Any]) -> _ConversionBuilder[list[float]]: ...

@overload
def convert(value: int | float | str | Decimal, unit: UnitLike) -> _ConversionBuilder[float]: ...

@overload
def convert(value: list[Any] | tuple[Any, ...] | set[Any], unit: UnitLike) -> _ConversionBuilder[list[float]]: ...

@overload
def convert(value: 'np.ndarray', unit: UnitLike | None = ...) -> _ConversionBuilder['np.ndarray']: ...

def convert(value: ConvertibleInput, unit: UnitLike | None = None) -> _ConversionBuilder[Any]:
    """
    Initializes a fluent conversion pipeline for physical and digital units.

    This method serves as the primary entry point for the Phaethon library. 
    It provides a chainable, intuitive, and highly precise conversion interface. 
    The pipeline preserves the shape of your input data 
    (e.g., returning a list if given a list, or an array if given an array).

    Args:
        value: The magnitude to be converted (scalar, list, or NumPy array), 
               or an iterable of instantiated Phaethon Units.
        unit: The source unit class or string alias (Required if value is a raw number).

    Returns:
        A builder object allowing chained execution methods like `.to()`, `.use()`, 
        `.context()`, and finally `.resolve()`.
    """
    return _default_engine.convert(value, unit)