from pathlib import Path
from typing import List, Union

import cv2 as cv
import numpy as np

from configuration_reader import Config
from constants import ALLOWED_IMAGE_FORMATS
from src.camera import CameraIdentifier


class FilesManager:
    def __init__(self):
        self.directory_images_left_camera: Path = None
        self.directory_images_right_camera: Path = None
        self.matching_images = None  # An array of pairs of images corresponding to left and right images

    def update_from_config(self, config: Config):
        self.set_directory_images_left_camera(config.left_camera.directory_path)
        self.set_directory_images_right_camera(config.right_camera.directory_path)
        if self.is_valid():
            self.matching_images = self.get_matching_images_path()

    def set_directory_images_left_camera(self, directory: Union[str, Path]):
        if isinstance(directory, str):
            directory = Path(directory)
        self.directory_images_left_camera = directory

    def set_directory_images_right_camera(self, directory: Union[str, Path]):
        if isinstance(directory, str):
            directory = Path(directory)
        self.directory_images_right_camera = directory

    def get_images_name_from_camera(self, camera_identifier: CameraIdentifier):
        images_paths = []
        if camera_identifier == CameraIdentifier.LEFT_CAMERA:
            for extension in ALLOWED_IMAGE_FORMATS:
                images_paths += list(self.directory_images_left_camera.glob(extension))
        else:
            for extension in ALLOWED_IMAGE_FORMATS:
                images_paths += list(self.directory_images_right_camera.glob(extension))
        return images_paths

    def get_matching_images_path(self, starting_point=None) -> List[List[Path, Path]]:
        matched_images = []

        if starting_point:
            # TODO
            # We should do something in case we want to process images after a certain point
            pass

        images_left_camera = self.get_images_name_from_camera(CameraIdentifier.LEFT_CAMERA)
        images_right_camera = self.get_images_name_from_camera(CameraIdentifier.RIGHT_CAMERA)

        # TODO: do we want to implement a specific sorting method ?
        images_left_camera.sort()
        images_right_camera.sort()

        maximum_usable_images = min(len(images_left_camera), len(images_right_camera))
        for i in range(maximum_usable_images):
            image_left_camera = images_left_camera[i]
            closest_image_right_camera = find_closest_image_by_timestamp(
                image_left_camera.identifier, images_right_camera, i
            )

            matched_images[i] = [image_left_camera, closest_image_right_camera]

        return matched_images

    def is_valid(self):
        if self.directory_images_left_camera is None or self.directory_images_right_camera is None:
            return False
        return self.directory_images_left_camera.is_dir() and self.directory_images_right_camera.is_dir()


def find_closest_image_by_timestamp(current_image_name: str, list_image_to_compare, current_image_idx=None) -> Path:
    # TODO: find how to return the closest image to the timestamp
    return list_image_to_compare[0]


def read_image(image_path: Union[str, Path], in_grayscale: bool = False) -> np.ndarray:
    return cv.imread(image_path, cv.IMREAD_GRAYSCALE if in_grayscale else cv.IMREAD_COLOR)
