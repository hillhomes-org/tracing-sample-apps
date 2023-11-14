import argparse
import http.server
import socketserver
import time

from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import (
    BatchSpanProcessor,
    ConsoleSpanExporter,
)

provider = TracerProvider()
processor = BatchSpanProcessor(ConsoleSpanExporter())
provider.add_span_processor(processor)

# Sets the global default tracer provider
trace.set_tracer_provider(provider)

tracer = trace.get_tracer(__name__)

parser = argparse.ArgumentParser(
    prog="Simple Python Proxy Server",
    description="Serves a simple web server at the defined port and proxies it",
)
parser.add_argument("-p", "--port", default=8080)
parser.add_argument("-u", "--url", default="https://www.google.com")
args = parser.parse_args()

PORT = int(args.port)
PROXY = args.url


def getProxyHandler(proxy):
    """
    Simple funtion that creates a `SimpleHTTPRequestHandler` that proxies
    requests to the defined URL
    """

    class proxyHandler(http.server.SimpleHTTPRequestHandler):
        def do_GET(self):
            with tracer.start_as_current_span("root") as root_span:
                with tracer.start_as_current_span("sleep") as span:
                    sleep_duration = 2
                    time.sleep(sleep_duration)
                    span.set_attribute("sleep.duration", sleep_duration)

                with tracer.start_as_current_span("proxy") as span:
                    self.send_response(301)
                    span.set_attribute("proxy.url", proxy)
                    self.send_header("Location", proxy)
                    self.end_headers()

    return proxyHandler


with socketserver.TCPServer(("", PORT), getProxyHandler(PROXY)) as httpd:
    print("PythonProxy")
    print(20 * "-")
    print("Serving at port", PORT)
    print("Forwarding to", PROXY)
    httpd.serve_forever()
