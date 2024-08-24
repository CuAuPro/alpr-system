import onnxruntime as rt
import cv2
import numpy as np
from engine.pipes.number_plate_text_readers.base.ocr import Ocr
from engine.tools.ocr_tools import decode_batch
import time
from tqdm import tqdm

ocr = Ocr()
ocr.load_model("engine/models/model-ocr.onnx")
ocr.init_label_converter()


# Read and preprocess the image
raw_img = cv2.imread("data/RP70012.png")

time_start = time.time()
N = 100
for i in tqdm(range(N)):
    cropped_img = cv2.resize(raw_img, (300, 100))
    cropped_img = cv2.cvtColor(cropped_img, cv2.COLOR_BGR2RGB)
    image_data = ocr.preprocess([cropped_img])
    out = ocr.predict(image_data)
time_end = time.time()

working_time = time_end - time_start
print(working_time / N)
