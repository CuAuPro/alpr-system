import itertools
import numpy as np
from numpy import mean
from PIL import Image, ImageDraw
from typing import List

import collections

try:
    collections_abc = collections.abc
except AttributeError:
    collections_abc = collections


class StrLabelConverter(object):
    """Convert between str and label.
        Insert `blank` to the alphabet for CTC.
    Args:
        letters (str): set of the possible characters.
        ignore_case (bool, default=True): whether or not to ignore all of the case.
    """

    def __init__(self, letters: str,
                 max_text_len: int,
                 ignore_case: bool = True):
        self._ignore_case = ignore_case
        if self._ignore_case:
            letters = letters.lower()
        self.letters = letters
        self.letters_max = len(self.letters) + 1
        self.max_text_len = max_text_len

    def labels_to_text(self, labels: List) -> str:
        out_best = [k for k, g in itertools.groupby(labels)]
        outstr = ''
        for c in out_best:
            if c != 0:
                outstr += self.letters[c - 1]
        return outstr



def decode_prediction(logits: np.ndarray, label_converter: StrLabelConverter) -> str:
    # Compute softmax along the last axis
    softmax_logits = np.exp(logits - np.max(logits, axis=-1, keepdims=True))
    softmax_logits /= np.sum(softmax_logits, axis=-1, keepdims=True)
    
    # Get the most likely tokens
    tokens = np.argmax(softmax_logits, axis=-1)
    tokens = np.squeeze(tokens, axis=1)  # Remove single-dimensional entries

    # Convert tokens to text
    text = label_converter.labels_to_text(tokens)
    return text


def decode_batch(net_out_value: np.ndarray, label_converter: StrLabelConverter) -> list:
    texts = []
    batch_size = net_out_value.shape[0]  # First dimension is batch size
    
    for i in range(batch_size):
        logits = net_out_value[i]  # Extract logits for the current image in the batch
        pred_texts = decode_prediction(logits, label_converter)
        texts.append(pred_texts)
    texts = [text.upper() for text in texts]
    return texts


def is_valid_str(s: str, letters: List) -> bool:
    for ch in s:
        if ch not in letters:
            return False
    return True


def plot_loss(epoch: int,
              train_losses: list,
              val_losses: list,
              n_steps: int = 100):
    """
    Plots train and validation losses
    """
    import matplotlib.pyplot as plt

    # making titles
    train_title = f'Epoch:{epoch} | Train Loss:{mean(train_losses[-n_steps:]):.6f}'
    val_title = f'Epoch:{epoch} | Val Loss:{mean(val_losses[-n_steps:]):.6f}'

    fig, ax = plt.subplots(1, 2, figsize=(12, 6))
    ax[0].plot(train_losses)
    ax[1].plot(val_losses)

    ax[0].set_title(train_title)
    ax[1].set_title(val_title)

    plt.show()
