"""
Defines a set of physical laws, constraints, and mathematical modifiers 
that dynamically govern the instantiation and conversion of Phaethon units.
It acts as a physics rule engine utilizing Python decorators.
"""
from __future__ import annotations

import math
import inspect
import functools
from typing import Callable, Any, Literal, TYPE_CHECKING

if TYPE_CHECKING:
    from .base import BaseUnit
    from typing import Protocol

    class SupportsContextEvaluation(Protocol):
        def __call__(self, context: ContextDict) -> NumericLike: ...

from .compat import _UnitClassT, _CallableT, NumericLike, ContextDict
from ..exceptions import AxiomViolationError, DimensionMismatchError

try:
    import numpy as np
    HAS_NUMPY = True
except ImportError:
    HAS_NUMPY = False

class CtxProxy:
    """
    A declarative Context Variable proxy for Phaethon Axioms.
    Allows developers to build mathematical formulas using standard Python operators.
    """
    def __init__(self, key: str | None = None, default: Any = 0.0, _evaluator: Callable[..., Any] | None = None) -> None:
        self.key = key
        self.default = default
        self._evaluator = _evaluator

    def __call__(self, context: ContextDict) -> Any:
        if self._evaluator:
            return self._evaluator(context)
        return context.get(self.key, self.default)

    def __add__(self, other: NumericLike | 'CtxProxy') -> CtxProxy:
        return CtxProxy(_evaluator=lambda c: self(c) + (other(c) if isinstance(other, CtxProxy) else other))
    
    def __radd__(self, other: NumericLike | 'CtxProxy') -> CtxProxy:
        return CtxProxy(_evaluator=lambda c: (other(c) if isinstance(other, CtxProxy) else other) + self(c))

    def __sub__(self, other: NumericLike | 'CtxProxy') -> CtxProxy:
        return CtxProxy(_evaluator=lambda c: self(c) - (other(c) if isinstance(other, CtxProxy) else other))

    def __rsub__(self, other: NumericLike | 'CtxProxy') -> CtxProxy:
        return CtxProxy(_evaluator=lambda c: (other(c) if isinstance(other, CtxProxy) else other) - self(c))

    def __mul__(self, other: NumericLike | 'CtxProxy') -> CtxProxy:
        return CtxProxy(_evaluator=lambda c: self(c) * (other(c) if isinstance(other, CtxProxy) else other))

    def __rmul__(self, other: NumericLike | 'CtxProxy') -> CtxProxy:
        return CtxProxy(_evaluator=lambda c: (other(c) if isinstance(other, CtxProxy) else other) * self(c))

    def __truediv__(self, other: NumericLike | 'CtxProxy') -> CtxProxy:
        return CtxProxy(_evaluator=lambda c: self(c) / (other(c) if isinstance(other, CtxProxy) else other))

    def __rtruediv__(self, other: NumericLike | 'CtxProxy') -> CtxProxy:
        return CtxProxy(_evaluator=lambda c: (other(c) if isinstance(other, CtxProxy) else other) / self(c))

    def __pow__(self, other: NumericLike | 'CtxProxy') -> CtxProxy:
        return CtxProxy(_evaluator=lambda c: self(c) ** (other(c) if isinstance(other, CtxProxy) else other))

C = CtxProxy

