

import jetson.inference
import jetson.utils

import argparse
import sys

import torch
import pycuda.driver as cuda

import logging
import cv2
from engine.pipes.number_plate_text_readers.base.ocr_trt import OcrTrt

from logger.logger import init_logger
from engine.mqtt import MQTTEngine
# parse the command line
# parse the command line
parser = argparse.ArgumentParser(description="Locate objects in a live camera stream using an object detection DNN.", 
                                 formatter_class=argparse.RawTextHelpFormatter, epilog=jetson.inference.detectNet.Usage() +
                                 jetson.utils.videoSource.Usage() + jetson.utils.videoOutput.Usage() + jetson.utils.logUsage())

parser.add_argument("input_URI", type=str, default="", nargs='?', help="URI of the input stream")
parser.add_argument("output_URI", type=str, default="", nargs='?', help="URI of the output stream")
parser.add_argument("--network", type=str, default="ssd-mobilenet-v2", help="pre-trained model to load (see below for options)")
parser.add_argument("--overlay", type=str, default="box,labels,conf", help="detection overlay flags (e.g. --overlay=box,labels,conf)\nvalid combinations are:  'box', 'labels', 'conf', 'none'")
parser.add_argument("--threshold", type=float, default=0.5, help="minimum detection threshold to use") 

parser.add_argument("--ocr_model", type=str, default="", help="OCR model path")


is_headless = ["--headless"] if sys.argv[0].find('console.py') != -1 else [""]

try:
	opt = parser.parse_known_args()[0]
except:
	logging.debug("")
	parser.print_help()
	sys.exit(0)

init_logger(logging_level=logging.INFO, print_to_stdout=False, log_in_file=True)

config = {  'broker': 'databus',
            'port': 8883,
            'client_id': 'ai-engine',
            'tls_ca_cert': './certs/ca.crt',
            'tls_certfile': './certs/databus-ai-engine.crt',
            'tls_keyfile': './certs/databus-ai-engine.key',
            }
mqtt_engine = MQTTEngine(config)
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
ocr.load(opt.ocr_model)
logging.debug("[OCR] Initializing weights - DONE.")

        
# load the object detection network
net = jetson.inference.detectNet(opt.network, sys.argv, opt.threshold)

# create video sources & outputs
input = jetson.utils.videoSource(opt.input_URI, argv=sys.argv)
output = jetson.utils.videoOutput(opt.output_URI, argv=sys.argv+is_headless)

# process frames until the user exits
while True:
    # capture the next image
    img = input.Capture()
    raw_img = jetson.utils.cudaToNumpy(img)
    # detect objects in the image (with overlay)
    detections = net.Detect(img, overlay=opt.overlay)

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
    output.SetStatus("{:s} | Network {:.0f} FPS".format(opt.network, net.GetNetworkFPS()))

    # print out performance info
    #net.PrintProfilerTimes()
    logging.debug("Network {:.0f} FPS".format(net.GetNetworkFPS()))
    logging.debug("========================================")
    # exit on input/output EOS
    if not input.IsStreaming() or not output.IsStreaming():
       break

