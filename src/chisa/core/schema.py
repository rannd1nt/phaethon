import pandas as pd
import numpy as np
from typing import Literal, Dict, Optional, Type, Union, Callable
from .registry import default_ureg
from ..exceptions import AxiomViolationError, NormalizationError, UnitNotFoundError, DimensionMismatchError

def pre_normalize(func: Callable[[pd.DataFrame], pd.DataFrame]) -> Callable[[pd.DataFrame], pd.DataFrame]:
    """
    Decorator to register a method as a pre-normalization hook.
    The hooked method will be executed before any data parsing or conversion occurs.
    """
    func.__is_chisa_pre_hook__ = True
    return func

def post_normalize(func: Callable[[pd.DataFrame], pd.DataFrame]) -> Callable[[pd.DataFrame], pd.DataFrame]:
    """
    Decorator to register a method as a post-normalization hook.
    The hooked method will be executed after all schema fields have been processed.
    """
    func.__is_chisa_post_hook__ = True
    return func

class Field:
    """
    Defines a column-level validation and conversion rule within a Chisa Schema.
    
    A Field maps a source column from a raw DataFrame to a strongly-typed 
    physical dimension, dictating how to parse, validate, and convert the data.
    """
    def __init__(
        self, 
        source: str, 
        source_unit: Optional[Union[Type, str]] = None, 
        unit_col: Optional[str] = None,
        parse_string: bool = False,
        min: Optional[float] = None, 
        max: Optional[float] = None, 
        round: Optional[int] = None,
        on_error: Literal['raise', 'coerce'] = 'raise',
        context: Optional[Dict[str, str]] = None,
        target_unit: Optional[Type] = None
    ):
        """
        Args:
            source: The name of the column in the raw DataFrame.
            source_unit: The default unit of the source data if no unit string is provided.
            unit_col: The name of a separate column containing the unit strings.
            parse_string: If True, extracts numeric values and units from mixed string data.
            min: The minimum allowed value for the final output data.
            max: The maximum allowed value for the final output data.
            round: The number of decimal places to round the output to.
            on_error: Strategy for handling invalid data or physics violations ('raise' or 'coerce').
            context: Additional physical context variables (e.g., temperature) for dynamic units.
            target_unit: Explicit target unit class (usually inferred automatically via type hints).
        """
        self.source = source
        self.source_unit = source_unit
        self.unit_col = unit_col
        self.parse_string = parse_string
        self.min = min
        self.max = max
        self.round = round
        self.on_error = on_error
        self.context = context or {}
        self.target_unit = target_unit 

class SchemaMeta(type):
    def __new__(mcs, name, bases, namespace):
        cls = super().__new__(mcs, name, bases, namespace)
        fields = {k: v for k, v in namespace.items() if isinstance(v, Field)}
        annotations = getattr(cls, '__annotations__', {})
        
        for key, field in fields.items():
            if key in annotations:
                field.target_unit = annotations[key]
            elif getattr(field, 'target_unit', None) is not None:
                pass
            else:
                raise TypeError(f"Field '{key}' requires a unit target. Use type hinting.")
                
        cls._fields = fields
        return cls

