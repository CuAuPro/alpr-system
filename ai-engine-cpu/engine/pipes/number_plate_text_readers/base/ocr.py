import numpy as np
from typing import List, Tuple, Any, Dict
from engine.tools.image_processing import normalize_img
from engine.tools.ocr_tools import StrLabelConverter, decode_batch
import onnxruntime as rt


class Ocr:
    def __init__(self) -> None:
        self.input_name = None
        self.output_names = None

        self.width = 200
        self.height = 50
        self.color_channels = 3

        self.letters = [
            "0",
            "1",
            "2",
            "3",
            "4",
            "5",
            "6",
            "7",
            "8",
            "9",
            "A",
            "B",
            "C",
            "D",
            "E",
            "F",
            "G",
            "H",
            "I",
            "J",
            "K",
            "L",
            "M",
            "N",
            "O",
            "P",
            "Q",
            "R",
            "S",
            "T",
            "U",
            "V",
            "W",
            "X",
            "Y",
            "Z",
        ]
        self.max_text_len = 9
        self.letters_max = len(self.letters) + 1
        self.label_length = 13

    def load_model(self, engine_file_path):
        self.engine = rt.InferenceSession(engine_file_path)
        self.input_name = self.engine.get_inputs()[0].name
        # Get the output names
        self.output_names = [s.name for s in self.engine.get_outputs()]
        return self.engine

    def init_label_converter(self):
        self.label_converter = StrLabelConverter(
            "".join(self.letters), self.max_text_len
        )

    def preprocess(self, imgs, need_preprocess=True):
        xs = []
        if need_preprocess:
            for img in imgs:
                x = normalize_img(img, width=self.width, height=self.height)
                xs.append(x)
            xs = np.moveaxis(np.array(xs), 3, 1)
        else:
            xs = np.array(imgs)
        return xs

    def predict(self, xs: np.ndarray, return_acc: bool = False) -> Any:

        out = self.engine.run(self.output_names, {self.input_name: xs})
        pred_texts = decode_batch(np.array(out), self.label_converter)
        pred_texts = [pred_text.upper() for pred_text in pred_texts]
        if return_acc:
            if len(out):
                out = np.array(out)
                out = out.reshape((out.shape[1], out.shape[0], out.shape[2]))
            return pred_texts, out
        return pred_texts
