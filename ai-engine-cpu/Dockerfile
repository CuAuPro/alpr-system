# Use a minimal base image suitable for ARM architecture
FROM arm64v8/ubuntu:20.04

# Install necessary dependencies
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        libgpiod-dev \
        python3-pip \
        libgl1-mesa-dev \
        libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Set the working directory
WORKDIR /app

# Copy requirements.txt and install Python dependencies
COPY requirements.txt .
RUN pip3 install -r requirements.txt

# Copy your application code
COPY . .

# Run your application
CMD [ "python3", "./main.py" ]