def bound(
    min_val: NumericLike | None = None, 
    max_val: NumericLike | None = None, 
    msg: str | None = None,
    abstract: bool = False
) -> Callable[[_UnitClassT], _UnitClassT]:
    """
    Enforces physical boundary limits on a unit's magnitude during instantiation.
    Respects the 'axiom_strictness_level' and 'default_on_error' strategy.

    Args:
        min_val: The absolute minimum allowed value.
        max_val: The absolute maximum allowed value.
        msg: A custom error message thrown upon violation.
        abstract: If True, blocks users from instantiating this parent class directly.

    Returns:
        A class decorator enforcing the boundary.
    """
    def decorator(cls: _UnitClassT) -> _UnitClassT:
        cls.__axiom_min__ = min_val  # type: ignore
        cls.__axiom_max__ = max_val  # type: ignore
        cls.__is_abstract_dimension__ = abstract
        original_init = cls.__init__
        
        @functools.wraps(original_init)
        def new_init(self_obj: Any, value: int | float | str | Any, context: dict[str, Any] | None = None) -> None:
            if abstract and type(self_obj) is cls:
                raise TypeError(
                    f"'{cls.__name__}' is an Abstract Dimensional Class "
                    f"and cannot be instantiated directly. It is strictly used for inheritance and "
                    f"polymorphism. Please use a concrete unit (e.g., 'Pascal' or 'Meter')."
                )
            
            original_init(self_obj, value, context)
            val = self_obj._value
            
            from .config import get_config
            import warnings
            
            strictness = self_obj.context.get("axiom_strictness_level")
            if strictness is None:
                strictness = get_config("axiom_strictness_level") or "default"
                
            if strictness == "ignore":
                return
            
            is_math_op = self_obj.context.get("__is_math_op__", False)
            should_warn = False
            should_enforce = False
            
            if is_math_op:
                if strictness == "strict": should_enforce = True
                elif strictness == "strict_warn": should_warn = True
            else:
                if strictness in ("default", "strict", "strict_warn"): should_enforce = True
                elif strictness == "loose_warn": should_warn = True
            
            if not should_warn and not should_enforce:
                return

            policy = self_obj.context.get("default_on_error") or get_config("default_on_error") or "raise"
            TOLERANCE = 1e-12 
            
            if HAS_NUMPY and isinstance(val, (np.ndarray, np.generic)):
                mask = ~np.isnan(val)
                valid_vals = val[mask]
                
                if valid_vals.size > 0:
                    violated_min = min_val is not None and np.any(valid_vals < (float(min_val) - TOLERANCE))
                    violated_max = max_val is not None and np.any(valid_vals > (float(max_val) + TOLERANCE))
                    
                    if violated_min or violated_max:
                        error_msg = msg or f"Array contains values outside physical boundaries (min={min_val}, max={max_val})."
                        
                        if should_warn and not should_enforce:
                            warnings.warn(f"Phaethon Axiom Warning: {error_msg} (in {cls.__name__})", category=UserWarning, stacklevel=3)
                            return
                        
                        if should_enforce:
                            if policy == "raise":
                                if violated_min: raise AxiomViolationError(msg or f"Array contains values strictly less than {min_val}")
                                if violated_max: raise AxiomViolationError(msg or f"Array contains values strictly greater than {max_val}")
                            elif policy in ("null", "coerce"):
                                new_val = np.array(val, dtype=float)
                                if min_val is not None: new_val = np.where(new_val < float(min_val), np.nan, new_val)
                                if max_val is not None: new_val = np.where(new_val > float(max_val), np.nan, new_val)
                                self_obj._value = new_val
                            elif policy == "clip":
                                a_min = float(min_val) if min_val is not None else None
                                a_max = float(max_val) if max_val is not None else None
                                self_obj._value = np.clip(val, a_min, a_max)
                        
            else:
                is_nan = math.isnan(val)
                if not is_nan:
                    val_f = float(val)
                    violated_min = min_val is not None and val_f < (float(min_val) - TOLERANCE)
                    violated_max = max_val is not None and val_f > (float(max_val) + TOLERANCE)
                    
                    if violated_min or violated_max:
                        error_msg = msg or f"Value violates physical boundaries (min={min_val}, max={max_val})."
                        
                        if should_warn and not should_enforce:
                            warnings.warn(f"Phaethon Axiom Warning: {error_msg} (in {cls.__name__})", category=UserWarning, stacklevel=3)
                            return

                        if should_enforce:
                            if policy == "raise":
                                if violated_min: raise AxiomViolationError(msg or f"Value cannot be strictly less than {min_val}")
                                if violated_max: raise AxiomViolationError(msg or f"Value cannot be strictly greater than {max_val}")
                            elif policy in ("null", "coerce"):
                                self_obj._value = float('nan')
                            elif policy == "clip":
                                if violated_min: self_obj._value = float(min_val) # type: ignore
                                elif violated_max: self_obj._value = float(max_val) # type: ignore

        cls.__init__ = new_init  # type: ignore
        return cls
    return decorator


