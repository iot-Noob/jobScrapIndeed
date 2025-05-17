# Use the official Selenium Standalone Chrome image as the base
FROM selenium/standalone-chrome:latest

# Switch to root to install OS packages
USER root

# Update and install system tools
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    python3-dev \
    libffi-dev \
    libssl-dev \
    net-tools \
    vim \
    iputils-ping \
    dnsutils \
    htop \
    nano \
    python3-pip && \
    rm -rf /var/lib/apt/lists/*

RUN python3 --version

# Copy and install Python dependencies
COPY requirements.txt /tmp/requirements.txt
RUN pip3 install --no-cache-dir -r /tmp/requirements.txt

# Copy the application code
COPY . /app
WORKDIR /app

# Expose ports if needed (optional, for debugging or API)
EXPOSE 4444

# Make your project folders mountable if needed
VOLUME ["/app/csv_dir", "/app/Scrap_volume"]

# Set the default command
CMD ["python3", "main.py"]
