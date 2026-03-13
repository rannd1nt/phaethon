from __future__ import annotations

import polars as pl
from typing import Any, Callable

class ImputerStage:
    @staticmethod
    def process(
        expr: pl.Expr,
        field: Any,
        parse_bound_fn: Callable[..., Any]
    ) -> pl.Expr:
        
        if field.impute_by is not None:
            if field.impute_by == 'mean':
                expr = expr.fill_null(strategy="mean")
            elif field.impute_by == 'median':
                expr = expr.fill_null(strategy="median")
            elif field.impute_by == 'ffill':
                expr = expr.fill_null(strategy="forward")
            elif field.impute_by == 'bfill':
                expr = expr.fill_null(strategy="backward")
            elif field.impute_by == 'mode':
                expr = expr.fill_null(expr.mode().first())
            else:
                fill_val = parse_bound_fn(field.impute_by, field.target_unit)
                expr = expr.fill_null(pl.lit(fill_val))

        if getattr(field, 'round', None) is not None:
            expr = expr.round(field.round)
            
        return expr