def shift(
    ctx: str | None = None, 
    default: NumericLike = 0.0, 
    op: Literal["add", "sub"] = "add", 
    formula: Callable[..., NumericLike] | CtxProxy | None = None
) -> Callable[[_UnitClassT], _UnitClassT]:
    """
    Applies a linear shift (addition or subtraction) to the base offset of a unit.
    Driven dynamically by environmental context variables.

    Args:
        ctx: The dictionary key to search for in the unit's context.
        default: Fallback shift value if the context key is missing.
        op: Mathematical operation, strictly either "add" or "sub". Defaults to "add".
        formula: A custom physics function to calculate complex shifts.

    Returns:
        A class decorator overriding base logic.
    """
    def decorator(cls: _UnitClassT) -> _UnitClassT:
        orig_to_base = getattr(cls, '_to_base_value')
        orig_from_base = getattr(cls, '_from_base_value')
        _cached_sig = None

        if formula and not isinstance(formula, CtxProxy):
            try:
                _cached_sig = inspect.signature(formula)
            except (ValueError, TypeError):
                _cached_sig = None

        def get_ctx_val(context: dict[str, Any]) -> float | Any:
            res = default
            if formula:
                if isinstance(formula, CtxProxy):
                    res = formula(context)
                    if hasattr(res, '_to_base_value'):
                        res = res._to_base_value()
                elif _cached_sig:
                    kwargs = {}
                    for param_name, param in _cached_sig.parameters.items():
                        if param_name in context:
                            val = context[param_name]
                            if hasattr(val, 'to') and hasattr(val, 'mag'):
                                kwargs[param_name] = val
                            else:
                                kwargs[param_name] = float(val) if not isinstance(val, (np.ndarray, np.generic)) else val
                        elif param.default is not inspect.Parameter.empty:
                            kwargs[param_name] = param.default
                        else:
                            raise AxiomViolationError(
                                f"Missing required context variable: '{param_name}' "
                                f"needed to evaluate the axiom formula in {cls.__name__}."
                            )
                    res = formula(**kwargs)
            elif ctx:
                val = context.get(ctx, default)
                if hasattr(val, '_to_base_value'):
                    val = val._to_base_value()
                res = val

            if HAS_NUMPY and isinstance(res, (np.ndarray, np.generic)): return res
            return float(res)

        def new_to_base(self_obj: Any) -> float | Any:
            base_val = orig_to_base(self_obj)
            ctx_val = get_ctx_val(self_obj.context)
            if op == "add": return base_val + ctx_val
            elif op == "sub": return base_val - ctx_val
            return base_val

        @classmethod
        def new_from_base(cls_obj: type, base_val: float | Any, context: dict[str, Any]) -> float | Any:
            ctx_val = get_ctx_val(context)
            if op == "add": base_val = base_val - ctx_val
            elif op == "sub": base_val = base_val + ctx_val
            return orig_from_base.__func__(cls_obj, base_val, context)

        cls._to_base_value = new_to_base  # type: ignore
        cls._from_base_value = new_from_base  # type: ignore
        return cls
    return decorator


