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

    def _execute_fused(self, raw_series: pd.Series, field: Any, target_dim: str, field_aliases: dict) -> np.ndarray:
        on_err_str = get_config("default_on_error", getattr(field, 'on_error', None))
        err_mode_int = 0 if on_err_str == 'raise' else 2 if on_err_str == 'clip' else 1
        
        strictness = get_config("axiom_strictness_level", getattr(field, 'axiom_strictness_level', None)) or "default"
        ignore_bound_for_rust = strictness in ("ignore", "loose_warn")

        active_context = get_merged_context(getattr(field, 'context', {}))
        if getattr(field, 'axiom_strictness_level', None) is not None:
            active_context["axiom_strictness_level"] = field.axiom_strictness_level
        if getattr(field, 'on_error', None) is not None:
            active_context["default_on_error"] = field.on_error

        require_tag = getattr(field, 'require_tag', True)

        payload_map = {}
        valid_classes = ureg().unitsin(target_dim, ascls=True)

        for cls in valid_classes:
            dyn_mult = float(cls._get_dynamic_multiplier(cls, active_context, is_array=False))
            offset = float(getattr(cls, 'base_offset', 0.0))
            a_min_raw = getattr(cls, '__axiom_min__', None)
            a_min = float(a_min_raw) if (not ignore_bound_for_rust and a_min_raw is not None) else None
            a_max_raw = getattr(cls, '__axiom_max__', None)
            a_max = float(a_max_raw) if (not ignore_bound_for_rust and a_max_raw is not None) else None

            meta = (dyn_mult, offset, a_min, a_max)
            if hasattr(cls, 'symbol') and cls.symbol: payload_map[cls.symbol] = meta
            if hasattr(cls, 'aliases') and cls.aliases:
                for alias in cls.aliases: payload_map[alias] = meta

        for off_key, dirty_vals in field_aliases.items():
            if off_key in payload_map:
                if not isinstance(dirty_vals, list): dirty_vals = [dirty_vals]
                for v in dirty_vals: payload_map[v] = payload_map[off_key]

        if getattr(field, 'source_unit', None):
            src_cls = ureg().get_unit_class(field.source_unit, expected_dim=target_dim) if isinstance(field.source_unit, str) else field.source_unit
            dyn_mult = float(src_cls._get_dynamic_multiplier(src_cls, active_context, is_array=False))
            offset = float(getattr(src_cls, 'base_offset', 0.0))
            a_min_raw = getattr(src_cls, '__axiom_min__', None)
            a_min = float(a_min_raw) if (not ignore_bound_for_rust and a_min_raw is not None) else None
            a_max_raw = getattr(src_cls, '__axiom_max__', None)
            a_max = float(a_max_raw) if (not ignore_bound_for_rust and a_max_raw is not None) else None
            payload_map[""] = (dyn_mult, offset, a_min, a_max)

        tgt_cls = field.target_unit
        tgt_mult = float(tgt_cls._get_dynamic_multiplier(tgt_cls, active_context, is_array=False))
        tgt_offset = float(getattr(tgt_cls, 'base_offset', 0.0))
        
        fallback_unit_key = ""
        if getattr(field, 'source_unit', None):
            fallback_unit_key = field.source_unit if isinstance(field.source_unit, str) else getattr(field.source_unit, 'symbol', "")
        else:
            fallback_unit_key = getattr(tgt_cls, 'symbol', "")
        
        from phaethon._rust_core import fast_fused_normalize
        
        rust_array = fast_fused_normalize(
            raw_series.tolist(), payload_map, tgt_mult, tgt_offset, err_mode_int,
            require_tag, fallback_unit_key
        )
        return np.array(rust_array, dtype=float)

    def normalize(self, df: pd.DataFrame, fields: dict[str, Any], schema_cls: Any, keep_unmapped: bool, drop_raw: bool) -> pd.DataFrame:
        working_df = df.copy()
        clean_df = pd.DataFrame()
        clean_df.index = working_df.index 

        cols_to_drop_missing = []

        for field_name, field in fields.items():
            if type(field).__name__ == "DerivedField": continue
            
            raw_series = working_df[field.source].copy()

            if getattr(field, 'null_values', None):
                raw_series = raw_series.replace(field.null_values, np.nan)
            
            if getattr(field, 'drop_missing', False):
                cols_to_drop_missing.append(field_name)
            
            is_ontology = hasattr(field.target_unit, 'match')
            is_semantic = hasattr(field.target_unit, 'classify')

            if is_ontology:
                fuzzy = getattr(field, 'fuzzy_match', False)
                conf = getattr(field, 'confidence', 0.85)
                unique_raw_vals = raw_series.dropna().astype(str).str.strip().unique()
                mapping_dict = {}
                for val in unique_raw_vals:
                    mapping_dict[val] = field.target_unit.match(val, fuzzy_match=fuzzy, confidence=conf)
                res_series = raw_series.astype(str).str.strip().map(mapping_dict)
                isna_mask = pd.isna(raw_series) | (raw_series.astype(str).str.strip() == "")
                res_series.loc[isna_mask] = None
                
                if getattr(field, 'impute_by', None):
                    res_series = res_series.fillna(field.impute_by) if field.impute_by not in ('mode', 'ffill', 'bfill') else res_series.ffill()
                
                clean_df[field_name] = res_series
                continue

            target_dim = getattr(field.target_unit, 'dimension', None)
            on_err = get_config("default_on_error", getattr(field, 'on_error', None))
            dec_mark = get_config("decimal_mark", getattr(field, 'decimal_mark', None))
            thou_sep = get_config("thousands_sep", getattr(field, 'thousands_sep', None))
            field_aliases = get_config("aliases", getattr(field, 'aliases', None)) or {}

            if is_semantic and field.parse_string:
                try:
                    conditions = field.target_unit.__phaethon_conditions__
                    if conditions:
                        ref_unit_cls = next(iter(conditions.values())).target_unit
                        sem_target_dim = getattr(ref_unit_cls, 'dimension', 'unknown')
                        
                        class _MockField:
                            on_error = 'coerce'
                            axiom_strictness_level = getattr(field, 'axiom_strictness_level', None) # 🌟 MOCK UPDATE
                            context = getattr(field, 'context', {})
                            source_unit = getattr(field, 'source_unit', None)
                            target_unit = ref_unit_cls

                        numeric_array = self._execute_fused(raw_series, _MockField(), sem_target_dim, field_aliases)
                        
                        condlist = []
                        choicelist = []
                        valid_mask = ~np.isnan(numeric_array)
                        
                        for name, cond in conditions.items():
                            c_mask = valid_mask.copy()
                            c_min, c_max = cond.min, cond.max
                            
                            if cond.target_unit != ref_unit_cls:
                                active_ctx = get_merged_context(getattr(field, 'context', {}))
                                if c_min is not None: c_min = cond.target_unit(c_min, context=active_ctx).to(ref_unit_cls).mag
                                if c_max is not None: c_max = cond.target_unit(c_max, context=active_ctx).to(ref_unit_cls).mag
                            
                            if c_min is not None: c_mask &= (numeric_array >= float(c_min))
                            if c_max is not None: c_mask &= (numeric_array <= float(c_max))
                            
                            condlist.append(c_mask)
                            choicelist.append(name)
                            
                        result_array_sem = np.select(condlist, choicelist, default=None)
                        result_array_sem = np.where(result_array_sem == 'None', None, result_array_sem)
                        
                        res_series = pd.Series(result_array_sem, index=raw_series.index)
                        if getattr(field, 'impute_by', None):
                            res_series = res_series.fillna(field.impute_by) if field.impute_by not in ('mode', 'ffill', 'bfill') else res_series.ffill()
                        
                        clean_df[field_name] = res_series
                        continue
                except ImportError:
                    pass 
            
            raw_series = LocalizerStage.process(raw_series, dec_mark, thou_sep, field_aliases)
            bound_parser = lambda val, tgt: schema_cls._parse_physical_bound(val, tgt, field_aliases)

            if field.parse_string and not is_semantic:
                try:
                    is_pure_numeric = pd.api.types.is_numeric_dtype(raw_series)
                    
                    if is_pure_numeric:
                        tgt_cls = field.target_unit
                        
                        active_context = get_merged_context(getattr(field, 'context', {}))
                        if getattr(field, 'axiom_strictness_level', None) is not None:
                            active_context["axiom_strictness_level"] = field.axiom_strictness_level
                        if getattr(field, 'on_error', None) is not None:
                            active_context["default_on_error"] = field.on_error
                            
                        tgt_mult = float(tgt_cls._get_dynamic_multiplier(tgt_cls, active_context, is_array=False))
                        tgt_offset = float(getattr(tgt_cls, 'base_offset', 0.0))
                        
                        src_mult, src_offset = 1.0, 0.0
                        if getattr(field, 'source_unit', None):
                            src_cls = ureg().get_unit_class(field.source_unit, expected_dim=target_dim) if isinstance(field.source_unit, str) else field.source_unit
                            src_mult = float(src_cls._get_dynamic_multiplier(src_cls, active_context, is_array=False))
                            src_offset = float(getattr(src_cls, 'base_offset', 0.0))
                            
                        result_array = ((raw_series.values + src_offset) * src_mult / tgt_mult) - tgt_offset
                        isna_mask = np.asarray(pd.isna(raw_series), dtype=bool)
                    else:
                        result_array = self._execute_fused(raw_series, field, target_dim, field_aliases)
                        isna_mask = np.asarray(pd.isna(raw_series) | (raw_series.astype(str).str.strip() == ""), dtype=bool)
                    
                    result_array = ValidatorStage.process(
                        working_df, field_name, field, result_array, raw_series, 
                        isna_mask, on_err, target_dim, bound_parser
                    )
                    
                    if getattr(field, 'interpolate', None):
                        interp_method = field.interpolate
                        temp_series = pd.Series(result_array, index=working_df.index)
                        
                        try:
                            temp_series = temp_series.interpolate(method=interp_method)
                        except ImportError as e:
                            if "scipy" in str(e).lower():
                                raise ImportError(
                                    f"The '{interp_method}' interpolation requires 'scipy"
                                    f"Please install it using `pip install scipy` "
                                    f"or switch to method='linear'."
                                ) from None
                            raise e
                        except ValueError as e:
                            raise ValueError(f"Phaethon Interpolation Error on field '{field.name}': {e}") from None
                            
                        result_array = temp_series.to_numpy()
                    
                    result_array = ImputerStage.process(result_array, field, bound_parser)
                    if getattr(field, 'round', None) is not None:
                        result_array = np.round(result_array, field.round)
                        
                    clean_df[field_name] = result_array
                    continue 
                except ImportError:
                    pass
                except ValueError as e:
                    from ....exceptions import AxiomViolationError, NormalizationError
                    parts = str(e).split('|')
                    if len(parts) > 1:
                        err_type = parts[0]
                        idx = int(parts[1])
                        real_index = working_df.index[idx]

                        if err_type in ("AXIOM_MIN", "AXIOM_MAX"):
                            val, limit = float(parts[2]), float(parts[3])
                            b_type = "min" if err_type == "AXIOM_MIN" else "max"
                            raise AxiomViolationError(f"Raw value {val} violates {b_type} bound of {limit} at indices [{real_index}]")
                        elif err_type == "UNIT_ERROR":
                            raise NormalizationError(
                                field=field_name, issue=f"Unrecognized unit '{parts[2]}'.", indices=[real_index],
                                raw_sample=str(raw_series.iloc[idx]), expected_dim=str(target_dim) if target_dim else "unknown",
                                suggestion="Fix the raw data, register the unit alias, or set Field(on_error='coerce')."
                            )
                        elif err_type == "PARSE_ERROR":
                            raise NormalizationError(
                                field=field_name, issue="Data format rejected by parser.", indices=[real_index],
                                raw_sample=str(raw_series.iloc[idx]), expected_dim=str(target_dim) if target_dim else "unknown",
                                suggestion="Ensure data contains a number and valid unit, or set Field(on_error='coerce')."
                            )
                    raise e

            unit_col_data = working_df[field.unit_col] if getattr(field, 'unit_col', None) else None
            values_array, units_array, isna_mask = ExtractorStage.process(raw_series, field.parse_string, unit_col_data)
            
            if isna_mask.all() and getattr(field, 'impute_by', None) is None:
                clean_df[field_name] = np.full(len(raw_series), None, dtype=object) if is_semantic else np.full(len(raw_series), np.nan, dtype=float)
                continue

            if is_semantic:
                result_array_sem = np.full(len(raw_series), None, dtype=object)
                
                active_context = get_merged_context(getattr(field, 'context', {}))
                if getattr(field, 'axiom_strictness_level', None) is not None:
                    active_context["axiom_strictness_level"] = field.axiom_strictness_level
                if getattr(field, 'on_error', None) is not None:
                    active_context["default_on_error"] = field.on_error
                    
                for i in range(len(raw_series)):
                    if isna_mask[i] or pd.isna(values_array[i]): continue
                    u_str = units_array[i] if units_array is not None else getattr(field, 'source_unit', None)
                    if u_str:
                        try:
                            src_cls = ureg().get_unit_class(u_str) if isinstance(u_str, str) else u_str
                            result_array_sem[i] = field.target_unit.classify(values_array[i], src_cls, active_context)
                        except Exception: pass
                res_series = pd.Series(result_array_sem, index=raw_series.index)
                if getattr(field, 'impute_by', None):
                    res_series = res_series.fillna(field.impute_by) if field.impute_by not in ('mode', 'ffill', 'bfill') else res_series.ffill()
                clean_df[field_name] = res_series
                continue

            result_array = ConverterStage.process(working_df, field_name, field, raw_series, values_array, units_array, isna_mask, on_err, target_dim)
            result_array = ValidatorStage.process(working_df, field_name, field, result_array, raw_series, isna_mask, on_err, target_dim, bound_parser)
            result_array = ImputerStage.process(result_array, field, bound_parser)
            if getattr(field, 'round', None) is not None: result_array = np.round(result_array, field.round)
            clean_df[field_name] = result_array

        for field_name, field in fields.items():
            if type(field).__name__ != "DerivedField": continue
            raw_result = field.formula(clean_df, backend='pandas')
            if getattr(field, 'round', None) is not None: raw_result = raw_result.round(field.round)
            clean_df[field_name] = raw_result

        if keep_unmapped:
            schema_sources = {f.source for f in fields.values() if hasattr(f, 'source')}
            schema_targets = set(fields.keys())
            for col in working_df.columns:
                if col in schema_targets: continue
                if drop_raw and col in schema_sources and col not in schema_targets: continue
                clean_df[col] = working_df[col]
                
            cols = clean_df.columns.tolist()
            metadata_cols = [c for c in cols if c not in schema_targets]
            schema_cols = [c for c in cols if c in schema_targets]
            clean_df = clean_df[metadata_cols + schema_cols]
        
        if cols_to_drop_missing:
            clean_df = clean_df.dropna(subset=cols_to_drop_missing)
        
        return clean_df