class Schema(metaclass=SchemaMeta):
    """
    Base class for defining declarative data normalization pipelines.
    
    Subclass this to define a schema using Field descriptors. The schema will
    automatically extract, convert, and validate messy DataFrame columns into
    clean, uniform dimensional arrays using high-speed vectorization.
    """
    @classmethod
    def normalize(cls, df: pd.DataFrame, keep_unmapped: bool = False, drop_raw: bool = True) -> pd.DataFrame:
        """
        Executes the normalization pipeline on a given DataFrame.

        Args:
            df: The raw input DataFrame.
            keep_unmapped: If True, retains original metadata columns that are not mapped in the schema.
            drop_raw: If True, drops the original source columns that were mapped, keeping only target columns.

        Returns:
            A new DataFrame containing the cleaned, scaled, and validated data.
        """
        working_df = df.copy()

        # --- Stage 0: Execute Pre-Hooks ---
        for attr_name in dir(cls):
            attr = getattr(cls, attr_name)
            if getattr(attr, '__is_chisa_pre_hook__', False):
                working_df = attr(cls, working_df)

        clean_df = pd.DataFrame()
        clean_df.index = working_df.index 
        
        for field_name, field in cls._fields.items():
            if field.source not in working_df.columns:
                raise KeyError(f"Source column '{field.source}' not found.")
            
            target_dim = getattr(field.target_unit, 'dimension', None)
            raw_series = working_df[field.source]
            
            isna_mask = raw_series.isna()
            if raw_series.dtype == object:
                isna_mask = isna_mask | (raw_series.astype(str).str.strip() == "")
            
            result_array = np.full(len(raw_series), np.nan, dtype=float)

            if isna_mask.all():
                clean_df[field_name] = result_array
                continue

            # --- Stage 1: Extraction ---
            values_array = np.full(len(raw_series), np.nan, dtype=float)
            units_array = None
            
            if field.parse_string:
                extracted = raw_series.astype(str).str.extract(r'^\s*([-+]?[0-9]*\.?[0-9]+(?:[eE][-+]?[0-9]+)?)\s*(.+?)\s*$')
                values_array = pd.to_numeric(extracted[0], errors='coerce').values
                units_array = extracted[1].values
            
            elif field.unit_col:
                values_array = pd.to_numeric(raw_series, errors='coerce').values
                units_array = working_df[field.unit_col].astype(str).values
            else:
                values_array = pd.to_numeric(raw_series, errors='coerce').values

            # --- Stage 2: Vectorized Conversion ---
            if units_array is not None:
                unique_units = pd.Series(units_array).dropna().unique()
                for u_str in unique_units:
                    if str(u_str).strip().lower() in ['nan', 'none', '']: continue
                    
                    mask = (units_array == u_str) & (~isna_mask)
                    if not mask.any(): continue
                    
                    try:
                        source_cls = default_ureg.get_unit_class(u_str, expected_dim=target_dim)
                        raw_masked = values_array[mask].astype(float)
                        
                        # --- Vectorized Pre-Filtering ---
                        axiom_min = getattr(source_cls, '__axiom_min__', None)
                        axiom_max = getattr(source_cls, '__axiom_max__', None)
                        
                        if axiom_min is not None:
                            violators = raw_masked < float(axiom_min)
                            if violators.any():
                                if field.on_error == 'raise':
                                    raise AxiomViolationError(f"Raw data '{u_str}' violates min bound of {axiom_min}")
                                raw_masked[violators] = np.nan
                                
                        if axiom_max is not None:
                            violators = raw_masked > float(axiom_max)
                            if violators.any():
                                if field.on_error == 'raise':
                                    raise AxiomViolationError(f"Raw data '{u_str}' violates max bound of {axiom_max}")
                                raw_masked[violators] = np.nan
                        
                        source_instances = source_cls(raw_masked)
                        target_instances = source_instances.to(field.target_unit)
                        result_array[mask] = target_instances.mag
                        
                    except UnitNotFoundError:
                        if field.on_error == 'raise':
                            bad_indices = working_df.index[mask].tolist()
                            raw_sample = raw_series.loc[bad_indices[0]] if len(bad_indices) > 0 else u_str
                            
                            clean_u_str = str(u_str).strip()
                            if clean_u_str.isnumeric() or clean_u_str == "":
                                issue_msg = "Missing or malformed unit string."
                            else:
                                issue_msg = f"Unrecognized unit '{u_str}'."
                                
                            raise NormalizationError(
                                field=field_name, 
                                issue=issue_msg, 
                                indices=bad_indices,
                                raw_sample=str(raw_sample),
                                expected_dim=str(target_dim) if target_dim else "unknown",
                                suggestion="Fix the raw data, register the unit alias, or set Field(on_error='coerce')."
                            )
                            
                    except DimensionMismatchError as e:
                        if field.on_error == 'raise':
                            bad_indices = working_df.index[mask].tolist()
                            raw_sample = raw_series.loc[bad_indices[0]] if len(bad_indices) > 0 else "unknown"
                            
                            raise NormalizationError(
                                field=field_name, 
                                issue=str(e), 
                                indices=bad_indices,
                                raw_sample=str(raw_sample),
                                expected_dim=str(target_dim) if target_dim else "unknown",
                                suggestion=f"Check the source data. Expected '{target_dim}' but received a completely different dimension."
                            )
                            
                    except Exception as e:
                        if field.on_error == 'raise':
                            bad_indices = working_df.index[mask].tolist()
                            raw_sample = raw_series.loc[bad_indices[0]] if len(bad_indices) > 0 else "unknown"
                            
                            suggestion = "Verify data formatting or set Field(on_error='coerce')."
                            if isinstance(e, AxiomViolationError):
                                suggestion = "Data violates physical boundaries. Consider relaxing Schema bounds or cleaning upstream data."
                                
                            raise NormalizationError(
                                field=field_name, 
                                issue=str(e), 
                                indices=bad_indices,
                                raw_sample=str(raw_sample),
                                expected_dim=str(target_dim) if target_dim else "unknown",
                                suggestion=suggestion
                            )
            else:
                mask = ~isna_mask
                if mask.any():
                    if field.source_unit is None and not field.unit_col:
                        if field.on_error == 'raise':
                            bad_indices = working_df.index[mask].tolist()
                            raw_sample = raw_series.loc[bad_indices[0]] if len(bad_indices) > 0 else "unknown"
                            
                            raise NormalizationError(
                                field=field_name,
                                issue="Missing 'source_unit' definition in Schema.",
                                indices=bad_indices,
                                raw_sample=str(raw_sample),
                                expected_dim=str(target_dim) if target_dim else "unknown",
                                suggestion="Set 'parse_string=True' to parse text like '10 kg', or provide 'source_unit' if the data is purely numeric."
                            )
                        else:
                            pass
                    else:
                        try:
                            source_cls = field.source_unit
                            if isinstance(source_cls, str):
                                source_cls = default_ureg.get_unit_class(source_cls, expected_dim=target_dim)
                            
                            raw_masked = values_array[mask]
                            source_instances = source_cls(raw_masked)
                            target_instances = source_instances.to(field.target_unit)
                            result_array[mask] = target_instances.mag
                        except Exception as e:
                            if field.on_error == 'raise':
                                bad_indices = working_df.index[mask].tolist()
                                raw_sample = raw_series.loc[bad_indices[0]] if len(bad_indices) > 0 else "unknown"
                                raise NormalizationError(
                                    field=field_name,
                                    issue=str(e),
                                    indices=bad_indices,
                                    raw_sample=str(raw_sample),
                                    expected_dim=str(target_dim) if target_dim else "unknown",
                                    suggestion="Check upstream data formatting or set Field(on_error='coerce')."
                                )

            # --- Stage 2.5: Safety Net for Regex Rejected Data ---
            if field.on_error == 'raise':
                unprocessed_mask = (~isna_mask) & np.isnan(result_array)
                if unprocessed_mask.any():
                    bad_indices = working_df.index[unprocessed_mask].tolist()
                    raw_sample = raw_series.loc[bad_indices[0]]
                    
                    if not field.parse_string:
                        issue_msg = "Data contains non-numeric characters but 'parse_string' is False."
                        suggestion_msg = "Set Field(parse_string=True) to extract numbers from text, or clean upstream data."
                    else:
                        issue_msg = "Data format rejected by parser (missing unit or invalid text)."
                        suggestion_msg = "Ensure the data contains both a number and a valid unit (e.g., '10 kg') or set Field(on_error='coerce')."

                    raise NormalizationError(
                        field=field_name, 
                        issue=issue_msg, 
                        indices=bad_indices,
                        raw_sample=str(raw_sample),
                        expected_dim=str(target_dim) if target_dim else "unknown",
                        suggestion=suggestion_msg
                    )

            # --- Stage 3: Boundary Validation ---
            valid_results = result_array[~np.isnan(result_array)]
            if len(valid_results) > 0:
                if field.min is not None and np.any(valid_results < field.min):
                    if field.on_error == 'raise':
                        raise AxiomViolationError(f"Field '{field_name}' violates min bound of {field.min}.")
                    else:
                        result_array[result_array < field.min] = np.nan
                if field.max is not None and np.any(valid_results > field.max):
                    if field.on_error == 'raise':
                        raise AxiomViolationError(f"Field '{field_name}' violates max bound of {field.max}.")
                    else:
                        result_array[result_array > field.max] = np.nan
            
            # --- Stage 4: Result Injection ---
            if getattr(field, 'round', None) is not None:
                result_array = np.round(result_array, field.round)
            
            clean_df[field_name] = result_array

        # --- Stage 5: Metadata Management ---
        if keep_unmapped:
            schema_sources = {f.source for f in cls._fields.values()}
            schema_targets = set(cls._fields.keys())
            
            for col in working_df.columns:
                if col in schema_targets:
                    continue
                if drop_raw and col in schema_sources and col not in schema_targets:
                    continue
                
                clean_df[col] = working_df[col]
                
            cols = clean_df.columns.tolist()
            metadata_cols = [c for c in cols if c not in schema_targets]
            schema_cols = [c for c in cols if c in schema_targets]
            clean_df = clean_df[metadata_cols + schema_cols]

        # --- Stage 6: Execute Post-Hooks ---
        for attr_name in dir(cls):
            attr = getattr(cls, attr_name)
            if getattr(attr, '__is_chisa_post_hook__', False):
                clean_df = attr(cls, clean_df)
            
        return clean_df