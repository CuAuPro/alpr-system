# Use a minimal base image suitable for ARM architecture
FROM arm64v8/ubuntu:20.04

# Install necessary dependencies
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        libgpiod-dev \
        python3-pip \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Set the working directory
WORKDIR /app

# Copy requirements.txt and install Python dependencies
COPY . .
RUN pip3 install -r requirements.txt

CMD [ "python3", "./main.py"]