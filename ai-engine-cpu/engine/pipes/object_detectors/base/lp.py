import numpy as np
import cv2
import onnxruntime as rt


class LicensePlateDetector:
    def __init__(self, config) -> None:
        self.input_name = None
        self.output_names = None

        self.width = 300
        self.height = 300
        self.color_channels = 3

        self.confidence_threshold = config['threshold']
        self.top_n = config['top_n']

    def load_model(self, engine_file_path):
        self.engine = rt.InferenceSession(engine_file_path) 
        self.input_name = self.engine.get_inputs()[0].name
        self.output_names = [s.name for s in self.engine.get_outputs()]
        return self.engine

    def preprocess(self, img, need_preprocess=True):
        if need_preprocess:
            image_data = cv2.resize(img, (self.width, self.height)).astype(np.float32)
        image_data = np.transpose(image_data, (2, 0, 1))  
        image_data = np.expand_dims(image_data, axis=0)
        return image_data

    def initial_filtering(self, scores, boxes):
        # Flatten the confidence scores and box coordinates
        confidence_scores = scores[:, 1]  
        boxes_above_threshold = boxes[confidence_scores > self.confidence_threshold]
        confidences_above_threshold = confidence_scores[confidence_scores > self.confidence_threshold]

        # Sort by confidence and select the top N detections
        top_indices = np.argsort(confidences_above_threshold)[-self.top_n:][::-1]  

        top_boxes = boxes_above_threshold[top_indices]
        top_confidences = confidences_above_threshold[top_indices]

        return top_boxes, top_confidences

    def predict(self, xs: np.ndarray):
        out = self.engine.run(self.output_names, {self.input_name: xs})

        # Extract scores and boxes
        scores = np.squeeze(out[0], axis=0)  # shape: (3000, 2)
        boxes = np.squeeze(out[1], axis=0)   # shape: (3000, 4)

        # Perform initial filtering
        top_boxes, top_confidences = self.initial_filtering(scores, boxes)

        # Apply Non-Maximum Suppression (NMS)
        final_boxes, final_confidences  = self.non_maximum_suppression(top_boxes, top_confidences)

        # Prepare the list of detection objects
        detections = []
        for box, confidence in zip(final_boxes, final_confidences):
            x_min = box[0]
            y_min = box[1]
            x_max = box[2]
            y_max = box[3]

            detection = type('Detection', (object,), {})()
            detection.Left = x_min
            detection.Right = x_max
            detection.Top = y_min
            detection.Bottom = y_max
            detection.Confidence = confidence

            detections.append(detection)
        
        return detections

    def non_maximum_suppression(self, boxes, confidences, iou_threshold=0.5):
        if len(boxes) == 0:
            return []

        x1 = boxes[:, 0]
        y1 = boxes[:, 1]
        x2 = boxes[:, 2]
        y2 = boxes[:, 3]

        areas = (x2 - x1 + 1) * (y2 - y1 + 1)
        order = confidences.argsort()[::-1]

        keep = []
        while order.size > 0:
            i = order[0]
            keep.append(i)
            xx1 = np.maximum(x1[i], x1[order[1:]])
            yy1 = np.maximum(y1[i], y1[order[1:]])
            xx2 = np.minimum(x2[i], x2[order[1:]])
            yy2 = np.minimum(y2[i], y2[order[1:]])

            w = np.maximum(0, xx2 - xx1 + 1)
            h = np.maximum(0, yy2 - yy1 + 1)

            inter = w * h
            iou = inter / (areas[i] + areas[order[1:]] - inter)

            indices_to_keep = np.where(iou <= iou_threshold)[0]
            order = order[indices_to_keep + 1]


        final_boxes = boxes[keep]
        final_confidences = confidences[keep]
        return final_boxes, final_confidences
