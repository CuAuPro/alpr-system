# Dockerfile for ai-engine
FROM dustynv/jetson-inference:r32.7.1

# Install any additional dependencies
RUN apt-get update

# Build and install jetson-inference
RUN cd /jetson-inference/build \
    && cmake -DENABLE_NVMM=off ../ \
    && make \
    && make install
    
# Set the working directory
WORKDIR /app

# Copy your application code
COPY . .

# https://stackoverflow.com/questions/77490435/attributeerror-cython-sources
RUN python3 -m pip install --upgrade pip
RUN pip3 install "cython<3.0.0" wheel
RUN pip3 install "pyyaml==5.4.1" --no-build-isolation
# Install Python dependencies
RUN python3 -m pip install -r requirements.txt

# Run your application
CMD ["python3", "main.py"]
