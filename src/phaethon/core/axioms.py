"""
Defines a set of physical laws, constraints, and mathematical modifiers 
that dynamically govern the instantiation and conversion of Phaethon units.
It acts as a physics rule engine utilizing Python decorators.
"""
from __future__ import annotations

import inspect
import functools
from decimal import Decimal
from typing import Callable, Any, Literal, TYPE_CHECKING
import numpy as np

if TYPE_CHECKING:
    from .base import BaseUnit

from .compat import _T_Cls, _T_Fn, NumericLike, ContextDict
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

    def __add__(self, other: Any) -> CtxProxy:
        return CtxProxy(_evaluator=lambda c: self(c) + (other(c) if callable(other) else other))
    
    def __radd__(self, other: Any) -> CtxProxy:
        return CtxProxy(_evaluator=lambda c: (other(c) if callable(other) else other) + self(c))

    def __sub__(self, other: Any) -> CtxProxy:
        return CtxProxy(_evaluator=lambda c: self(c) - (other(c) if callable(other) else other))

    def __rsub__(self, other: Any) -> CtxProxy:
        return CtxProxy(_evaluator=lambda c: (other(c) if callable(other) else other) - self(c))

    def __mul__(self, other: Any) -> CtxProxy:
        return CtxProxy(_evaluator=lambda c: self(c) * (other(c) if callable(other) else other))

    def __rmul__(self, other: Any) -> CtxProxy:
        return CtxProxy(_evaluator=lambda c: (other(c) if callable(other) else other) * self(c))

    def __truediv__(self, other: Any) -> CtxProxy:
        return CtxProxy(_evaluator=lambda c: self(c) / (other(c) if callable(other) else other))

    def __rtruediv__(self, other: Any) -> CtxProxy:
        return CtxProxy(_evaluator=lambda c: (other(c) if callable(other) else other) / self(c))

    def __pow__(self, other: Any) -> CtxProxy:
        return CtxProxy(_evaluator=lambda c: self(c) ** (other(c) if callable(other) else other))

C = CtxProxy

# =========================================================================
# INTERNAL TYPE NORMALIZER (THE BULLETPROOF FUNNEL)
# =========================================================================
def _normalize_types(val_a: Any, val_b: Any) -> tuple[Any, Any]:
    """
    Aligns two variables for mathematical operations to prevent crashes.
    - If either is a NumPy array, Decimals are strictly cast to floats.
    - If neither is an array, floats are only cast to Decimals IF one is already a Decimal.
    """
    a_is_arr = HAS_NUMPY and isinstance(val_a, (np.ndarray, np.generic))
    b_is_arr = HAS_NUMPY and isinstance(val_b, (np.ndarray, np.generic))

    if a_is_arr or b_is_arr:
        if isinstance(val_a, Decimal): val_a = float(val_a)
        if isinstance(val_b, Decimal): val_b = float(val_b)
        return val_a, val_b
    
    has_decimal = isinstance(val_a, Decimal) or isinstance(val_b, Decimal)
    if has_decimal:
        if not isinstance(val_a, Decimal): val_a = Decimal(str(val_a))
        if not isinstance(val_b, Decimal): val_b = Decimal(str(val_b))
    
    return val_a, val_b


