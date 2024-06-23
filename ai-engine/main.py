

import jetson.inference
import jetson.utils

import argparse
import sys
from engine.utils import load_config
import torch
import pycuda.driver as cuda
import time
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

# Map logging level string to numerical constant
log_level = {
    "debug": logging.DEBUG,
    "info": logging.INFO,
    "warn": logging.WARNING,
    "warning": logging.WARNING,
    "error": logging.ERROR,
    "fatal": logging.FATAL,
    "critical": logging.CRITICAL
}.get(config['logging']['level'].lower(), logging.INFO)  # Default to INFO if level is not recognized
# Initialize logger
init_logger(logging_level=log_level, 
            print_to_stdout=config['logging']['print_to_stdout'], 
            log_in_file=config['logging']['log_in_file'])

# Extract camera configuration
camera_config = config['camera'][0]
input_image_width = camera_config['image_size']['width']
input_image_height = camera_config['image_size']['height']
camera_regions = camera_config['regions']

# MQTT configuration
mqtt_config = {
    'broker': config['mqtt']['broker'],
    'port': config['mqtt']['port'],
    'clientId': config['mqtt']['clientId'],
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
ocr.load(config['engine']['ocr_model'])
logging.debug("[OCR] Initializing weights - DONE.")

argv = [
        "--model=" + config['engine']['model'],
        "--class_labels=" + config['engine']['class_labels'],
        "--input_blob=" + config['engine']['input_blob'],
        "--output_cvg=" + config['engine']['output_cvg'],
        "--output_bbox=" + config['engine']['output_bbox'],
        "--input-width=" + str(config['engine']['width']),
        "--input-height=" + str(config['engine']['height'])
    ]
# Load the object detection network
net = jetson.inference.detectNet(
    config['engine']['network'],
    argv,
    config['engine']['threshold']
    )

# Create video sources & outputs
is_headless = ["--headless"] if config['engine']['headless'] else []
input_stream = jetson.utils.videoSource(config['camera'][0]['input_stream'], argv)
output_stream = jetson.utils.videoOutput(config['camera'][0]['output_stream'], argv=argv+is_headless)
#capture = cv2.VideoCapture(camera_config['input_stream'])


# Max retries configuration
max_retries = config['engine'].get('max_retries', 5)  # Default to 5 retries if not specified in the config

# Initialize retry counter
retry_counter = 0

# process frames until the user exits
while True:
    try:
        # capture the next image
        img = input_stream.Capture()
        raw_img = jetson.utils.cudaToNumpy(img)
        raw_img = cv2.resize(raw_img, (input_image_width, input_image_height))
        retry_counter = 0  # Reset counter on success
    except Exception as e:
        logging.error(f"Error capturing and processing image: {e}")
        retry_counter += 1
        if retry_counter > max_retries:
            mqtt_message = {
                "error": "Max retries exceeded",
                "message": f"Error capturing and processing image: {e}"
            }
            mqtt_engine.publish(mqtt_message, "alpr/ai-engine/error")
            break  # Exit the loop after exceeding max retries
        time.sleep(1)  # Wait for a short period before trying again
        continue
    # Extract regions based on the configuration
    for region in camera_regions:
        try:
            name = region['name']
            coords = region['coordinates']
            
            # Extract the top-left and bottom-right coordinates
            x1, y1 = coords[0]['x'], coords[0]['y']
            x2, y2 = coords[2]['x'], coords[2]['y']
            
            # Crop the region from the resized image
            region_img = raw_img[y1:y2, x1:x2, :]
            
            img = jetson.utils.cudaFromNumpy(region_img)
            # detect objects in the image (with overlay)
            detections = net.Detect(img, overlay=config['engine'].get('overlay', "box,labels,conf"))

            # print the detections
            logging.debug("[DET] Detected {:d} objects in region {}".format(len(detections), name))

            for i, detection in enumerate(detections):
                try:
                    x_min = int(detection.Left)
                    x_max = int(detection.Right)
                    y_max = int(detection.Bottom)
                    y_min = int(detection.Top)

                    cropped_img = region_img[y_min:y_max, x_min:x_max, :]
                    cropped_img = cv2.resize(cropped_img, (300,100))
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
                    # Draw the detection and text on the full-sized raw_img
                    cv2.rectangle(raw_img, (x_min + x1, y_min + y1), (x_max + x1, y_max + y1), (0, 255, 0), 2)
                    cv2.putText(raw_img, license_plate_text, (x_min + x1, y_min + y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
                    #logging.debug("========================================")
                except Exception as e:
                    logging.error(f"Error processing detection: {e}")
        except Exception as e:
            logging.error(f"Error processing region {region['name']}: {e}")
    try:
        # render the image
        img = jetson.utils.cudaFromNumpy(raw_img)
        output_stream.Render(img)

        # update the title bar
        output_stream.SetStatus("{:s} | Network {:.0f} FPS".format(config['engine']['network'], net.GetNetworkFPS()))

        # print out performance info
        logging.debug("Network {:.0f} FPS".format(net.GetNetworkFPS()))
        logging.debug("========================================")
    except Exception as e:
        logging.error(f"Error rendering image: {e}")
    # exit on input/output EOS
    if not input_stream.IsStreaming() or not output_stream.IsStreaming():
       break

