from __future__ import annotations

from ...compat import HAS_POLARS
if HAS_POLARS:
    import polars as pl
import numpy as np
from typing import Any

from ...config import get_config, get_merged_context
from .localizer import LocalizerStage
from .extractor import ExtractorStage
from .converter import ConverterStage
from .validator import ValidatorStage
from .imputer import ImputerStage
from ...registry import ureg

class PolarsBackend:

    def _get_rust_payload(self, field: Any, target_dim: str, field_aliases: dict, schema_cls: Any, target_unit_cls: Any = None) -> tuple:
        on_err_str = get_config("default_on_error", getattr(field, 'on_error', None))
        err_mode_int = 0 if on_err_str == 'raise' else 2 if on_err_str == 'clip' else 1
        
        strictness = get_config("axiom_strictness_level", getattr(field, 'axiom_strictness_level', None)) or "default"
        ignore_bound_for_rust = strictness in ("ignore", "loose_warn")

        active_context = get_merged_context(getattr(field, 'context', {}))
        if getattr(field, 'axiom_strictness_level', None) is not None:
            active_context["axiom_strictness_level"] = field.axiom_strictness_level
        if getattr(field, 'on_error', None) is not None:
            active_context["default_on_error"] = field.on_error

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

        tgt_cls = target_unit_cls if target_unit_cls is not None else field.target_unit
        tgt_mult = float(tgt_cls._get_dynamic_multiplier(tgt_cls, active_context, is_array=False))
        tgt_offset = float(getattr(tgt_cls, 'base_offset', 0.0))

        return payload_map, tgt_mult, tgt_offset, err_mode_int

    def normalize(self, df: pl.DataFrame, fields: dict[str, Any], schema_cls: Any, keep_unmapped: bool, drop_raw: bool) -> pl.DataFrame:
        working_df = df.clone()
        new_columns = []
        cols_to_drop_missing = []

        for field_name, field in fields.items():
            if type(field).__name__ == "DerivedField": continue
            
            if field.source not in working_df.columns:
                raise KeyError(f"Source column '{field.source}' not found.")
            
            raw_expr = pl.col(field.source)
            source_dtype = working_df.schema[field.source]
            is_pure_numeric = source_dtype in (pl.Float64, pl.Float32, pl.Int64, pl.Int32)

            if getattr(field, 'null_values', None):
                null_strs = [v for v in field.null_values if isinstance(v, str)]
                null_nums = [v for v in field.null_values if isinstance(v, (int, float)) and not np.isnan(v)]
                
                cond = pl.lit(False)
                
                if is_pure_numeric:
                    if null_nums: cond = cond | raw_expr.is_in(null_nums)
                elif source_dtype in (pl.String, pl.Categorical):
                    all_str_targets = null_strs + [str(n) for n in null_nums] + [str(float(n)) for n in null_nums]
                    if all_str_targets: cond = cond | raw_expr.is_in(all_str_targets)
                else:
                    if null_strs: cond = cond | raw_expr.cast(pl.String).is_in(null_strs)
                    if null_nums: cond = cond | raw_expr.cast(pl.Float64, strict=False).is_in(null_nums)
                    
                raw_expr = pl.when(cond).then(None).otherwise(raw_expr)
                
            if getattr(field, 'drop_missing', False):
                cols_to_drop_missing.append(field_name)

            is_ontology = hasattr(field.target_unit, 'match')
            is_semantic = hasattr(field.target_unit, 'classify')

            if is_ontology:
                def _match_onto_vectorized(s: pl.Series, f: Any = field, **kwargs: Any) -> pl.Series:
                    fuzzy = getattr(f, 'fuzzy_match', False)
                    conf = getattr(f, 'confidence', 0.85)
                    unique_vals = s.drop_nulls().cast(pl.String).str.strip_chars().unique().to_list()
                    mapping_dict = {val: f.target_unit.match(val, fuzzy_match=fuzzy, confidence=conf) for val in unique_vals}
                    return s.cast(pl.String).str.strip_chars().replace_strict(mapping_dict, default=None).cast(pl.String)

                expr = raw_expr.map_batches(_match_onto_vectorized, return_dtype=pl.String)
                if getattr(field, 'impute_by', None):
                    if field.impute_by in ('ffill', 'bfill'): expr = getattr(expr, field.impute_by)()
                    else: expr = expr.fill_null(field.impute_by)
                new_columns.append(expr.alias(field_name))
                continue

            target_dim = getattr(field.target_unit, 'dimension', None)
            source_dtype = working_df.schema[field.source]
            on_err = get_config("default_on_error", getattr(field, 'on_error', None))
            dec_mark = get_config("decimal_mark", getattr(field, 'decimal_mark', None))
            thou_sep = get_config("thousands_sep", getattr(field, 'thousands_sep', None))
            field_aliases = get_config("aliases", getattr(field, 'aliases', None)) or {}
            
            expr = LocalizerStage.process(raw_expr, source_dtype, dec_mark, thou_sep, field_aliases)
            
            def _make_bound_parser(fa: dict):
                return lambda val, tgt: schema_cls._parse_physical_bound(val, tgt, fa)
            bound_parser = _make_bound_parser(field_aliases)

            if is_semantic and field.parse_string:
                try:
                    conditions = field.target_unit.__phaethon_conditions__
                    if conditions:
                        ref_unit_cls = next(iter(conditions.values())).target_unit
                        sem_target_dim = getattr(ref_unit_cls, 'dimension', 'unknown')
                        
                        class _MockField:
                            on_error = 'coerce'
                            axiom_strictness_level = getattr(field, 'axiom_strictness_level', None) # 🌟 UPDATE
                            context = getattr(field, 'context', {})
                            source_unit = getattr(field, 'source_unit', None)
                            target_unit = ref_unit_cls

                        payload_map, tgt_mult, tgt_offset, err_mode_int = self._get_rust_payload(_MockField(), sem_target_dim, field_aliases, schema_cls, ref_unit_cls)

                        rt = getattr(field, 'require_tag', True)
                        fuk = getattr(field, 'source_unit', "") if isinstance(getattr(field, 'source_unit', None), str) else getattr(ref_unit_cls, 'symbol', "")

                        def _hybrid_semantic_udf(
                            s: pl.Series, f: Any = field, pm: dict = payload_map, 
                            tm: float = tgt_mult, toff: float = tgt_offset, em: int = err_mode_int, 
                            cnds: dict = conditions, ruc: Any = ref_unit_cls, 
                            fname: str = field_name, tdim: str = sem_target_dim, **kwargs: Any
                        ) -> pl.Series:
                            try:
                                from phaethon._rust_core import fast_fused_normalize
                                rust_list = fast_fused_normalize(s.cast(pl.String).to_list(), pm, tm, toff, em, rt, fuk)
                                numeric_array = np.array(rust_list, dtype=float)

                                condlist = []
                                choicelist = []
                                valid_mask = ~np.isnan(numeric_array)
                                
                                for name, cond in cnds.items():
                                    c_mask = valid_mask.copy()
                                    c_min, c_max = cond.min, cond.max
                                    
                                    if cond.target_unit != ruc:
                                        active_ctx = get_merged_context(getattr(f, 'context', {}))
                                        if c_min is not None: c_min = cond.target_unit(c_min, context=active_ctx).to(ruc).mag
                                        if c_max is not None: c_max = cond.target_unit(c_max, context=active_ctx).to(ruc).mag
                                    
                                    if c_min is not None: c_mask &= (numeric_array >= float(c_min))
                                    if c_max is not None: c_mask &= (numeric_array <= float(c_max))
                                    
                                    condlist.append(c_mask)
                                    choicelist.append(name)
                                    
                                result_array_sem = np.select(condlist, choicelist, default=None)
                                result_array_sem = np.where(result_array_sem == 'None', None, result_array_sem)
                                return pl.Series(s.name, result_array_sem, dtype=pl.String)
                                
                            except ValueError as e:
                                from ....exceptions import AxiomViolationError, NormalizationError
                                parts = str(e).split('|')
                                if len(parts) > 1:
                                    err_type = parts[0]
                                    idx = int(parts[1])
                                    if err_type in ("AXIOM_MIN", "AXIOM_MAX"):
                                        val, limit = float(parts[2]), float(parts[3])
                                        b_type = "min" if err_type == "AXIOM_MIN" else "max"
                                        raise AxiomViolationError(f"Raw value {val} violates {b_type} bound of {limit}")
                                    elif err_type == "UNIT_ERROR":
                                        raise NormalizationError(
                                            field=fname, issue=f"Unrecognized unit '{parts[2]}'.", indices=[idx],
                                            raw_sample=str(s[idx]), expected_dim=str(tdim) if tdim else "unknown",
                                            suggestion="Fix the raw data, register the unit alias, or set Field(on_error='coerce')."
                                        )
                                    elif err_type == "PARSE_ERROR":
                                        raise NormalizationError(
                                            field=fname, issue="Data format rejected by parser.", indices=[idx],
                                            raw_sample=str(s[idx]), expected_dim=str(tdim) if tdim else "unknown",
                                            suggestion="Ensure data contains a number and valid unit, or set Field(on_error='coerce')."
                                        )
                                raise e

                        expr = expr.map_batches(_hybrid_semantic_udf, return_dtype=pl.String)
                        
                        if getattr(field, 'impute_by', None):
                            if field.impute_by in ('ffill', 'bfill'): expr = getattr(expr, field.impute_by)()
                            else: expr = expr.fill_null(field.impute_by)
                        new_columns.append(expr.alias(field_name))
                        continue
                except ImportError:
                    pass
            
            if field.parse_string and not is_semantic:
                try:
                    source_dtype = working_df.schema[field.source]
                    is_pure_numeric = source_dtype in (pl.Float64, pl.Float32, pl.Int64, pl.Int32)
                    
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

                        expr = ((raw_expr + src_offset) * src_mult / tgt_mult) - tgt_offset
                    else:
                        payload_map, tgt_mult, tgt_offset, err_mode_int = self._get_rust_payload(field, target_dim, field_aliases, schema_cls, field.target_unit)
                        req_tag = getattr(field, 'require_tag', True)
                        fback_u = getattr(field, 'source_unit', "") if isinstance(getattr(field, 'source_unit', None), str) else getattr(field.target_unit, 'symbol', "")

                        def _rust_physics_udf(
                            s: pl.Series, fname: str = field_name, tdim: str = target_dim, 
                            pm: dict = payload_map, tm: float = tgt_mult, toff: float = tgt_offset, 
                            em: int = err_mode_int, rt: bool = req_tag, fuk: str = fback_u, **kwargs: Any
                        ) -> pl.Series:
                            try:
                                from phaethon._rust_core import fast_fused_normalize
                                rust_list = fast_fused_normalize(s.cast(pl.String).to_list(), pm, tm, toff, em, rt, fuk)
                                return pl.Series(s.name, rust_list, dtype=pl.Float64)
                            except ValueError as e:
                                from ....exceptions import AxiomViolationError, NormalizationError
                                parts = str(e).split('|')
                                if len(parts) > 1:
                                    err_type = parts[0]
                                    idx = int(parts[1])
                                    if err_type in ("AXIOM_MIN", "AXIOM_MAX"):
                                        val, limit = float(parts[2]), float(parts[3])
                                        b_type = "min" if err_type == "AXIOM_MIN" else "max"
                                        raise AxiomViolationError(f"Raw value {val} violates {b_type} bound of {limit}")
                                    elif err_type == "UNIT_ERROR":
                                        raise NormalizationError(
                                            field=fname, issue=f"Unrecognized unit '{parts[2]}'.", indices=[idx],
                                            raw_sample=str(s[idx]), expected_dim=str(tdim) if tdim else "unknown",
                                            suggestion="Fix the raw data, register the unit alias, or set Field(on_error='coerce')."
                                        )
                                    elif err_type == "PARSE_ERROR":
                                        raise NormalizationError(
                                            field=fname, issue="Data format rejected by parser.", indices=[idx],
                                            raw_sample=str(s[idx]), expected_dim=str(tdim) if tdim else "unknown",
                                            suggestion="Ensure data contains a number and valid unit, or set Field(on_error='coerce')."
                                        )
                                raise e

                        expr = expr.map_batches(_rust_physics_udf, return_dtype=pl.Float64)

                    if field.min is not None:
                        min_val = bound_parser(field.min, field.target_unit)
                        if on_err == 'clip': expr = pl.when(expr < min_val).then(min_val).otherwise(expr)
                        elif on_err == 'coerce': expr = pl.when(expr < min_val).then(None).otherwise(expr)

                    if field.max is not None:
                        max_val = bound_parser(field.max, field.target_unit)
                        if on_err == 'clip': expr = pl.when(expr > max_val).then(max_val).otherwise(expr)
                        elif on_err == 'coerce': expr = pl.when(expr > max_val).then(None).otherwise(expr)

                    if getattr(field, 'outlier_std', None) is not None:
                        mean_expr = expr.mean()
                        std_expr = expr.std()
                        z_expr = ((expr - mean_expr) / std_expr).abs()
                        expr = pl.when(z_expr > field.outlier_std).then(None).otherwise(expr)

                    interp_method = getattr(field, 'interpolate', None)
                    if interp_method is not None:
                        if interp_method in ("linear", "nearest"):
                            expr = expr.interpolate(method=interp_method)
                        else:
                            import warnings
                            warnings.warn(
                                f"Polars engine natively supports only 'linear' and 'nearest' interpolation. "
                                f"Falling back to 'linear' instead of requested '{interp_method}'. "
                                f"Switch to Pandas DataFrame if SciPy interpolation is required."
                            )
                            expr = expr.interpolate(method="linear")

                    if getattr(field, 'impute_by', None) is not None:
                        if field.impute_by in ('ffill', 'bfill'): expr = getattr(expr, field.impute_by)()
                        elif field.impute_by == 'mean': expr = expr.fill_null(expr.mean())
                        elif field.impute_by == 'median': expr = expr.fill_null(expr.median())
                        elif field.impute_by == 'mode': expr = expr.fill_null(expr.mode().first())
                        else: expr = expr.fill_null(bound_parser(field.impute_by, field.target_unit))

                    if getattr(field, 'round', None) is not None:
                        expr = expr.round(field.round)

                    new_columns.append(expr.alias(field_name))
                    
                    continue
                except ImportError:
                    pass

            unit_col_expr = pl.col(field.unit_col) if getattr(field, 'unit_col', None) else None
            packed_expr, isna_expr = ExtractorStage.process(expr, source_dtype, field.parse_string, unit_col_expr)

            if is_semantic:
                def _classify_sem(s: pl.Series, f: Any = field, **kwargs: Any) -> pl.Series:
                    active_context = get_merged_context(getattr(f, 'context', {}))
                    if getattr(f, 'axiom_strictness_level', None) is not None:
                        active_context["axiom_strictness_level"] = f.axiom_strictness_level
                    if getattr(f, 'on_error', None) is not None:
                        active_context["default_on_error"] = f.on_error
                        
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
                        if (u_str is None or np.isnan(u_str)) and getattr(f, 'source_unit', None): u_str = f.source_unit
                        if u_str:
                            try:
                                src_cls = ureg().get_unit_class(u_str) if isinstance(u_str, str) else u_str
                                result_array[i] = f.target_unit.classify(values_array[i], src_cls, active_context)
                            except Exception: pass
                    return pl.Series(result_array, dtype=pl.String)
                
                expr = packed_expr.map_batches(_classify_sem, return_dtype=pl.String)
                if getattr(field, 'impute_by', None):
                    expr = getattr(expr, field.impute_by)() if field.impute_by in ('ffill', 'bfill') else expr.fill_null(field.impute_by)
                new_columns.append(expr.alias(field_name))
                continue

            expr = ConverterStage.process(packed_expr, field_name, field, on_err, target_dim)
            packed_val_expr = pl.struct(res=expr, isna=isna_expr, raw=raw_expr)
            expr = ValidatorStage.process(packed_val_expr, field_name, field, on_err, target_dim, bound_parser)
            expr = ImputerStage.process(expr, field, bound_parser)
            new_columns.append(expr.alias(field_name))

        clean_df = working_df.with_columns(new_columns)

        for field_name, field in fields.items():
            if type(field).__name__ != "DerivedField": continue
            expr = field.formula(None, backend='polars')
            if getattr(field, 'round', None) is not None: expr = expr.round(field.round)
            clean_df = clean_df.with_columns(expr.alias(field_name))

        if cols_to_drop_missing:
            clean_df = clean_df.drop_nulls(subset=cols_to_drop_missing)

        if keep_unmapped:
            schema_sources = {f.source for f in fields.values() if hasattr(f, 'source')}
            schema_targets = set(fields.keys())
            cols_to_keep = [pl.col(col) for col in working_df.columns if col not in schema_targets and not (drop_raw and col in schema_sources)]
            clean_df = clean_df.select(cols_to_keep + [pl.col(c) for c in schema_targets])
        else:
            clean_df = clean_df.select([pl.col(c) for c in fields.keys()])
            
        return clean_df