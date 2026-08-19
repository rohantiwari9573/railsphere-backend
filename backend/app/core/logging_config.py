import logging

from app.core.config import settings


def configure_logging() -> None:
    """
    Configure root and third-party loggers.

    Gunicorn/uvicorn already log HTTP access/errors to stdout/stderr
    (captured by systemd journal in production). This adds a consistent
    formatter and level for the application's own loggers.
    """
    level = logging.DEBUG if settings.DEBUG else logging.INFO

    logging.basicConfig(
        level=level,
        format="%(asctime)s %(levelname)-8s %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    logging.getLogger("uvicorn").setLevel(level)
    logging.getLogger("uvicorn.access").setLevel(level)
    logging.getLogger("sqlalchemy.engine").setLevel(
        logging.INFO if settings.DEBUG else logging.WARNING
    )
