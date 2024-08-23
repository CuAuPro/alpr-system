

import numpy as np
from typing import List, Tuple, Any, Dict
from engine.tools.image_processing import normalize_img
from engine.tools.ocr_tools import StrLabelConverter, decode_batch
import onnxruntime as rt 
import cv2

class LicensePlateDetector():
    def __init__(self, config) -> None:
        self.input_name = None
        self.output_names = None

        
        self.width = 300
        self.height = 300
        self.color_channels  = 3
        
        self.confidence_threshold = config['threshold']
        self.top_n = config['top_n']



    def load_model(self, engine_file_path):
        self.engine = rt.InferenceSession(engine_file_path) 
        self.input_name = self.engine.get_inputs()[0].name
        # Get the output names
        self.output_names = [s.name for s in self.engine.get_outputs()]
        return self.engine
    
    
    def preprocess(self, img, need_preprocess=True):
        if need_preprocess:
            image_data = cv2.resize(img, (self.width, self.height)).astype(np.float32)
        # Reorder dimensions to match model's expected input (1, channels, height, width)
        image_data = np.transpose(image_data, (2, 0, 1))  # (height, width, channels) -> (channels, height, width)
        # Add batch dimension: (1, channels, height, width)
        image_data = np.expand_dims(image_data, axis=0)
        return image_data

    def predict(self, xs: np.ndarray, return_acc: bool = False) -> Any:
        
        out = self.engine.run(self.output_names, {self.input_name: xs})

        # Extract scores and boxes
        scores = out[0]  # shape: (1, 3000, 2)
        boxes = out[1]   # shape: (1, 3000, 4)
        
        # Squeeze the arrays to remove the batch dimension
        scores = np.squeeze(scores, axis=0)
        boxes = np.squeeze(boxes, axis=0)

        # Flatten the confidence scores and box coordinates
        confidence_scores = scores[:, 1]  # Assuming the second value is the confidence score for the license plate class
        boxes_above_threshold = boxes[confidence_scores > self.confidence_threshold]
        confidences_above_threshold = confidence_scores[confidence_scores > self.confidence_threshold]

        # Sort by confidence and select the top N detections
        top_indices = np.argsort(confidences_above_threshold)[-self.top_n:][::-1]  # Sort descending and get top N indices

        top_boxes = boxes_above_threshold[top_indices]
        top_confidences = confidences_above_threshold[top_indices]
        
        # Prepare the list of detection objects
        detections = []
        for box, confidence in zip(top_boxes, top_confidences):
            # Scale the coordinates to the original image size
            x_min = box[0]
            y_min = box[1]
            x_max = box[2]
            y_max = box[3]

            # Create a detection object (simulating the structure you expect)
            detection = type('Detection', (object,), {})()
            detection.Left = x_min
            detection.Right = x_max
            detection.Top = y_min
            detection.Bottom = y_max
            detection.Confidence = confidence

            detections.append(detection)
        
        return detections