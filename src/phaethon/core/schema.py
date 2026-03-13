from __future__ import annotations

import re
from typing import (
    Callable, TYPE_CHECKING, Any, TypedDict
)

from .backends import PandasBackend, PolarsBackend
from .registry import ureg
from .compat import (
    DataFrameLike, is_pandas_df, is_polars_df, _T_DF, ErrorAction,
    UnitLike, ColumnTarget, AliasRegistry, ContextDict, ImputeMethod,
    NumericLike
)

if TYPE_CHECKING:
    from .base import BaseUnit

# 🌟 Tipe khusus untuk bounds di Schema (Angka murni atau string dengan satuan fisik)
_PhysicalBound = NumericLike | str | None

class _ExprNode:
    """
    An Abstract Syntax Tree (AST) node representing a deferred mathematical 
    expression for DerivedFields. Evaluated dynamically by the active Backend.
    """
    def __init__(self, evaluator: Callable[[DataFrameLike, str], Any]) -> None:
        self.evaluator = evaluator
        
    def __call__(self, df: DataFrameLike, backend: str) -> Any:
        return self.evaluator(df, backend)
        
    def __add__(self, other: _ExprNode | Any) -> _ExprNode:
        return _ExprNode(lambda df, b: self(df, b) + (other(df, b) if isinstance(other, _ExprNode) else other))
        
    def __sub__(self, other: _ExprNode | Any) -> _ExprNode:
        return _ExprNode(lambda df, b: self(df, b) - (other(df, b) if isinstance(other, _ExprNode) else other))
        
    def __mul__(self, other: _ExprNode | Any) -> _ExprNode:
        return _ExprNode(lambda df, b: self(df, b) * (other(df, b) if isinstance(other, _ExprNode) else other))
        
    def __truediv__(self, other: _ExprNode | Any) -> _ExprNode:
        return _ExprNode(lambda df, b: self(df, b) / (other(df, b) if isinstance(other, _ExprNode) else other))
        
    def __pow__(self, other: _ExprNode | Any) -> _ExprNode:
        return _ExprNode(lambda df, b: self(df, b) ** (other(df, b) if isinstance(other, _ExprNode) else other))
        
    def __radd__(self, other: _ExprNode | Any) -> _ExprNode:
        return _ExprNode(lambda df, b: (other(df, b) if isinstance(other, _ExprNode) else other) + self(df, b))
        
    def __rsub__(self, other: _ExprNode | Any) -> _ExprNode:
        return _ExprNode(lambda df, b: (other(df, b) if isinstance(other, _ExprNode) else other) - self(df, b))
        
    def __rmul__(self, other: _ExprNode | Any) -> _ExprNode:
        return _ExprNode(lambda df, b: (other(df, b) if isinstance(other, _ExprNode) else other) * self(df, b))
        
    def __rtruediv__(self, other: _ExprNode | Any) -> _ExprNode:
        return _ExprNode(lambda df, b: (other(df, b) if isinstance(other, _ExprNode) else other) / self(df, b))

class _FieldBlueprint(TypedDict):
    type: str
    source_column: str | None
    target: str
    bounds: str
    imputation: str
    fuzzy_match: bool
    target_unit: str | None

def col(name: str) -> _ExprNode:
    """
    References a cleaned column for use within a DerivedField formula.
    Seamlessly translates to `pl.col()` in Polars or `df['name']` in Pandas.

    Args:
        name: The name of the target column that has already been normalized 
            in the first pass of the Schema pipeline.

    Returns:
        An _ExprNode representing the deferred column evaluation.

    Example:
        >>> power: u.Watt = ptn.DerivedField(formula=ptn.col("volts") * ptn.col("amps"))
    """
    def _eval(df: DataFrameLike, backend: str) -> Any:
        if backend == 'polars':
            import polars as pl
            return pl.col(name)
        else:
            return df[name]
    return _ExprNode(_eval)

def pre_normalize(func: Callable[[type[Schema], _T_DF], _T_DF]) -> Callable[[type[Schema], _T_DF], _T_DF]:
    """
    Decorator to register a method as a pre-normalization lifecycle hook.
    Executed before any Phaethon physics validation or conversion occurs.
    
    The hooked method receives the raw DataFrame and must return a DataFrame.
    """
    func.__is_phaethon_pre_hook__ = True # type: ignore
    return func

def post_normalize(func: Callable[[type[Schema], _T_DF], _T_DF]) -> Callable[[type[Schema], _T_DF], _T_DF]:
    """
    Decorator to register a method as a post-normalization lifecycle hook.
    Executed after all schema fields and derived formulas have been fully processed.
    
    The hooked method receives the cleaned DataFrame and must return a DataFrame.
    """
    func.__is_phaethon_post_hook__ = True # type: ignore
    return func

