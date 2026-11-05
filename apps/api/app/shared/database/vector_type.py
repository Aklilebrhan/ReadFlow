import json
from typing import List, Optional
from sqlalchemy import types
from pgvector.sqlalchemy import Vector


class CompatibleVector(types.TypeDecorator):
    """
    Polymorphic Vector Type that renders as pgvector.sqlalchemy.Vector on PostgreSQL,
    and as a JSON-encoded Text string on SQLite/other databases.
    """
    impl = types.Text
    cache_ok = True

    def __init__(self, dim: int = 384, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.dim = dim

    def load_dialect_impl(self, dialect):
        if dialect.name == "postgresql":
            return dialect.type_descriptor(Vector(self.dim))
        return dialect.type_descriptor(types.Text())

    def process_bind_param(self, value: Optional[List[float]], dialect):
        if value is None:
            return None
        if dialect.name == "postgresql":
            return value
        return json.dumps(value)

    def process_result_value(self, value, dialect) -> Optional[List[float]]:
        if value is None:
            return None
        if isinstance(value, list):
            return [float(x) for x in value]
        if isinstance(value, str):
            try:
                parsed = json.loads(value)
                return [float(x) for x in parsed]
            except Exception:
                return None
        return list(value)
