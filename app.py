# Imports
import argparse
import http.server
import http.client
import socketserver
import time
import urllib.request

from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.resources import SERVICE_NAME, Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import (
    BatchSpanProcessor,
    ConsoleSpanExporter,
)
from opentelemetry.trace.propagation.tracecontext import TraceContextTextMapPropagator


# Get arguments and settings
parser = argparse.ArgumentParser(
    prog="Simple Python Proxy Server",
    description="Serves a simple web server at the defined port and proxies it",
)
parser.add_argument("-p", "--port", default=8080)
parser.add_argument("-u", "--url", default="https://www.google.com")
parser.add_argument("-o", "--oltp", default=None)
args = parser.parse_args()

PORT = int(args.port)
PROXY = args.url
OLTP = args.oltp

# Set tracing configuration
resource = Resource(attributes={SERVICE_NAME: "python-proxy"})

provider = TracerProvider(resource=resource)
processor = BatchSpanProcessor(ConsoleSpanExporter())
if OLTP is not None:
    processor = BatchSpanProcessor(OTLPSpanExporter(endpoint=OLTP))

provider.add_span_processor(processor)
trace.set_tracer_provider(provider)
tracer = trace.get_tracer("pythonProxy.tracer")


# Define proxy server
def getProxyHandler(proxy):
    """
    Simple funtion that creates a `SimpleHTTPRequestHandler` that proxies
    requests to the defined URL
    """

    class proxyHandler(http.server.SimpleHTTPRequestHandler):
        def do_GET(self):
            # Get current context
            carrier = {}
            traceparent_header = self.headers.get("traceparent")
            if traceparent_header:
                carrier = {"traceparent": int(traceparent_header, 16)}
            ctx = TraceContextTextMapPropagator().extract(carrier=carrier)

            with tracer.start_as_current_span("root", ctx) as _:
                with tracer.start_as_current_span("sleep") as span:
                    sleep_duration = 2
                    time.sleep(sleep_duration)
                    span.set_attribute("sleep.duration", sleep_duration)

                with tracer.start_as_current_span("proxy") as span:
                    self.send_response(200)
                    span.set_attribute("proxy.url", proxy)
                    # Propagate trace id
                    self.send_header("traceparent", span.get_span_context().trace_id)
                    self.end_headers()
                    self.copyfile(urllib.request.urlopen(proxy), self.wfile)

    return proxyHandler


with socketserver.TCPServer(("", PORT), getProxyHandler(PROXY)) as httpd:
    print("PythonProxy")
    print(20 * "-")
    print("Serving at port", PORT)
    print("Forwarding to", PROXY)
    print("OLTP endpoint is set to", OLTP)
    httpd.serve_forever()
