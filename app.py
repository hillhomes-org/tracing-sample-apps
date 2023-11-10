import argparse
import http.server
import socketserver

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
            self.send_response(301)
            self.send_header("Location", proxy)
            self.end_headers()

    return proxyHandler


with socketserver.TCPServer(("", PORT), getProxyHandler(PROXY)) as httpd:
    print("PythonProxy")
    print(20 * "-")
    print("Serving at port", PORT)
    print("Forwarding to", PROXY)
    httpd.serve_forever()
