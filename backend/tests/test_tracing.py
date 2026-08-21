from fastapi import FastAPI
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor

from app.core.config import settings
from app.core.tracing import configure_tracing


def test_configure_tracing_is_a_noop_without_an_endpoint(monkeypatch):
    monkeypatch.setattr(settings, "OTEL_EXPORTER_OTLP_ENDPOINT", "")
    app = FastAPI()

    configure_tracing(app)

    assert getattr(app, "_is_instrumented_by_opentelemetry", False) is False


def test_configure_tracing_instruments_app_when_endpoint_set(monkeypatch):
    monkeypatch.setattr(
        settings, "OTEL_EXPORTER_OTLP_ENDPOINT", "http://localhost:4318"
    )
    app = FastAPI()

    try:
        configure_tracing(app)
        assert app._is_instrumented_by_opentelemetry is True
    finally:
        FastAPIInstrumentor().uninstrument_app(app)