def bound(
    min_val: NumericLike | None = None, 
    max_val: NumericLike | None = None, 
    msg: str | None = None
) -> Callable[[_T_Cls], _T_Cls]:
    """
    Enforces physical boundary limits on a unit's magnitude during instantiation.
    Respects the 'default_on_error' strategy ('raise', 'coerce', 'clip').

    Args:
        min_val: The absolute minimum allowed value.
        max_val: The absolute maximum allowed value.
        msg: A custom error message thrown upon violation.

    Returns:
        A class decorator enforcing the boundary.
    """
    def decorator(cls: _T_Cls) -> _T_Cls:
        cls.__axiom_min__ = min_val  # type: ignore
        cls.__axiom_max__ = max_val  # type: ignore
        original_init = cls.__init__
        
        @functools.wraps(original_init)
        def new_init(self_obj: Any, value: int | float | Decimal | str | Any, context: dict[str, Any] | None = None) -> None:
            original_init(self_obj, value, context)
            val = self_obj._value
            
            from .config import get_config
            
            ignore_bound = self_obj.context.get("ignore_axiom_bound")
            if ignore_bound is None:
                ignore_bound = get_config("ignore_axiom_bound")
                
            if ignore_bound is True:
                return

            policy = self_obj.context.get("default_on_error") or get_config("default_on_error") or "raise"
            TOLERANCE = 1e-12 
            
            if HAS_NUMPY and isinstance(val, (np.ndarray, np.generic)):
                violated_min = min_val is not None and np.any(val < (float(min_val) - TOLERANCE))
                violated_max = max_val is not None and np.any(val > (float(max_val) + TOLERANCE))
                
                if violated_min or violated_max:
                    if policy == "raise":
                        if violated_min: raise AxiomViolationError(msg or f"Array contains values strictly less than {min_val}")
                        if violated_max: raise AxiomViolationError(msg or f"Array contains values strictly greater than {max_val}")
                        
                    elif policy in ("null", "coerce"):
                        new_val = np.array(val, dtype=float)
                        if min_val is not None:
                            new_val = np.where(new_val < float(min_val), np.nan, new_val)
                        if max_val is not None:
                            new_val = np.where(new_val > float(max_val), np.nan, new_val)
                        self_obj._value = new_val
                        
                    elif policy == "clip":
                        a_min = float(min_val) if min_val is not None else None
                        a_max = float(max_val) if max_val is not None else None
                        self_obj._value = np.clip(val, a_min, a_max)
                        
            else:
                violated_min = min_val is not None and val < Decimal(str(min_val))
                violated_max = max_val is not None and val > Decimal(str(max_val))
                
                if violated_min or violated_max:
                    if policy == "raise":
                        if violated_min: raise AxiomViolationError(msg or f"Value cannot be strictly less than {min_val}")
                        if violated_max: raise AxiomViolationError(msg or f"Value cannot be strictly greater than {max_val}")
                        
                    elif policy in ("null", "coerce"):
                        self_obj._value = Decimal('NaN') if isinstance(val, Decimal) else float('nan')
                        
                    elif policy == "clip":
                        if violated_min:
                            self_obj._value = type(val)(str(min_val)) if isinstance(val, Decimal) else type(val)(min_val)
                        elif violated_max:
                            self_obj._value = type(val)(str(max_val)) if isinstance(val, Decimal) else type(val)(max_val)

        cls.__init__ = new_init  # type: ignore
        return cls
    return decorator


