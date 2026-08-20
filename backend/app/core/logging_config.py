import logging

from app.core.config import settings
from app.core.request_context import RequestIdLogFilter


def configure_logging() -> None:
    """
    Configure root and third-party loggers.

    Gunicorn/uvicorn already log HTTP access/errors to stdout/stderr
    (captured by systemd journal in production). This adds a consistent
    formatter and level for the application's own loggers, and tags
    every line with the request id of the request that triggered it
    (see app/core/request_context.py) so a single request's log lines
    can be grepped out of a busy production log.
    """
    level = logging.DEBUG if settings.DEBUG else logging.INFO

    logging.basicConfig(
        level=level,
        format=(
            "%(asctime)s %(levelname)-8s [%(request_id)s] "
            "%(name)s: %(message)s"
        ),
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # Filters must live on the handler (not the root logger) to apply to
    # records from child loggers -- propagation calls handlers directly
    # and never re-runs an ancestor logger's own .filter().
    request_id_filter = RequestIdLogFilter()
    for handler in logging.getLogger().handlers:
        handler.addFilter(request_id_filter)

    logging.getLogger("uvicorn").setLevel(level)
    logging.getLogger("uvicorn.access").setLevel(level)
    logging.getLogger("sqlalchemy.engine").setLevel(
        logging.INFO if settings.DEBUG else logging.WARNING
    )
