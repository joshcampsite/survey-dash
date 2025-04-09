# Dockerfile

# Use an official Python runtime as a parent image
FROM python:3.12-slim

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container at /app
COPY requirements.txt .

# Install any needed packages specified in requirements.txt
# Use --no-cache-dir to reduce image size
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code into the container at /app
COPY . .

# Make port 8080 available to the world outside this container
# Cloud Run expects the container to listen on the port defined by the PORT env var ($PORT), defaulting to 8080
EXPOSE 8080

# Define environment variable (optional, good practice)
ENV PORT=8080

# Run app.py using gunicorn when the container launches
# Make sure 'app' matches the variable name you assigned dash.Dash() to (app = dash.Dash(...))
# Make sure 'app:server' points to your Dash app's underlying Flask server instance
# Use 0.0.0.0 to bind to all network interfaces within the container
# Use $PORT environment variable Cloud Run provides
# Correct "shell" form for variable expansion
CMD gunicorn --bind 0.0.0.0:$PORT dashboard:app.server