def scale(
    ctx: str | None = None, 
    default: NumericLike = 1.0, 
    formula: Callable[..., NumericLike] | CtxProxy | None = None
) -> Callable[[_UnitClassT], _UnitClassT]:
    """
    Applies a dynamic scaling factor (multiplication/division) to the base multiplier.
    Safe for both Decimal scalars and NumPy arrays.

    Args:
        ctx: The dictionary key in the unit's context.
        default: Fallback multiplier if the context key is missing.
        formula: A custom physics function to calculate dynamic scaling.

    Returns:
        A class decorator overriding base logic.
    """
    def decorator(cls: _UnitClassT) -> _UnitClassT:
        orig_to_base = getattr(cls, '_to_base_value')
        orig_from_base = getattr(cls, '_from_base_value')
        _cached_sig = None

        if formula and not isinstance(formula, CtxProxy):
            try:
                _cached_sig = inspect.signature(formula)
            except (ValueError, TypeError):
                _cached_sig = None

        def get_ctx_val(context: dict[str, Any]) -> float | Any:
            res = default
            if formula:
                if isinstance(formula, CtxProxy):
                    res = formula(context)
                    if hasattr(res, '_to_base_value'):
                        res = res._to_base_value()
                elif _cached_sig:
                    kwargs = {}
                    for param_name, param in _cached_sig.parameters.items():
                        if param_name in context:
                            val = context[param_name]
                            if hasattr(val, 'to') and hasattr(val, 'mag'):
                                kwargs[param_name] = val
                            else:
                                kwargs[param_name] = float(val) if not isinstance(val, (np.ndarray, np.generic)) else val
                        elif param.default is not inspect.Parameter.empty:
                            kwargs[param_name] = param.default
                        else:
                            raise AxiomViolationError(
                                f"Missing required context variable: '{param_name}' "
                                f"needed to evaluate the axiom formula in {cls.__name__}."
                            )
                    res = formula(**kwargs)
            elif ctx:
                val = context.get(ctx, default)
                if hasattr(val, '_to_base_value'):
                    val = val._to_base_value()
                res = val

            if HAS_NUMPY and isinstance(res, (np.ndarray, np.generic)): return res
            return float(res)

        def new_to_base(self_obj: Any) -> float | Any:
            base_val = orig_to_base(self_obj)
            ctx_val = get_ctx_val(self_obj.context)
            return base_val * ctx_val

        @classmethod
        def new_from_base(cls_obj: type, base_val: float | Any, context: dict[str, Any]) -> float | Any:
            ctx_val = get_ctx_val(context)
            return orig_from_base.__func__(cls_obj, base_val / ctx_val, context)

        cls._to_base_value = new_to_base  # type: ignore
        cls._from_base_value = new_from_base  # type: ignore
        return cls
    return decorator


def derive(
    unit_expr: type[BaseUnit] | None = None,
    *,
    mul: list[type[BaseUnit] | NumericLike] | None = None, 
    div: list[type[BaseUnit] | NumericLike] | None = None
) -> Callable[[_UnitClassT], _UnitClassT]:
    """
    A class decorator for Dimensional Synthesis.
    
    Synthesizes a new physical unit by deriving its dimensional signature and 
    base multiplier from an algebraic expression of existing units.
    
    Supports direct Metaclass algebra (preferred) or explicit mul/div lists.
    
    Example:
        >>> @derive(Kilogram * Meter / Second**2)
        >>> class Newton(ForceUnit): 
        >>>    symbol = "N"
            
        >>> # Deprecated Syntax
        >>> @derive(mul=[u.Kilogram, u.Meter], div=[u.Second, u.Second])
        >>> class Newton(ForceUnit): 
        >>>    symbol = "N"
    """
    import warnings
    if mul is not None or div is not None:
        msg = (
            "\033[33mThe explicit 'mul' and 'div' list arguments in '@axiom.derive' "
            "are deprecated and will be removed in a future update. "
            "Please migrate to the new Dimensional Synthesis syntax (e.g., @axiom.derive(Joule / Meter)).\033[0m\n"
        )
        warnings.warn(msg, category=DeprecationWarning, stacklevel=2)

    def decorator(cls: _UnitClassT) -> _UnitClassT:
        if unit_expr is not None:
            cls.base_multiplier = float(getattr(unit_expr, 'base_multiplier', 1.0))  # type: ignore
            cls.base_offset = float(getattr(unit_expr, 'base_offset', 0.0))  # type: ignore

            expr_sig = getattr(unit_expr, '_signature', None)
            if expr_sig:
                cls._signature = expr_sig  # type: ignore
                from .registry import ureg
                dim_name = getattr(cls, 'dimension', 'anonymous')
                if dim_name != 'anonymous':
                    ureg().inject_dna(expr_sig, dim_name)

            if hasattr(unit_expr, '_to_base_value') and getattr(unit_expr, '__name__', '').startswith('Derived_'):
                cls._to_base_value = unit_expr._to_base_value # type: ignore
                cls._from_base_value = unit_expr._from_base_value # type: ignore

            return cls
            
        mul_list = mul or []
        div_list = div or []
        
        multiplier = 1.0
        
        for item in mul_list:
            if isinstance(item, (int, float, str)):
                multiplier *= float(item)
            else:
                multiplier *= float(getattr(item, 'base_multiplier', 1.0))
                
        for item in div_list:
            if isinstance(item, (int, float, str)):
                val = float(item)
            else:
                val = float(getattr(item, 'base_multiplier', 1.0))
                
            if val == 0.0:
                raise ZeroDivisionError(f"Base multiplier cannot be zero in derive for {cls.__name__}.")
            multiplier /= val
            
        cls.base_offset = 0.0  # type: ignore
        cls.base_multiplier = multiplier  # type: ignore
        return cls
        
    return decorator


