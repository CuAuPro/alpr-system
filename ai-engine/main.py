

import jetson.inference
import jetson.utils

import argparse
import sys
from engine.utils import load_config
import torch
import pycuda.driver as cuda

import logging
import cv2
from engine.pipes.number_plate_text_readers.base.ocr_trt import OcrTrt

from logger.logger import init_logger
from engine.mqtt import MQTTEngine

try:
    # Load configuration
    config = load_config('config.yaml')
except:
	logging.error("INVALID CONFIG FILE.")
	sys.exit(0)

init_logger(logging_level=config['logging']['level'], 
            print_to_stdout=config['logging']['print_to_stdout'], 
            log_in_file=config['logging']['log_in_file'])

# MQTT configuration
mqtt_config = {
    'broker': config['mqtt']['broker'],
    'port': config['mqtt']['port'],
    'client_id': config['mqtt']['clientId'],
    'auth': {
        'username': config['mqtt']['auth']['username'],
        'password': config['mqtt']['auth']['password']
    },
    'tls': {
        'ca': config['mqtt']['tls']['ca'],
        'cert': config['mqtt']['tls']['cert'],
        'key': config['mqtt']['tls']['key']
    }
}
mqtt_engine = MQTTEngine(mqtt_config)
mqtt_engine.client.tls_insecure_set(True)
mqtt_engine.connect()
mqtt_engine.client.loop_start()
    
logging.debug(torch.cuda.is_available())
ctx = cuda.Device(0).make_context()
stream = cuda.Stream()

logging.debug("[OCR] Initializing OCR model...")
ocr = OcrTrt()
logging.debug("[OCR] Initializing OCR model - DONE.")

logging.debug("[OCR] Initializing label converter...")
ocr.init_label_converter()
logging.debug("[OCR] Initializing label converter - DONE.")
logging.debug("[OCR] Initializing weights...")
ocr.load(config['ocr_model'])
logging.debug("[OCR] Initializing weights - DONE.")

        
# Load the object detection network
net = jetson.inference.detectNet(config['network'], config['threshold'], [
    "--class_labels=" + config['class_labels'],
    "--input_blob=" + config['input_blob'],
    "--output_cvg=" + config['output_cvg'],
    "--output_bbox=" + config['output_bbox'],
    "--width=" + str(config['width']),
    "--height=" + str(config['height'])
])

# Create video sources & outputs
is_headless = ["--headless"] if config['headless'] else []
input = jetson.utils.videoSource(config['camera'][0]['input_stream'], argv=is_headless)
output = jetson.utils.videoOutput(config['camera'][0]['output_stream'], argv=is_headless)

# process frames until the user exits
while True:
    # capture the next image
    img = input.Capture()
    raw_img = jetson.utils.cudaToNumpy(img)
    # detect objects in the image (with overlay)
    detections = net.Detect(img, overlay=config.get('overlay', "box,labels,conf"))

    # print the detections
    logging.debug("detected {:d} objects in image".format(len(detections)))

    for i, detection in enumerate(detections):
        x_min = int(detection.Left)
        x_max = int(detection.Right)
        y_max = int(detection.Bottom)
        y_min = int(detection.Top)

        cropped_img = raw_img[y_min:y_max, x_min:x_max, :]
        cropped_img = cv2.cvtColor(cropped_img, cv2.COLOR_BGR2RGB)
        ctx.push()
        #logging.debug("[OCR] Preprocessing image.")
        xs = ocr.preprocess([cropped_img])
        #logging.debug("[OCR] Image preprocessed.")
        #logging.debug("[OCR] Predicting.")
        license_plate_text = ocr.predict(xs, stream)[0]
        ctx.pop()
        logging.debug("[OCR] Predicted: {}".format(license_plate_text))
        
        data = {}
        data["licensePlate"] = license_plate_text
        mqtt_engine.publish(data, "alpr/ramp/req")
        # Draw bounding box
        cv2.rectangle(raw_img, (x_min, y_min), (x_max, y_max), (0, 255, 0), 2)
        cv2.putText(raw_img, license_plate_text, (x_min, y_min - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
        #logging.debug("========================================")
    # render the image
    
    img = jetson.utils.cudaFromNumpy(raw_img)
    output.Render(img)

    # update the title bar
    output.SetStatus("{:s} | Network {:.0f} FPS".format(config['network'], net.GetNetworkFPS()))

    # print out performance info
    #net.PrintProfilerTimes()
    logging.debug("Network {:.0f} FPS".format(net.GetNetworkFPS()))
    logging.debug("========================================")
    # exit on input/output EOS
    if not input.IsStreaming() or not output.IsStreaming():
       break

