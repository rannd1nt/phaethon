from typing import Protocol, Dict, Any

class DataFrameBackend(Protocol):
    def normalize(self, df: Any, fields: Dict[str, Any], schema_cls: Any, keep_unmapped: bool, drop_raw: bool) -> Any:
        ...