def require(**dim_or_class: str | type) -> Callable[[_CallableT], _CallableT]:
    """
    Enforces strict dimension or specific unit constraints on function arguments.
    Acts as a guardrail for custom physics functions preventing logic errors.

    Args:
        **dim_or_class: Keyword arguments mapping function parameter names 
            to either a required dimension string (e.g., 'mass') or a 
            specific BaseUnit class (e.g., Newton).

    Returns:
        A function wrapper validating the arguments before execution.
    """
    def decorator(func: _CallableT) -> _CallableT:
        sig = inspect.signature(func)
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            bound_args = sig.bind(*args, **kwargs)
            bound_args.apply_defaults()
            
            for param_name, param_value in bound_args.arguments.items():
                if param_name in dim_or_class:
                    constraint = dim_or_class[param_name]
                    
                    if isinstance(constraint, str):
                        if not hasattr(param_value, 'dimension'):
                            raise DimensionMismatchError(
                                expected_dim=constraint, 
                                received_dim=type(param_value).__name__,
                                context=f"Argument '{param_name}' is not a valid Phaethon unit object"
                            )
                        if param_value.dimension != constraint:
                            raise DimensionMismatchError(
                                expected_dim=constraint, 
                                received_dim=param_value.dimension,
                                context=f"Argument '{param_name}' in function '{func.__name__}'"
                            )
                            
                    elif isinstance(constraint, type):
                        if not isinstance(param_value, constraint):
                            raise TypeError(
                                f"Strict Type Violation: Argument '{param_name}' expected exactly "
                                f"'{constraint.__name__}', but got '{type(param_value).__name__}'."
                            )
                        
            return func(*args, **kwargs)
        return wrapper # type: ignore
    return decorator

def prepare(**unit_mappings: type[BaseUnit]) -> Callable[[_CallableT], _CallableT]:
    """
    Pre-processes formula arguments for pure mathematical functions.
    Automatically intercepts Phaethon objects, converts them to the specified 
    target unit, and extracts their raw magnitude (.mag) before execution.
    """
    def decorator(func: _CallableT) -> _CallableT:
        sig = inspect.signature(func)
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            bound_args = sig.bind(*args, **kwargs)
            bound_args.apply_defaults()

            for param_name, target_class in unit_mappings.items():
                if param_name in bound_args.arguments:
                    val = bound_args.arguments[param_name]
                    if hasattr(val, 'to') and hasattr(val, 'mag'):
                        bound_args.arguments[param_name] = val.to(target_class).mag

            return func(*bound_args.args, **bound_args.kwargs)
        return wrapper # type: ignore
    return decorator

