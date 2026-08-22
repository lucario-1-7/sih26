import logging
import sys


def configure_logging(level: str = "INFO") -> None:
    root = logging.getLogger()
    if root.handlers:
        return
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(
        logging.Formatter(
            fmt='{"time":"%(asctime)s","level":"%(levelname)s","logger":"%(name)s","message":"%(message)s"}'
        )
    )
    root.addHandler(handler)
    root.setLevel(level)

    # Never let uvicorn/sqlalchemy leak query params containing PII by default.
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
