import numpy as np
import cv2


def normalize_img(
    img: np.ndarray, height: int = 64, width: int = 295, to_gray: bool = False
) -> np.ndarray:

    if to_gray and img.shape[-1] == 3:
        img = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
    if not to_gray and len(img.shape) == 2:
        img = cv2.cvtColor(img, cv2.COLOR_GRAY2RGB)
    img = cv2.resize(img, (width, height))
    img = cv2.normalize(
        img, None, alpha=0, beta=1, norm_type=cv2.NORM_MINMAX, dtype=cv2.CV_32F
    )

    if to_gray:
        img = np.reshape(img, [*img.shape, 1])
    return img
