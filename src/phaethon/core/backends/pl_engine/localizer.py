from __future__ import annotations

from ...compat import HAS_POLARS
if HAS_POLARS:
    import polars as pl
import re

class LocalizerStage:
    @staticmethod
    def process(
        expr: pl.Expr, 
        source_dtype: pl.DataType,
        decimal_mark: str | None, 
        thousands_sep: str | None, 
        aliases: dict[str, str | list[str]] | None
    ) -> pl.Expr:
        
        _PL_NUMERIC_DTYPES = frozenset({
            pl.Int8, pl.Int16, pl.Int32, pl.Int64,
            pl.UInt8, pl.UInt16, pl.UInt32, pl.UInt64,
            pl.Float32, pl.Float64, pl.Decimal
        })

        if source_dtype in _PL_NUMERIC_DTYPES:
            return expr

        expr = expr.cast(pl.String)

        if decimal_mark == thousands_sep and decimal_mark is not None:
            thousands_sep = None

        if aliases:
            for official_key, dirty_vals in aliases.items():
                if not isinstance(dirty_vals, list):
                    dirty_vals = [dirty_vals]
                for v in dirty_vals:
                    pattern = rf'\b{re.escape(v)}\b'
                    expr = expr.str.replace_all(pattern, official_key)

        if thousands_sep or (decimal_mark and decimal_mark != '.'):
            expr = expr.str.strip_chars()
            
            if thousands_sep:
                expr = expr.str.replace_all(thousands_sep, "", literal=True)
            
            if decimal_mark and decimal_mark != '.':
                expr = expr.str.replace_all(decimal_mark, ".", literal=True)

            expr = pl.when(expr == "").then(None).otherwise(expr)

        return expr