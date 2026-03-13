from __future__ import annotations

import polars as pl
import numpy as np
import pandas as pd
from typing import Any

from ...config import get_config, get_merged_context
from .localizer import LocalizerStage
from .extractor import ExtractorStage
from .converter import ConverterStage
from .validator import ValidatorStage
from .imputer import ImputerStage
from ...registry import ureg

class PolarsBackend:
    def normalize(self, df: pl.DataFrame, fields: dict[str, Any], schema_cls: Any, keep_unmapped: bool, drop_raw: bool) -> pl.DataFrame:
        working_df = df.clone()
        new_columns = []
        
        for field_name, field in fields.items():
            if type(field).__name__ == "DerivedField": continue
            
            if field.source not in working_df.columns:
                raise KeyError(f"Source column '{field.source}' not found.")
            
            raw_expr = pl.col(field.source)
            is_ontology = hasattr(field.target_unit, 'match')
            is_semantic = hasattr(field.target_unit, 'classify')

            if is_ontology:
                def _match_onto(s: pl.Series, *args: Any, f: Any = field, **kwargs: Any) -> pl.Series:
                    fuzzy = getattr(f, 'fuzzy_match', False)
                    conf = getattr(f, 'confidence', 0.85)
                    return pl.Series([
                        f.target_unit.match(str(val), fuzzy_match=fuzzy, confidence=conf) if val is not None else None 
                        for val in s
                    ])
                    
                expr = raw_expr.map_batches(_match_onto, return_dtype=pl.String)
                
                if field.impute_by:
                    if field.impute_by in ('ffill', 'bfill'):
                        expr = getattr(expr, field.impute_by)()
                    else:
                        expr = expr.fill_null(field.impute_by)
                        
                new_columns.append(expr.alias(field_name))
                continue

            target_dim = getattr(field.target_unit, 'dimension', None)
            source_dtype = working_df.schema[field.source]
            
            on_err = get_config("default_on_error", field.on_error)
            dec_mark = get_config("decimal_mark", field.decimal_mark)
            thou_sep = get_config("thousands_sep", field.thousands_sep)
            field_aliases = get_config("aliases", field.aliases) or {}
            
            expr = LocalizerStage.process(raw_expr, source_dtype, dec_mark, thou_sep, field_aliases)
            unit_col_expr = pl.col(field.unit_col) if field.unit_col else None
            expr, isna_expr = ExtractorStage.process(expr, source_dtype, field.parse_string, unit_col_expr)

            if is_semantic:
                def _classify_sem(s: pl.Series, *args: Any, f: Any = field, **kwargs: Any) -> pl.Series:
                    active_context = get_merged_context(getattr(f, 'context', {}))
                    
                    if s.dtype == pl.Struct:
                        values_array = s.struct.field("value").cast(pl.Float64, strict=False).to_numpy()
                        units_array = s.struct.field("unit").cast(pl.String).to_numpy(allow_copy=True)
                    else:
                        values_array = s.cast(pl.Float64, strict=False).to_numpy()
                        units_array = None
                        
                    result_array = np.full(len(values_array), None, dtype=object)
                    
                    for i in range(len(values_array)):
                        if np.isnan(values_array[i]): continue
                        u_str = units_array[i] if units_array is not None else None
                        if (u_str is None or pd.isna(u_str)) and f.source_unit:
                            u_str = f.source_unit
                            
                        if u_str:
                            try:
                                src_cls = ureg().get_unit_class(u_str) if isinstance(u_str, str) else u_str
                                result_array[i] = f.target_unit.classify(values_array[i], src_cls, active_context)
                            except Exception:
                                pass
                    return pl.Series(result_array)
                    
                expr = expr.map_batches(_classify_sem, return_dtype=pl.String)
                
                if field.impute_by:
                    if field.impute_by in ('ffill', 'bfill'):
                        expr = getattr(expr, field.impute_by)()
                    else:
                        expr = expr.fill_null(field.impute_by)
                        
                new_columns.append(expr.alias(field_name))
                continue

            expr = ConverterStage.process(expr, field_name, field, on_err, target_dim)
            bound_parser = lambda val, tgt: schema_cls._parse_physical_bound(val, tgt, field_aliases)
            packed_expr = pl.struct(res=expr, isna=isna_expr, raw=raw_expr)
            expr = ValidatorStage.process(packed_expr, field_name, field, on_err, target_dim, bound_parser)
            expr = ImputerStage.process(expr, field, bound_parser)
                
            new_columns.append(expr.alias(field_name))

        clean_df = working_df.with_columns(new_columns)

        for field_name, field in fields.items():
            if type(field).__name__ != "DerivedField": continue
            
            def _eval_formula(f: Any = field) -> pl.Expr:
                return f.formula(None, backend='polars')
                
            expr = _eval_formula()
            
            if getattr(field, 'round', None) is not None:
                expr = expr.round(field.round)
                
            clean_df = clean_df.with_columns(expr.alias(field_name))

        if keep_unmapped:
            schema_sources = {f.source for f in fields.values() if hasattr(f, 'source')}
            schema_targets = set(fields.keys())
            cols_to_keep = [pl.col(col) for col in working_df.columns if col not in schema_targets and not (drop_raw and col in schema_sources)]
            clean_df = clean_df.select(cols_to_keep + [pl.col(c) for c in schema_targets])
        else:
            clean_df = clean_df.select([pl.col(c) for c in fields.keys()])
            
        return clean_df