def shift(
    ctx: str | None = None, 
    default: NumericLike = 0.0, 
    op: Literal["add", "sub"] = "add", 
    formula: Callable[[ContextDict], NumericLike] | None = None
) -> Callable[[_T_Cls], _T_Cls]:
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
    def decorator(cls: _T_Cls) -> _T_Cls:
        orig_to_base = getattr(cls, '_to_base_value')
        orig_from_base = getattr(cls, '_from_base_value')

        def get_ctx_val(context: dict[str, Any]) -> Decimal | Any:
            res = default
            if formula:
                if isinstance(formula, CtxProxy):
                    res = formula(context)
                    if hasattr(res, '_to_base_value'):
                        res = res._to_base_value()
                else:
                    sig = inspect.signature(formula)
                    kwargs = {}
                    for param_name, param in sig.parameters.items():
                        if param_name in context:
                            val = context[param_name]
                            
                            if hasattr(val, 'to') and hasattr(val, 'mag'):
                                pass 
                            elif isinstance(val, Decimal):
                                val = float(val)
                            kwargs[param_name] = val
                            
                        elif param.default is not inspect.Parameter.empty:
                            kwargs[param_name] = param.default
                        else:
                            kwargs[param_name] = None
                    res = formula(**kwargs)
            elif ctx:
                val = context.get(ctx, default)
                if hasattr(val, '_to_base_value'):
                    val = val._to_base_value()
                res = val

            if HAS_NUMPY and isinstance(res, (np.ndarray, np.generic)):
                return res
            if isinstance(res, Decimal):
                return res
            return Decimal(str(res))

        def new_to_base(self_obj: Any) -> Decimal | Any:
            base_val = orig_to_base(self_obj)
            ctx_val = get_ctx_val(self_obj.context)
            
            base_val, ctx_val = _normalize_types(base_val, ctx_val)
            
            if op == "add": return base_val + ctx_val
            elif op == "sub": return base_val - ctx_val
            return base_val

        @classmethod
        def new_from_base(cls_obj: type, base_val: Decimal | Any, context: dict[str, Any]) -> Decimal | Any:
            ctx_val = get_ctx_val(context)
            
            base_val, ctx_val = _normalize_types(base_val, ctx_val)
            
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
    formula: Callable[[ContextDict], NumericLike] | None = None
) -> Callable[[_T_Cls], _T_Cls]:
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
    def decorator(cls: _T_Cls) -> _T_Cls:
        orig_to_base = getattr(cls, '_to_base_value')
        orig_from_base = getattr(cls, '_from_base_value')

        def get_ctx_val(context: dict[str, Any]) -> Decimal | Any:
            res = default
            if formula:
                if isinstance(formula, CtxProxy):
                    res = formula(context)
                    if hasattr(res, '_to_base_value'):
                        res = res._to_base_value()
                else:
                    sig = inspect.signature(formula)
                    kwargs = {}
                    for param_name, param in sig.parameters.items():
                        if param_name in context:
                            val = context[param_name]
                            
                            if hasattr(val, 'to') and hasattr(val, 'mag'):
                                pass 
                            elif isinstance(val, Decimal):
                                val = float(val)
                            kwargs[param_name] = val
                            
                        elif param.default is not inspect.Parameter.empty:
                            kwargs[param_name] = param.default
                        else:
                            kwargs[param_name] = None
                    res = formula(**kwargs)
            elif ctx:
                val = context.get(ctx, default)
                if hasattr(val, '_to_base_value'):
                    val = val._to_base_value()
                res = val

            if HAS_NUMPY and isinstance(res, (np.ndarray, np.generic)):
                return res
            if isinstance(res, Decimal):
                return res
            return Decimal(str(res))

        def new_to_base(self_obj: Any) -> Decimal | Any:
            base_val = orig_to_base(self_obj)
            ctx_val = get_ctx_val(self_obj.context)
            
            base_val, ctx_val = _normalize_types(base_val, ctx_val)
                
            return base_val * ctx_val

        @classmethod
        def new_from_base(cls_obj: type, base_val: Decimal | Any, context: dict[str, Any]) -> Decimal | Any:
            ctx_val = get_ctx_val(context)
            
            base_val, ctx_val = _normalize_types(base_val, ctx_val)
                
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
) -> Callable[[_T_Cls], _T_Cls]:
    """
    A class decorator for Dimensional Synthesis.
    
    Synthesizes a new physical unit by deriving its dimensional signature and 
    base multiplier from an algebraic expression of existing units.
    
    Supports direct Metaclass algebra (preferred) or explicit mul/div lists.
    
    Example:
        >>> # Modern Metaclass Syntax (V0.2.0+)
        >>> @derive(u.Joule / u.Meter)
        >>> class Newton(ForceUnit): 
        >>>    symbol = "N"
            
        >>> # Legacy Syntax
        >>> @derive(mul=[u.Joule], div=[u.Meter])
        >>> class Newton(ForceUnit): 
        >>>    symbol = "N"
    """
    def decorator(cls: _T_Cls) -> _T_Cls:
        if unit_expr is not None:
            cls.base_multiplier = getattr(unit_expr, 'base_multiplier', Decimal('1.0'))  # type: ignore
            cls.base_offset = getattr(unit_expr, 'base_offset', 0.0)  # type: ignore

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
        
        multiplier = Decimal('1.0')
        
        for item in mul_list:
            if isinstance(item, (int, float, Decimal, str)):
                multiplier *= Decimal(str(item))
            else:
                multiplier *= Decimal(str(getattr(item, 'base_multiplier', 1.0)))
                
        for item in div_list:
            if isinstance(item, (int, float, Decimal, str)):
                val = Decimal(str(item))
            else:
                val = Decimal(str(getattr(item, 'base_multiplier', 1.0)))
                
            if val == 0:
                raise ZeroDivisionError(f"Base multiplier cannot be zero in derive for {cls.__name__}.")
            multiplier /= val
            
        cls.base_offset = 0.0  # type: ignore
        cls.base_multiplier = multiplier  # type: ignore
        return cls
        
    return decorator


def require(**dim_or_class: str | type) -> Callable[[_T_Fn], _T_Fn]:
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
    def decorator(func: _T_Fn) -> _T_Fn:
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

def prepare(**unit_mappings: type[BaseUnit]) -> Callable[[_T_Fn], _T_Fn]:
    """
    Pre-processes formula arguments for pure mathematical functions.
    Automatically intercepts Phaethon objects, converts them to the specified 
    target unit, and extracts their raw magnitude (.mag) before execution.
    """
    def decorator(func: _T_Fn) -> _T_Fn:
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