from __future__ import annotations

import polars as pl

class ExtractorStage:
    @staticmethod
    def process(
        expr: pl.Expr, 
        source_dtype: pl.DataType,
        parse_string: bool, 
        unit_col_expr: pl.Expr | None = None
    ) -> tuple[pl.Expr, pl.Expr]:
        
        isna_expr = expr.is_null()
        
        if source_dtype == pl.String:
            blank_str_expr = expr.str.strip_chars() == ""
            isna_expr = isna_expr | blank_str_expr

        if parse_string:
            regex_pattern = r'^\s*([-+]?[0-9]*\.?[0-9]+(?:[eE][-+]?[0-9]+)?)(?:\s+(.*?))?\s*$'
            
            struct_expr = expr.cast(pl.String).str.extract_groups(regex_pattern)
            
            value_expr = struct_expr.struct.field("1").cast(pl.Float64, strict=False)
            unit_expr = struct_expr.struct.field("2").str.strip_chars()
            
            unit_expr = pl.when(unit_expr == "").then(None).otherwise(unit_expr)
            
            combined_expr = pl.struct(value=value_expr, unit=unit_expr)

        elif unit_col_expr is not None:
            value_expr = expr.cast(pl.Float64, strict=False)
            unit_expr = unit_col_expr.cast(pl.String)
            combined_expr = pl.struct(value=value_expr, unit=unit_expr)
            
        else:
            value_expr = expr.cast(pl.Float64, strict=False)
            unit_expr = pl.lit(None, dtype=pl.String)
            combined_expr = pl.struct(value=value_expr, unit=unit_expr)

        return combined_expr, isna_expr