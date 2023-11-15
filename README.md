# tracing-sample-apps
Sample Python app that produces tracing data.

The app provides the following configurations:
```
usage: Simple Python Proxy Server [-h] [-p PORT] [-u URL] [-o OLTP]

Serves a simple web server at the defined port and proxies it

options:
  -h, --help            show this help message and exit
  -p PORT, --port PORT
  -u URL, --url URL
  -o OLTP, --oltp OLTP
```
- `-p` or `--port` provides the port of the server (default: 8080)
- `-u` or `--url` provides the url that will be proxied to (default: `https://www.google.com`)
- `-o` or `--oltp` provides an OLTP endpoint to export traces (default: `None`). If no endpoint is provided, traces will be logged to console.

To start the app manually, execute:
```
pipenv install .
pipenv run python app.py
```

# Run Container
## Quickstart
```
docker build -t python-proxy .
docker run -p 8080:8080 --name python-proxy -d python-proxy -u "https://www.heise.de"
```

## Collect Tracing Data
First, install Jaeger:
```
docker run --rm `
  -e COLLECTOR_ZIPKIN_HOST_PORT=:9411 `
  -p 16686:16686 `
  -p 4317:4317 `
  -p 4318:4318 `
  -p 9411:9411 `
  -d jaegertracing/all-in-one:latest
```
The Jaeger UI will be accessible at port 16686. OLTP will be enabled on ports 4317 and 4318.

Now let's try to send data to Jaeger:
```
docker run -p 8080:8080 --name python-proxy --add-host host.docker.internal:host-gateway -d python-proxy -o http://host.docker.internal:4317
```
Note that we need to add the `--add-host host.docker.internal:host-gateway` option in order to reach Jaeger, which is running on `localhost`, from inside our Docker container.

## Docker Hub
I created a dummy user on Docker Hub to publish the image. The username is `hillhomes`.
```
docker login
docker build -t hillhomes/python-proxy:v0.0.2 .
docker push hillhomes/python-proxy:v0.0.2
```
This way we can add a corresponding deployment to our Flux Repository and test our Grafana Tempo application.

Hence, the app can be run as follows as well:
```
docker run -p 8080:8080 --name python-proxy -d hillhomes/python-proxy:v0.0.2
```