from __future__ import annotations

import sys
from contextvars import ContextVar
from contextlib import contextmanager
from typing import Any, Generator
from .compat import ContextDict, AliasRegistry, ErrorAction

_GLB = "__phaethon_global__"
_CTX = "__phaethon_context__"

def _global() -> ContextDict:
    if _GLB not in sys.modules:
        sys.modules[_GLB] = {
            "decimal_mark": ".",
            "thousands_sep": ",",
            "default_on_error": "raise",
            "ignore_axiom_bound": False,
            "aliases": {},
            "context": {}
        }
    return sys.modules[_GLB]

def _context() -> ContextVar[dict[str, Any]]:
    if _CTX not in sys.modules:
        sys.modules[_CTX] = ContextVar("PHAETHON_CONTEXT", default={})
    return sys.modules[_CTX]

def config(
    decimal_mark: str | None = None,
    thousands_sep: str | None = None,
    default_on_error: ErrorAction | None = None,
    ignore_axiom_bound: bool | None = None,
    aliases: AliasRegistry | None = None,
    context: ContextDict | None = None
) -> None:
    """
    Configures the global behavior of the Phaethon data normalization engine.

    Args:
        decimal_mark: The character used to denote the decimal place (e.g., "." or ",").
        thousands_sep: The character used to separate thousands (e.g., "," or ".").
        default_on_error: Global strategy for handling physical axiom violations and limits.
            - 'raise': (Default) Halts execution and throws an AxiomViolationError.
            - 'coerce': Silently neutralizes invalid/out-of-bounds data into NaN or None.
            - 'clip': Forces values to stay within specified min/maxlimits or inherent axiom.bound if limits are undefined.
        ignore_axiom_bound: If True, completely disables innate physical limits (e.g., Absolute Zero).
        aliases: A dictionary mapping official Phaethon unit symbols to custom user strings.
            Format: {"official_symbol": ["dirty_string_1", "dirty_string_2"]}
            Example: {"kg": ["kilos", "kilogramme"]}
        context: A flat dictionary for injecting dynamic environmental variables at runtime.
            Used for volatile states like financial exchange rates or physical constants.
            Example: {"usd_to_idr": 15500, "atmospheric_pressure": 101325}
    """
    updates = {k: v for k, v in locals().items() if v is not None and k != "context"}
    _global().update(updates)
    
    if context is not None:
        _global()["context"].update(context)

@contextmanager
def using(
    decimal_mark: str | None = None,
    thousands_sep: str | None = None,
    default_on_error: ErrorAction | None = None,
    ignore_axiom_bound: bool | None = None,
    aliases: AliasRegistry | None = None,
    context: ContextDict | None = None
) -> Generator[None, None, None]:
    """
    Temporarily overrides the global Phaethon configuration within a context block.
    Safe for concurrent execution and asynchronous environments.

    Args:
        decimal_mark: The character used to denote the decimal place (e.g., "." or ",").
        thousands_sep: The character used to separate thousands (e.g., "," or ".").
        default_on_error: Global strategy for handling physical axiom violations and limits.
            - 'raise': (Default) Halts execution and throws an AxiomViolationError.
            - 'coerce': Silently neutralizes invalid/out-of-bounds data into NaN or None.
            - 'clip': Forces values to stay within specified min/maxlimits or inherent axiom.bound if limits are undefined.
        ignore_axiom_bound: If True, completely disables innate physical limits (e.g., Absolute Zero).
        aliases: A dictionary mapping official Phaethon unit symbols to custom user strings.
            Format: {"official_symbol": ["dirty_string_1", "dirty_string_2"]}
            Example: {"kg": ["kilos", "kilogramme"]}
        context: A flat dictionary for injecting dynamic environmental variables at runtime.
            Used for volatile states like financial exchange rates or physical constants.
            Example: {"usd_to_idr": 15500, "atmospheric_pressure": 101325}
    """
    ctx_var = _context()
    current = ctx_var.get().copy()
    
    updates = {k: v for k, v in locals().items() if k not in ("ctx_var", "current", "context") and v is not None}
    new_context_state = {**current, **updates}
    
    if context is not None:
        existing_ctx_dict = new_context_state.get("context", {}).copy()
        existing_ctx_dict.update(context)
        new_context_state["context"] = existing_ctx_dict
    
    token = ctx_var.set(new_context_state)
    try:
        yield
    finally:
        ctx_var.reset(token)

def get_config(key: str, field_override: Any | None = None) -> Any:
    """
    Resolves the configuration value based on the precedence hierarchy.
    """
    if field_override is not None:
        return field_override
        
    ctx_dict = _context().get()
    
    if "context" in ctx_dict and key in ctx_dict["context"]:
        return ctx_dict["context"][key]
        
    if key in ctx_dict:
        return ctx_dict[key]
        
    glb = _global()
    if "context" in glb and key in glb["context"]:
        return glb["context"][key]
        
    return glb.get(key)

def get_merged_context(field_context: ContextDict | None = None) -> ContextDict:
    merged = _global().get("context", {}).copy()
    
    ctx_dict = _context().get()
    if "context" in ctx_dict and ctx_dict["context"]:
        merged.update(ctx_dict["context"])
    
    if field_context:
        merged.update(field_context)
    
    return merged