def logarithmic(
    reference: NumericLike | BaseUnit, 
    multiplier: float = 10.0, 
    base: float = 10.0
) -> Callable[[_UnitClassT], _UnitClassT]:
    """
    Axiom for Non-Linear (Logarithmic) units like Decibels, pH, or Stellar Magnitude.
    
    Dynamically overrides base converters to handle logarithmic scales.
    Automatically intercepts algebraic operations (mul/div) and forces a "Linear Drop"
    using the absolute normalizer (~), protecting PINNs Autograd and Buckingham Pi 
    from exploding gradients or synthetic dimension errors.

    Args:
        reference: The linear reference value (e.g., Watt(1) for dBW).
        multiplier: The log multiplier (10.0 for Power, 20.0 for Voltage, -1.0 for pH).
        base: The logarithm base (typically 10.0).
    """
    def decorator(cls: _UnitClassT) -> _UnitClassT:
        ref_val = float(getattr(reference, '_to_base_value')()) if hasattr(reference, '_to_base_value') else float(reference)

        def new_to_base(self_obj: Any) -> Any:
            from .config import using
            with using(context=self_obj.context):
                val = self_obj._value
                if HAS_NUMPY and isinstance(val, (np.ndarray, np.generic)):
                    factor = base ** (val / multiplier)
                else:
                    factor = base ** (float(val) / multiplier)
                return ref_val * factor

        @classmethod
        def new_from_base(cls_obj: type, base_val: Any, context: dict[str, Any]) -> Any:
            from .config import using, get_config
            with using(context=context):
                policy = context.get("default_on_error") or get_config("default_on_error") or "raise"
                if HAS_NUMPY and isinstance(base_val, (np.ndarray, np.generic)):
                    safe_val = np.maximum(base_val, 1e-32)
                    return multiplier * (np.log(safe_val / ref_val) / np.log(base))
                
                b_float = float(base_val)
                if b_float <= 0:
                    if policy == "raise":
                        raise AxiomViolationError(
                            f"Cannot convert zero or negative linear value ({b_float}) "
                            f"to a logarithmic scale ({cls_obj.__name__})."
                        )
                    elif policy == "clip":
                        return float('-inf')
                    else: # coerce
                        return float('nan')

                return multiplier * math.log(b_float / ref_val, base)

        def new_mul(self_obj: Any, other: Any) -> Any:
            if isinstance(other, (int, float)) or (HAS_NUMPY and isinstance(other, (np.ndarray, np.generic))):
                linear_val_multiplied = self_obj._to_base_value() * other
                new_val = self_obj.__class__._from_base_value(linear_val_multiplied, self_obj.context)
                return self_obj.__class__(new_val, context=self_obj.context)
            return (~self_obj) * other

        def new_rmul(self_obj: Any, other: Any) -> Any:
            return other * (~self_obj)

        def new_truediv(self_obj: Any, other: Any) -> Any:
            if isinstance(other, (int, float)) or (HAS_NUMPY and isinstance(other, (np.ndarray, np.generic))):
                linear_val_divided = self_obj._to_base_value() / other
                new_val = self_obj.__class__._from_base_value(linear_val_divided, self_obj.context)
                return self_obj.__class__(new_val, context=self_obj.context)
            return (~self_obj) / other

        def new_rtruediv(self_obj: Any, other: Any) -> Any:
            return other / (~self_obj)

        def block_invalid_op(self_obj: Any, *args: Any, **kwargs: Any) -> Any:
            raise AxiomViolationError(
                f"You cannot exponentiate, floor divide, "
                f"or modulo a logarithmic unit ({cls.__name__})."
            )

        cls.__is_logarithmic__ = True
        cls.__pow__ = block_invalid_op      # type: ignore
        cls.__floordiv__ = block_invalid_op # type: ignore
        cls.__mod__ = block_invalid_op      # type: ignore
        cls._to_base_value = new_to_base  # type: ignore
        cls._from_base_value = new_from_base  # type: ignore
        cls.__mul__ = new_mul             # type: ignore
        cls.__rmul__ = new_rmul           # type: ignore
        cls.__truediv__ = new_truediv     # type: ignore
        cls.__rtruediv__ = new_rtruediv   # type: ignore

        return cls
    return decorator