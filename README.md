# tracing-sample-apps
Sample Apps that produce tracing data

# Run Container
```
docker build -t python-proxy .
docker run -p 8080:8080 --name python-proxy -d python-proxy -u "https://www.heise.de"
```