# Dockerfile for ai-engine
FROM dustynv/jetson-inference:r32.7.1

# Install any additional dependencies
RUN apt-get update

# Set the working directory
WORKDIR /app

# Copy your application code
COPY . .

# Install Python dependencies
RUN python3 -m pip install -r requirements.txt

# Run your application
CMD ["python3", "main.py"]
