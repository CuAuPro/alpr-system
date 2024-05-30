# Dockerfile for ai-engine
FROM dustynv/jetson-inference:r32.7.1

# Install any additional dependencies
RUN apt-get update

# Copy your application code
COPY . /app

# Set the working directory
WORKDIR /app

# Install Python dependencies
RUN python3 -m pip install -r requirements.txt

# Run your application
CMD ["python3", "main.py", "/dev/video0", "rtsp://@:8554/stream", "--model=./engine/models/model-detect.onnx", "--class_labels=./engine/models/labels-detect.txt", "--input_blob=input_0", "--output_cvg=scores", "--output_bbox=boxes", "--width=640", "--height=480", "--ocr_model=./engine/models/model-ocr.trt", "--headless"]
