from pathlib import Path
from typing import List, Union

import cv2 as cv
import numpy as np

from configuration_reader import Config
from constants import ALLOWED_IMAGE_FORMATS
from src.constants import CameraIdentifier
from src.data_types import TimedPathPair


class FilesManager:
    def __init__(self):
        self._directory_images_left_camera: Path = None
        self._directory_images_right_camera: Path = None

        self.list_timed_matching_image_path_pair: List[TimedPathPair] = []

    def update_from_config(self, config: Config):
        self.set_directory_images_left_camera(config.left_camera_config.directory_path)
        self.set_directory_images_right_camera(config.right_camera_config.directory_path)
        if self.is_valid():
            self.create_list_timed_matching_image_path_pair()

    def set_directory_images_left_camera(self, directory: Union[str, Path]):
        if isinstance(directory, str):
            directory = Path(directory)
        self._directory_images_left_camera = directory

    def set_directory_images_right_camera(self, directory: Union[str, Path]):
        if isinstance(directory, str):
            directory = Path(directory)
        self._directory_images_right_camera = directory

    def get_images_name_from_camera(self, camera_identifier: CameraIdentifier):
        images_paths = []
        if camera_identifier == CameraIdentifier.LEFT_CAMERA:
            for extension in ALLOWED_IMAGE_FORMATS:
                images_paths += list(self._directory_images_left_camera.glob(f"*{extension}"))
        else:
            for extension in ALLOWED_IMAGE_FORMATS:
                images_paths += list(self._directory_images_right_camera.glob(f"*{extension}"))
        return [str(image_path) for image_path in images_paths]

    def create_list_timed_matching_image_path_pair(self, starting_point=None):

        if starting_point:
            # TODO : we should do something in case we want to process images after a certain point
            pass

        list_images_left_camera_path = self.get_images_name_from_camera(CameraIdentifier.LEFT_CAMERA)
        list_images_right_camera_path = self.get_images_name_from_camera(CameraIdentifier.RIGHT_CAMERA)

        list_images_left_camera_path.sort()
        list_images_right_camera_path.sort()

        maximum_number_of_pairs = min(len(list_images_left_camera_path), len(list_images_right_camera_path))
        timestamp = 0
        for i in range(maximum_number_of_pairs):
            image_left_camera_path = list_images_left_camera_path[i]
            closest_image_right_camera_path = find_closest_image_path(
                image_left_camera_path, list_images_right_camera_path, i
            )

            # TODO: add a way to know the timestamp (either the camera fps, or the image name)
            timestamp += 1

            timed_matching_pair = TimedPathPair(timestamp, image_left_camera_path, closest_image_right_camera_path)
            self.list_timed_matching_image_path_pair.append(timed_matching_pair)

    def is_valid(self):
        if self._directory_images_left_camera is None or self._directory_images_right_camera is None:
            return False
        return self._directory_images_left_camera.is_dir() and self._directory_images_right_camera.is_dir()


def find_closest_image_path(current_image_name: str, list_image_to_compare, current_image_idx=None) -> str:
    # TODO: find how to return the closest image to the timestamp.
    return list_image_to_compare[current_image_idx]


def read_image(image_path: Union[str, Path], in_grayscale: bool = False) -> np.ndarray:
    return cv.imread(image_path, cv.IMREAD_GRAYSCALE if in_grayscale else cv.IMREAD_COLOR)
