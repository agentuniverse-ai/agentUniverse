"""Shared chronological history selection for SQL-backed memory stores."""

from sqlalchemy import inspect


def query_recent_records(query, model_class, timestamp_column, top_k):
    """Fetch recent ORM rows without loading the whole matching history.

    Positive integer limits select newest timestamps/primary keys first and
    reverse the bounded result for chronological output. Other values keep the
    existing Python-slice behavior. Mapped keys support custom converters too.
    """
    if isinstance(top_k, int) and top_k > 0:
        order = [timestamp_column.desc()]
        order.extend(column.desc() for column in inspect(model_class).primary_key)
        # SQLite binds LIMIT as a signed 64-bit integer.
        records = query.order_by(*order).limit(min(top_k, 2**63 - 1)).all()
        records.reverse()
        return records
    return query.order_by(timestamp_column.asc()).all()[-top_k:]
