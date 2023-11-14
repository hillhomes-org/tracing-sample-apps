# Base image
FROM python:3.9-slim

# Set the working directory to /app
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install dependencies
RUN pip install opentelemetry-sdk

# Make port 8080 available to the world outside this container
EXPOSE 8080

# Run the Python script with specified arguments
ENTRYPOINT ["python", "app.py"]
