from __future__ import annotations

import pandas as pd
import numpy as np
from typing import Any

from ...config import get_config, get_merged_context
from .localizer import LocalizerStage
from .extractor import ExtractorStage
from .converter import ConverterStage
from .validator import ValidatorStage
from .imputer import ImputerStage
from ...registry import ureg

class PandasBackend:
    def normalize(self, df: pd.DataFrame, fields: dict[str, Any], schema_cls: Any, keep_unmapped: bool, drop_raw: bool) -> pd.DataFrame:
        working_df = df.copy()
        clean_df = pd.DataFrame()
        clean_df.index = working_df.index 

        for field_name, field in fields.items():
            if type(field).__name__ == "DerivedField": continue
            
            if field.source not in working_df.columns:
                raise KeyError(f"Source column '{field.source}' not found.")
            
            raw_series = working_df[field.source].copy()
            
            is_ontology = hasattr(field.target_unit, 'match')
            is_semantic = hasattr(field.target_unit, 'classify')

            if is_ontology:
                fuzzy = getattr(field, 'fuzzy_match', False)
                conf = getattr(field, 'confidence', 0.85)
                
                def _apply_onto(x: Any) -> Any:
                    if pd.isna(x): return None
                    return field.target_unit.match(str(x), fuzzy_match=fuzzy, confidence=conf)
                    
                res_series = raw_series.apply(_apply_onto)
                
                if field.impute_by:
                    if field.impute_by == 'mode' and not res_series.mode().empty:
                        res_series = res_series.fillna(res_series.mode()[0])
                    elif field.impute_by in ('ffill', 'bfill'):
                        res_series = getattr(res_series, field.impute_by)()
                    else:
                        res_series = res_series.fillna(field.impute_by)
                        
                clean_df[field_name] = res_series
                continue

            target_dim = getattr(field.target_unit, 'dimension', None)
            on_err = get_config("default_on_error", field.on_error)
            dec_mark = get_config("decimal_mark", field.decimal_mark)
            thou_sep = get_config("thousands_sep", field.thousands_sep)
            field_aliases = get_config("aliases", field.aliases) or {}
            
            raw_series = LocalizerStage.process(raw_series, dec_mark, thou_sep, field_aliases)
            unit_col_data = working_df[field.unit_col] if field.unit_col else None
            values_array, units_array, isna_mask = ExtractorStage.process(raw_series, field.parse_string, unit_col_data)
            
            if isna_mask.all() and field.impute_by is None:
                clean_df[field_name] = np.full(len(raw_series), None, dtype=object) if is_semantic else np.full(len(raw_series), np.nan, dtype=float)
                continue

            if is_semantic:
                result_array = np.full(len(raw_series), None, dtype=object)
                active_context = get_merged_context(getattr(field, 'context', {}))
                
                for i in range(len(raw_series)):
                    if isna_mask[i] or pd.isna(values_array[i]): continue
                    
                    u_str = units_array[i] if units_array is not None else None
                    if pd.isna(u_str) and field.source_unit:
                        u_str = field.source_unit
                        
                    if u_str:
                        try:
                            src_cls = ureg().get_unit_class(u_str) if isinstance(u_str, str) else u_str
                            state = field.target_unit.classify(values_array[i], src_cls, active_context)
                            result_array[i] = state
                        except Exception:
                            pass
                            
                res_series = pd.Series(result_array, index=raw_series.index)
                
                if field.impute_by:
                    if field.impute_by == 'mode' and not res_series.mode().empty:
                        res_series = res_series.fillna(res_series.mode()[0])
                    elif field.impute_by in ('ffill', 'bfill'):
                        res_series = getattr(res_series, field.impute_by)()
                    else:
                        res_series = res_series.fillna(field.impute_by)
                        
                clean_df[field_name] = res_series
                continue

            result_array = ConverterStage.process(
                working_df, field_name, field, raw_series, values_array, 
                units_array, isna_mask, on_err, target_dim
            )
            
            bound_parser = lambda val, tgt: schema_cls._parse_physical_bound(val, tgt, field_aliases)
            
            result_array = ValidatorStage.process(
                working_df, field_name, field, result_array, raw_series, 
                isna_mask, on_err, target_dim, bound_parser
            )
            
            result_array = ImputerStage.process(
                result_array, field, bound_parser
            )
            
            clean_df[field_name] = result_array

        for field_name, field in fields.items():
            if type(field).__name__ != "DerivedField": continue
            
            raw_result = field.formula(clean_df, backend='pandas')
            
            if getattr(field, 'round', None) is not None:
                raw_result = raw_result.round(field.round)
                
            clean_df[field_name] = raw_result

        if keep_unmapped:
            schema_sources = {f.source for f in fields.values() if hasattr(f, 'source')}
            schema_targets = set(fields.keys())
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
            
        return clean_df