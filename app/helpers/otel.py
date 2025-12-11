import os

from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import \
    OTLPSpanExporter
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor

from app.helpers.utils import strtobool


def setup_trace_provider(worker_pid):
    trace.set_tracer_provider(TracerProvider(resource=Resource.create()))

    # Since we created a new tracer, the default span processor is gone. We need to
    # create a new one using the default OTEL env variables and ad it to the tracer.
    span_processor = BatchSpanProcessor(
        OTLPSpanExporter(
            endpoint=os.getenv('OTEL_EXPORTER_OTLP_ENDPOINT', "http://localhost:4317"),
            headers=os.getenv('OTEL_EXPORTER_OTLP_HEADERS'),
            insecure=strtobool(os.getenv('OTEL_EXPORTER_OTLP_INSECURE', "false"))
        )
    )
    trace.get_tracer_provider().add_span_processor(span_processor)
