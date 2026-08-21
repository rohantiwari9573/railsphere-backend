import logging

from fastapi import FastAPI
from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.http.trace_exporter import (
    OTLPSpanExporter,
)
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.sdk.resources import SERVICE_NAME, Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor

from app.core.config import settings

logger = logging.getLogger("app")


def configure_tracing(app: FastAPI) -> None:
    """
    Instruments the app with OpenTelemetry request tracing, exporting
    spans to an OTLP/HTTP collector (e.g. Jaeger).

    A no-op unless OTEL_EXPORTER_OTLP_ENDPOINT is set: no tracer
    provider, exporter, or instrumentation is installed at all, so
    there's no memory or network cost on the production instance
    unless a collector is actually configured there.
    """
    if not settings.OTEL_EXPORTER_OTLP_ENDPOINT:
        return

    resource = Resource.create({SERVICE_NAME: settings.APP_NAME})
    provider = TracerProvider(resource=resource)
    exporter = OTLPSpanExporter(
        endpoint=f"{settings.OTEL_EXPORTER_OTLP_ENDPOINT}/v1/traces"
    )
    provider.add_span_processor(BatchSpanProcessor(exporter))
    trace.set_tracer_provider(provider)

    FastAPIInstrumentor.instrument_app(app)
    logger.info(
        "OpenTelemetry tracing enabled, exporting to %s",
        settings.OTEL_EXPORTER_OTLP_ENDPOINT,
    )
