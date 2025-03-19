from pathlib import Path
from typing import Union

import cv2 as cv
import numpy as np


def read_image(image_path: Union[str, Path], in_grayscale: bool = False) -> np.ndarray:
    return cv.imread(image_path, cv.IMREAD_GRAYSCALE if in_grayscale else cv.IMREAD_COLOR)
