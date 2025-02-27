# Use an official Python runtime as a parent image
FROM python:3.9-slim-buster

# Set the working directory to /app
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Update package lists
RUN apt-get update && apt-get upgrade -y

# Install cron
RUN apt-get install -y cron



# Copy the cron configuration file into the container
COPY crontab /etc/cron.d/bfx_rate_cron

# Give execution rights to the cron file
RUN chmod 0644 /etc/cron.d/bfx_rate_cron

# Apply cron job
RUN crontab /etc/cron.d/bfx_rate_cron
# Create the log file
RUN touch /var/log/cron.log

# Run cron and the python script when the container launches
CMD printenv > /etc/environment && cron -f -l 2
