from __future__ import annotations

import pandas as pd
import numpy as np
import re

class LocalizerStage:
    @staticmethod
    def process(
        raw_series: pd.Series, 
        decimal_mark: str | None, 
        thousands_sep: str | None, 
        aliases: dict[str, str | list[str]] | None
    ) -> pd.Series:
        
        if pd.api.types.is_numeric_dtype(raw_series):
            return raw_series

        series = raw_series.copy()

        if decimal_mark == thousands_sep and decimal_mark is not None:
            thousands_sep = None

        if aliases:
            inverted_aliases = {}
            for official_key, dirty_vals in aliases.items():
                if not isinstance(dirty_vals, list):
                    dirty_vals = [dirty_vals]
                for v in dirty_vals:
                    inverted_aliases[rf'\b{re.escape(v)}\b'] = official_key
            
            str_mask = series.apply(lambda x: isinstance(x, str))
            if str_mask.any():
                series.loc[str_mask] = series.loc[str_mask].replace(inverted_aliases, regex=True)

        if thousands_sep or (decimal_mark and decimal_mark != '.'):
            trans_dict = {}
            if thousands_sep:
                trans_dict[ord(thousands_sep)] = None
            if decimal_mark and decimal_mark != '.':
                trans_dict[ord(decimal_mark)] = ord('.')
                
            trans_table = str.maketrans(trans_dict) if trans_dict else None
            
            if trans_table:
                raw_list = series.tolist()
                cleaned_list = [
                    np.nan if (val != val or val is None or str(val).strip() in ('nan', 'None', ''))
                    else str(val).strip().translate(trans_table)
                    for val in raw_list
                ]
                series = pd.Series(cleaned_list, index=raw_series.index)

        return series