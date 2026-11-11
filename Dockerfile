# Use an official Python runtime as a parent image
FROM python:3.12-slim

# Set the working directory to /app
WORKDIR /app

# Install cron first so layer caching survives code changes
RUN apt-get update \
    && apt-get install -y --no-install-recommends cron \
    && rm -rf /var/lib/apt/lists/*

# Install any needed packages specified in requirements.txt
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the current directory contents into the container at /app
COPY . /app

# Copy the cron configuration file into the container
# (this file lives in /etc/cron.d, so its entries need the "root" user field)
COPY crontab /etc/cron.d/bfx_rate_cron

# Give execution rights to the cron file
RUN chmod 0644 /etc/cron.d/bfx_rate_cron

# Create the log file
RUN touch /var/log/cron.log

# Export the container environment to /etc/environment so cron jobs can see it
# (cron does not inherit the container's runtime environment), then run cron.
CMD printenv > /etc/environment && cron -f -l 2
