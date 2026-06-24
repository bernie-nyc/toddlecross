# We use Python version 3.11 lightweight slim image as our starting base.
FROM python:3.11-slim

# This setting prevents Python from buffering standard output and error,
# allowing us to see logs instantly in our deployment terminal.
ENV PYTHONUNBUFFERED=1

# This setting tells Django where our production settings module is.
ENV DJANGO_SETTINGS_MODULE=config.settings

# We set the default directory inside the container where our code will live.
WORKDIR /app

# We install system packages that might be needed by some libraries.
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# We copy only the requirements file first.
# Doing this allows Docker to cache our installed packages between builds.
COPY requirements.txt /app/

# We install all the Python libraries listed in our requirements file.
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# We copy the rest of our application code into the container.
COPY . /app/

# We make sure the startup entrypoint script is executable.
RUN chmod +x /app/entrypoint.sh

# We expose port 8080. This is the port where our web application will listen.
EXPOSE 8080

# We tell Docker to run our entrypoint script when the container starts.
ENTRYPOINT ["/app/entrypoint.sh"]