class Field:
    """
    Defines a column-level validation, extraction, and conversion rule within a Schema.
    """
    def __init__(
        self, 
        source: ColumnTarget = ...,
        source_unit: UnitLike | None = None,
        unit_col: str | None = None,
        parse_string: bool = False,
        min: _PhysicalBound = None, 
        max: _PhysicalBound = None, 
        round: int | None = None,
        on_error: ErrorAction | None = None,
        ignore_axiom_bound: bool | None = None,
        decimal_mark: str | None = None,
        thousands_sep: str | None = None,
        aliases: AliasRegistry | None = None,
        impute_by: ImputeMethod | None = None,
        outlier_std: float | None = None,
        context: ContextDict | None = None,
        fuzzy_match: bool = False,
        confidence: float = 0.85,
        target_unit: type[BaseUnit] | None = None
    ) -> None:
        """
        Defines a column-level validation, extraction, and conversion rule within a Schema.

        Args:
            source: The name of the raw column. Defaults to `...` (Ellipsis) to auto-map to the variable name.
            source_unit: The default unit class or string alias if the data lacks unit tags.
            unit_col: The name of a separate column containing the unit strings.
            parse_string: If True, uses regex to extract values and units from mixed text.
            min: The absolute minimum allowed magnitude. Can be a number or a physical string (e.g., '10 kg').
            max: The absolute maximum allowed magnitude. Can be a number or a physical string (e.g., '120 lbs').
            round: Number of decimal places to round the final output.
            on_error: Strategy for handling physical bounds violations or unparseable data.
                - 'raise': Halts execution and throws an error.
                - 'coerce': Converts invalid values strictly to `NaN` (useful for imputation later).
                - 'clip': Forces out-of-bounds values to the specified `min` or `max` limits.
            ignore_axiom_bound: If True, completely disables innate physical limits (e.g., Absolute Zero).
            decimal_mark: Override the global decimal mark (e.g., ',' for European formats).
            thousands_sep: Override the global thousands separator.
            aliases: Provide custom local unit aliases mapping to official symbols.
            impute_by: Strategy to fill NaN values ('mean', 'median', 'mode', 'ffill', 'bfill', or a constant physical string like '10 kg').
            outlier_std: Z-Score threshold to drop statistical anomalies (e.g., 3.0).
            context: A dictionary of environmental variables (e.g., exchange rates, temperature) to inject into dynamic Axioms for this specific field.
            fuzzy_match: If True, uses string metrics to auto-correct typos in unit strings or semantic categories.
            confidence: The minimum similarity score (0.0 to 1.0) required to accept a fuzzy match. Defaults to 0.85 (85%).
            target_unit: Internally populated via class annotations. Do not set manually.
        """
        self.source = source
        self.source_unit = source_unit
        self.unit_col = unit_col
        self.parse_string = parse_string
        self.min = min
        self.max = max
        self.round = round
        self.on_error = on_error
        self.ignore_axiom_bound = ignore_axiom_bound
        self.context = context or {}
        self.target_unit = target_unit 
        self.decimal_mark = decimal_mark
        self.thousands_sep = thousands_sep
        self.aliases = aliases
        self.impute_by = impute_by
        self.outlier_std = outlier_std
        self.fuzzy_match = fuzzy_match
        self.confidence = confidence

class DerivedField:
    """
    Synthesizes a new Machine Learning feature using cross-column dimensional algebra.
    Evaluated in the second pass of the pipeline, utilizing clean data from standard Fields.
    """
    def __init__(
        self,
        formula: _ExprNode,
        round: int | None = None,
        target_unit: type[BaseUnit] | None = None
    ) -> None:
        """
        Args:
            formula: A mathematical expression constructed using `ptn.col()`.
            round: Number of decimal places to round the final synthesized output.
            target_unit: Internally populated via class annotations. Do not set manually.

        Example:
            >>> speed: u.MeterPerSecond = ptn.DerivedField(formula=ptn.col('distance') / ptn.col('time'))
        """
        self.formula = formula
        self.round = round
        self.target_unit = target_unit

class SchemaMeta(type):
    """Metaclass that automatically binds type hints to Schema Fields."""
    def __new__(mcs, name: str, bases: tuple[type, ...], namespace: dict[str, Any]) -> SchemaMeta:
        cls = super().__new__(mcs, name, bases, namespace)
        fields = {k: v for k, v in namespace.items() if isinstance(v, (Field, DerivedField))}
        annotations = getattr(cls, '__annotations__', {})
        
        for key, field in fields.items():
            if getattr(field, 'source', None) is Ellipsis:
                field.source = key
                
            if key in annotations:
                field.target_unit = annotations[key]
            elif getattr(field, 'target_unit', None) is not None:
                pass
            else:
                raise TypeError(f"Field '{key}' requires a unit target. Use type hinting.")
                
        cls.__phaethon_fields__ = fields
        return cls

