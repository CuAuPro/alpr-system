import onnxruntime as rt
import cv2
import numpy as np
from engine.pipes.object_detectors.base.lp import LicensePlateDetector
import time
from tqdm import tqdm

# Read and preprocess the image
raw_img = cv2.imread("data/4.png")

config = {}
config["top_n"] = 5
config["threshold"] = 0.5
net = LicensePlateDetector(config)
net.load_model("engine/models/model-detect.onnx")

time_start = time.time()
N = 100
for i in tqdm(range(N)):
    image_data = net.preprocess(raw_img)
    # Inference run using image_data as the input to the model
    detections = net.predict(image_data)

    for i, detection in enumerate(detections):
        x_min = int(detection.Left * raw_img.shape[1])
        x_max = int(detection.Right * raw_img.shape[1])
        y_max = int(detection.Bottom * raw_img.shape[0])
        y_min = int(detection.Top * raw_img.shape[0])
        confidence = detection.Confidence
time_end = time.time()

working_time = time_end - time_start
print(working_time / N)
