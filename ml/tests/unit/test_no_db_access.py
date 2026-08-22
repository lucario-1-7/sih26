import inspect

import app.duplicate_detection.engine as duplicate_engine
import app.embeddings.engine as embeddings_engine
import app.matching.consortium as consortium_engine
import app.matching.engine as matching_engine
import app.scoring.field_intensity as field_intensity
import app.scoring.priority as priority
import app.scoring.tractability as tractability

FORBIDDEN = ("sqlalchemy", "psycopg", "asyncpg")


def test_ml_engine_modules_have_no_database_imports():
    modules = [
        duplicate_engine,
        embeddings_engine,
        consortium_engine,
        matching_engine,
        field_intensity,
        priority,
        tractability,
    ]
    for module in modules:
        src = inspect.getsource(module)
        for forbidden in FORBIDDEN:
            assert forbidden not in src, f"{module.__name__} must not reference {forbidden}"
