import logging
import uuid
from contextvars import ContextVar

_request_id_ctx: ContextVar[str] = ContextVar("request_id", default="-")


def set_request_id(request_id: str | None = None) -> str:
    request_id = request_id or uuid.uuid4().hex[:12]
    _request_id_ctx.set(request_id)
    return request_id


def get_request_id() -> str:
    return _request_id_ctx.get()


class RequestIdLogFilter(logging.Filter):
    """Injects the current request's id into every log record as %(request_id)s."""

    def filter(self, record: logging.LogRecord) -> bool:
        record.request_id = get_request_id()
        return True
