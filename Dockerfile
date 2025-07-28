# File: Dockerfile

# Use an official Python runtime as a base image.
# IMPORTANT: Ensure this Python version matches the one specified in pyproject.toml
FROM python:3.12-slim-buster

# Set environment variables
ENV PYTHONUNBUFFERED 1
ENV APP_HOME /app

# Install Poetry within the container.
# Pin the Poetry version for consistent builds. Check https://python-poetry.org/docs/#installation for the latest stable.
RUN pip install poetry==1.8.2
# Add Poetry's bin directory to the PATH for subsequent commands
ENV PATH="/root/.local/bin:$PATH"

# Set the working directory inside the container
WORKDIR ${APP_HOME}

# Copy pyproject.toml and poetry.lock first to leverage Docker layer caching.
# If these files don't change, Docker can reuse this layer, speeding up builds.
COPY pyproject.toml poetry.lock ./

# Install project dependencies using Poetry.
# --no-root: Prevents Poetry from installing the project itself as an editable package.
#            This is important for 'src' layout where the code is copied separately.
# --no-dev: Skips installation of development dependencies (e.g., pytest).
RUN poetry install --no-root --no-dev

# Copy the rest of your application code into the container.
# This includes the 'src' directory and its contents.
COPY . .

# Expose the port that the application will listen on.
# Cloud Run injects the PORT environment variable, which Gunicorn will use.
EXPOSE 8080

# Command to run the application using Gunicorn.
# 'gemini_python_app.main:app' refers to the 'app' object in 'main.py'
# within the 'gemini_python_app' package (which is inside 'src').
# Gunicorn will listen on the port provided by Cloud Run.
CMD exec gunicorn --bind :$PORT --workers 1 --threads 8 --timeout 0 gemini_python_app.main:app
