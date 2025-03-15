from pathlib import Path
from typing import List, Tuple, Union

import cv2 as cv
import numpy as np

from configuration_reader import Config
from constants import ALLOWED_IMAGE_FORMATS
from src.constants import CameraIdentifier
from src.data_types import TimedImagePair


class FilesManager:
    def __init__(self):
        self._directory_images_left_camera: Path = None
        self._directory_images_right_camera: Path = None

        self.list_timed_matching_image_pair: List[TimedImagePair] = None

    def update_from_config(self, config: Config):
        self.set_directory_images_left_camera(config.left_camera_config.directory_path)
        self.set_directory_images_right_camera(config.right_camera_config.directory_path)
        if self.is_valid():
            self.list_timed_matching_image_pair = self.get_list_timed_matching_image_pair()

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
                images_paths += list(self._directory_images_left_camera.glob(extension))
        else:
            for extension in ALLOWED_IMAGE_FORMATS:
                images_paths += list(self._directory_images_right_camera.glob(extension))
        return [str(image_path) for image_path in images_paths]

    def get_list_timed_matching_image_pair(self, starting_point=None) -> List[TimedImagePair]:
        list_timed_images_pair = []

        if starting_point:
            # TODO
            # We should do something in case we want to process images after a certain point
            pass

        list_images_left_camera_path = self.get_images_name_from_camera(CameraIdentifier.LEFT_CAMERA)
        list_images_right_camera_path = self.get_images_name_from_camera(CameraIdentifier.RIGHT_CAMERA)

        list_images_left_camera_path.sort()
        list_images_right_camera_path.sort()

        maximum_number_of_pairs = min(len(list_images_left_camera_path), len(list_images_right_camera_path))
        for i in range(maximum_number_of_pairs):
            image_left_camera_path = list_images_left_camera_path[i]
            closest_image_right_camera_path = find_closest_image_path_by_timestamp(
                image_left_camera_path, list_images_right_camera_path, i
            )
            # TODO: add a way to know the timestamp (dependant on how is stored the image)
            associated_timestamp = 0

            matching_pair = TimedImagePair(
                associated_timestamp, read_image(image_left_camera_path), read_image(closest_image_right_camera_path)
            )
            list_timed_images_pair.append(matching_pair)

        return list_timed_images_pair

    def is_valid(self):
        if self._directory_images_left_camera is None or self._directory_images_right_camera is None:
            return False
        return self._directory_images_left_camera.is_dir() and self._directory_images_right_camera.is_dir()


def find_closest_image_path_by_timestamp(current_image_name: str, list_image_to_compare, current_image_idx=None) -> str:
    # TODO: find how to return the closest image to the timestamp.
    return list_image_to_compare[0]


def read_image(image_path: Union[str, Path], in_grayscale: bool = False) -> np.ndarray:
    return cv.imread(image_path, cv.IMREAD_GRAYSCALE if in_grayscale else cv.IMREAD_COLOR)
