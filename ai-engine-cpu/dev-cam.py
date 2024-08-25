import sys
from engine.utils import load_config
import time
import logging
import cv2
from engine.pipes.object_detectors.base.lp import LicensePlateDetector
from engine.pipes.number_plate_text_readers.base.ocr import Ocr

from logger.logger import init_logger
from engine.mqtt import MQTTEngine

try:
    # Load configuration
    config = load_config("config.yaml")
except:
    logging.error("INVALID CONFIG FILE.")
    sys.exit(1)

# Map logging level string to numerical constant
log_level = {
    "debug": logging.DEBUG,
    "info": logging.INFO,
    "warn": logging.WARNING,
    "warning": logging.WARNING,
    "error": logging.ERROR,
    "fatal": logging.FATAL,
    "critical": logging.CRITICAL,
}.get(
    config["logging"]["level"].lower(), logging.INFO
)  # Default to INFO if level is not recognized
# Initialize logger
init_logger(
    logging_level=log_level,
    print_to_stdout=config["logging"]["print_to_stdout"],
    log_in_file=config["logging"]["log_in_file"],
)
# Extract camera configuration
camera_config = config["camera"][0]
input_image_width = camera_config["image_size"]["width"]
input_image_height = camera_config["image_size"]["height"]
camera_regions = camera_config["regions"]


logging.debug("[OCR] Initializing OCR model...")
ocr = Ocr()
logging.debug("[OCR] Initializing OCR model - DONE.")

logging.debug("[OCR] Initializing label converter...")
ocr.init_label_converter()
logging.debug("[OCR] Initializing label converter - DONE.")
logging.debug("[OCR] Initializing weights...")
ocr.load_model(config["engine"]["ocr_model"])
logging.debug("[OCR] Initializing weights - DONE.")

# Load the object detection network
net = LicensePlateDetector(config["engine"])
net.load_model(config["engine"]["model"])

try:
    input_stream = cv2.VideoCapture(config["camera"][0]["input_stream"], cv2.CAP_FFMPEG)
except Exception as e:
    logging.error(f"Could not connect to video source: {e}")
    sys.exit(1)
if not input_stream.isOpened():
    logging.error(f"Could not open RTSP stream: {config['camera'][0]['input_stream']}")
    sys.exit(1)

# Max retries configuration
max_retries = config["engine"].get(
    "max_retries", 5
)  # Default to 5 retries if not specified in the config

# Initialize retry counter
retry_counter = 0

# process frames until the user exits
while True:
    try:
        # capture the next image
        ret, raw_img = input_stream.read()
        if not ret:
            logging.error("Failed to capture frame from RTSP stream.")
            raise ValueError("Failed to capture frame from RTSP stream.")

        logging.debug(f"Captured image type: {type(raw_img)}")
        logging.debug(f"Captured image attributes: {dir(raw_img)}")

        raw_img = cv2.resize(raw_img, (input_image_width, input_image_height))
        retry_counter = 0  # Reset counter on success
    except ValueError as e:
        logging.warning("Attempting to reconnect to RTSP stream...")
        input_stream.release()  # Clean up the old stream
        input_stream = cv2.VideoCapture(config["camera"][0]["input_stream"])
        
        if not input_stream.isOpened():
            logging.error(f"Could not reconnect to RTSP stream: {config['camera'][0]['input_stream']}")
            sys.exit(1)
        
        retry_counter += 1
        if retry_counter > max_retries:
            mqtt_message = {
                "error": "Max retries exceeded",
                "message": f"Error capturing and processing image: {e}",
            }
            # Send your MQTT message or handle the error accordingly
            logging.error("Max retries exceeded. Exiting...")
            sys.exit(1)
        time.sleep(5)  # Short delay before the next attempt
        continue
    except Exception as e:
        logging.error(f"Unexpected error: {e}")
        retry_counter += 1
        if retry_counter > max_retries:
            mqtt_message = {
                "error": "Max retries exceeded",
                "message": f"Unexpected error capturing and processing image: {e}",
            }
            logging.error("Max retries exceeded. Exiting...")
            sys.exit(1)
        time.sleep(5)  # Short delay before the next attempt
        continue

    # Extract regions based on the configuration
    for region in camera_regions:
        try:
            name = region["name"]
            coords = region["coordinates"]

            # Extract the top-left and bottom-right coordinates
            x1, y1 = coords[0]["x"], coords[0]["y"]
            x2, y2 = coords[2]["x"], coords[2]["y"]

            # Crop the region from the resized image
            region_img = raw_img[y1:y2, x1:x2, :]

            # detect objects in the image (with overlay)
            image_data = net.preprocess(region_img)
            detections = net.predict(image_data)
            # print the detections
            logging.debug(
                "[DET] Detected {:d} objects in region {}".format(len(detections), name)
            )

            for i, detection in enumerate(detections):
                try:
                    x_min = int(detection.Left * region_img.shape[1])
                    x_max = int(detection.Right * region_img.shape[1])
                    y_max = int(detection.Bottom * region_img.shape[0])
                    y_min = int(detection.Top * region_img.shape[0])

                    cropped_img = region_img[y_min:y_max, x_min:x_max, :]
                    cropped_img = cv2.resize(cropped_img, (300, 100))
                    cropped_img = cv2.cvtColor(cropped_img, cv2.COLOR_BGR2RGB)
                    logging.debug("[OCR] Preprocessing image.")
                    xs = ocr.preprocess([cropped_img])
                    logging.debug("[OCR] Image preprocessed.")
                    logging.debug("[OCR] Predicting.")
                    license_plate_text = ocr.predict(xs)[0]
                    logging.debug("[OCR] Predicted: {}".format(license_plate_text))

                    data = {}
                    data["licensePlate"] = license_plate_text
                    # Draw the detection and text on the full-sized raw_img
                    cv2.rectangle(
                        raw_img,
                        (x_min + x1, y_min + y1),
                        (x_max + x1, y_max + y1),
                        (0, 255, 0),
                        2,
                    )
                    cv2.putText(
                        raw_img,
                        license_plate_text,
                        (x_min + x1, y_min + y1 - 10),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.5,
                        (0, 0, 255),
                        2,
                    )
                    # logging.debug("========================================")
                except Exception as e:
                    logging.error(f"Error processing detection: {e}")
        except Exception as e:
            logging.error(f"Error processing region {region['name']}: {e}")

    # Exit if the stream ends or the user interrupts
    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

input_stream.release()
cv2.destroyAllWindows()