class Schema(metaclass=SchemaMeta):
    """
    Declarative base class for defining dimensional data normalization pipelines.
    Supports both Pandas and Polars DataFrames automatically.

    Subclass this and define class attributes using `ptn.Field` and `ptn.DerivedField` 
    with type hints mapping to Phaethon target units.
    """
    __phaethon_fields__: dict[str, Field | DerivedField]

    @classmethod
    def _parse_physical_bound(
        cls, 
        bound_val: _PhysicalBound, 
        target_unit: type[BaseUnit], 
        aliases: AliasRegistry | None = None
    ) -> float:
        """Internal helper to convert string boundaries ('50 kg') into physical floats."""
        if bound_val is None:
            return float('inf') # Safe fallback, though calling functions should check for None
            
        if isinstance(bound_val, str):
            bound_str = bound_val
            
            if aliases:
                for official_key, dirty_vals in aliases.items():
                    if not isinstance(dirty_vals, list):
                        dirty_vals = [dirty_vals]
                    for v in dirty_vals:
                        bound_str = re.sub(rf'\b{re.escape(v)}\b', official_key, bound_str)

            match = re.match(r'^\s*([-+]?[0-9]*\.?[0-9]+(?:[eE][-+]?[0-9]+)?)\s*(.+?)\s*$', bound_str)
            if match:
                val = float(match.group(1))
                u_str = match.group(2)
                source_cls = ureg().get_unit_class(u_str, expected_dim=getattr(target_unit, 'dimension', None))
                return source_cls(val).to(target_unit).mag
                
        return float(bound_val) # type: ignore
        
    @classmethod
    def normalize(cls, df: _T_DF, keep_unmapped: bool = False, drop_raw: bool = True) -> _T_DF:
        """
        Executes the normalization pipeline against the provided DataFrame.

        Args:
            df: The dirty Pandas or Polars DataFrame.
            keep_unmapped: If True, retains columns from the original DataFrame that are not defined in the schema.
            drop_raw: If True, drops the original source columns after they have been mapped to target fields.

        Returns:
            A cleaned DataFrame (matching the input backend) with all units strictly standardized and validated.
        """
        if is_pandas_df(df):
            working_df = df.copy()
            backend = PandasBackend() # type: ignore
        elif is_polars_df(df):
            working_df = df.clone()
            backend = PolarsBackend() # type: ignore
        else:
            raise TypeError(f"Unsupported DataFrame backend: {type(df)}")

        # 1. Execute Pre-Hooks
        for attr_name in dir(cls):
            attr = getattr(cls, attr_name)
            if getattr(attr, '__is_phaethon_pre_hook__', False):
                working_df = attr(cls, working_df)
        
        # 2. Execute Main Engine (Semantic + Physics + Derivation)
        clean_df = backend.normalize(working_df, cls.__phaethon_fields__, cls, keep_unmapped, drop_raw)

        # 3. Execute Post-Hooks
        for attr_name in dir(cls):
            attr = getattr(cls, attr_name)
            if getattr(attr, '__is_phaethon_post_hook__', False):
                clean_df = attr(cls, clean_df)
            
        return clean_df
    
    @classmethod
    def blueprint(cls) -> dict[str, _FieldBlueprint]:
        """
        Generates a structural JSON-serializable blueprint of the schema 
        for Data Governance and automated Data Catalogs.
        """
        schema_info = {}
        for name, field in cls.__phaethon_fields__.items():
            if type(field).__name__ == "DerivedField":
                schema_info[name] = {
                    "type": "Derived Feature (ML)",
                    "target_unit": getattr(field.target_unit, '__name__', str(field.target_unit)),
                    "source_column": None,
                    "bounds": "Unlimited",
                    "imputation": "None",
                    "fuzzy_match": False
                }
            else:
                is_semantic = hasattr(field.target_unit, 'classify')
                is_onto = hasattr(field.target_unit, 'match')
                
                ftype = "Semantic State" if is_semantic else ("Ontology" if is_onto else "Physical Dimension")
                
                schema_info[name] = {
                    "type": ftype,
                    "source_column": getattr(field, 'source', None),
                    "target": getattr(field.target_unit, '__name__', str(field.target_unit)),
                    "bounds": f"{getattr(field, 'min', None)} to {getattr(field, 'max', None)}" if (getattr(field, 'min', None) or getattr(field, 'max', None)) else "Unlimited",
                    "imputation": getattr(field, 'impute_by', None) or "None",
                    "fuzzy_match": getattr(field, 'fuzzy_match', False),
                    "target_unit": None
                }
        return schema_info # type: ignore