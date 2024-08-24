import onnxruntime as rt
import cv2
import numpy as np
from engine.pipes.object_detectors.base.lp import LicensePlateDetector
from engine.pipes.number_plate_text_readers.base.ocr import Ocr

import time
from tqdm import tqdm


# Read and preprocess the image
image_path = "data/"
image_name = "4.png"
raw_img = cv2.imread(image_path + image_name)

config = {}
config["top_n"] = 5
config["threshold"] = 0.5
net = LicensePlateDetector(config)
net.load_model("engine/models/model-detect.onnx")

ocr = Ocr()
ocr.load_model("engine/models/model-ocr.onnx")
ocr.init_label_converter()


time_start = time.time()

image_data = net.preprocess(raw_img)
# Inference run using image_data as the input to the model
detections = net.predict(image_data)


for i, detection in enumerate(detections):
    x_min = int(detection.Left * raw_img.shape[1])
    x_max = int(detection.Right * raw_img.shape[1])
    y_max = int(detection.Bottom * raw_img.shape[0])
    y_min = int(detection.Top * raw_img.shape[0])
    confidence = detection.Confidence

    cropped_img = raw_img[y_min:y_max, x_min:x_max, :]
    cropped_img = cv2.resize(cropped_img, (300, 100))
    cropped_img = cv2.cvtColor(cropped_img, cv2.COLOR_BGR2RGB)
    xs = ocr.preprocess([cropped_img])
    license_plate_text = ocr.predict(xs)[0]
    cv2.rectangle(raw_img, (x_min, y_min), (x_max, y_max), (0, 255, 0), 2)
    cv2.putText(
        raw_img,
        license_plate_text,
        (x_min, y_min - 10),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.5,
        (0, 0, 255),
        2,
    )
    img_name_parts = image_name.split(".")
    cv2.imwrite(
        image_path + img_name_parts[0] + "_result." + img_name_parts[1], raw_img
    )
    print(license_plate_text)

time_end = time.time()

working_time = time_end - time_start
print(working_time)
