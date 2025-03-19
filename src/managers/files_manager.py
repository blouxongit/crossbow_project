from copy import deepcopy
from pathlib import Path
from typing import List, Tuple, Union

import cv2 as cv
import numpy as np

from configuration_reader import Config
from constants import ALLOWED_IMAGE_FORMATS
from data_types.data_types import Pair, TimedPathPair
from src.constants import CameraIdentifier


class FilesManager:
    def __init__(self):
        self._directory_images_left_camera: Path = None
        self._directory_images_right_camera: Path = None
        self._delta_time_per_image: float = None
        self._image_sampling_rate = 1
        self._list_timed_matching_image_path_pair: List[TimedPathPair] = []

        self._persistent_storage_list_timed_matching_image_path_pair = []

    def update_from_config(self, config: Config):
        self._set_directory_images_left_camera(config.left_camera_config.directory_path)
        self._set_directory_images_right_camera(config.right_camera_config.directory_path)
        delta_time_per_image = 1 / config.left_camera_config.framerate
        self._set_delta_time_per_image(delta_time_per_image)
        if self.is_valid():
            self._create_persistent_list_timed_matching_image_path_pair()
        self._list_timed_matching_image_path_pair = deepcopy(
            self._persistent_storage_list_timed_matching_image_path_pair
        )

    def set_image_sampling_rate(self, new_image_sampling_rate: int):
        assert (
            isinstance(new_image_sampling_rate, int) and new_image_sampling_rate > 0
        ), "The sampling rate must be greater than 1. "
        self._list_timed_matching_image_path_pair = self._persistent_storage_list_timed_matching_image_path_pair[
            ::new_image_sampling_rate
        ]

    def get_list_timed_matching_image_path_pair(self):
        return self._list_timed_matching_image_path_pair

    def _set_delta_time_per_image(self, new_delta_time_per_image):
        self._delta_time_per_image = new_delta_time_per_image

    def _set_directory_images_left_camera(self, directory: Union[str, Path]):
        if isinstance(directory, str):
            directory = Path(directory)
        self._directory_images_left_camera = directory

    def _set_directory_images_right_camera(self, directory: Union[str, Path]):
        if isinstance(directory, str):
            directory = Path(directory)
        self._directory_images_right_camera = directory

    def _get_images_paths_from_camera(self, camera_identifier: CameraIdentifier) -> List[str]:
        images_paths = []
        if camera_identifier == CameraIdentifier.LEFT_CAMERA:
            for extension in ALLOWED_IMAGE_FORMATS:
                images_paths += list(self._directory_images_left_camera.glob(f"*{extension}"))
        else:
            for extension in ALLOWED_IMAGE_FORMATS:
                images_paths += list(self._directory_images_right_camera.glob(f"*{extension}"))
        return [str(image_path) for image_path in images_paths]

    def _create_persistent_list_timed_matching_image_path_pair(self, starting_point=None) -> None:
        if starting_point:
            # TODO : we should do something in case we want to process images after a certain point
            pass

        list_images_paths_left_camera, list_images_paths_right_camera = self._get_pair_lists_of_sorted_images_path()
        maximum_number_of_pairs = min(len(list_images_paths_left_camera), len(list_images_paths_right_camera))
        timestamp = 0
        for idx in range(maximum_number_of_pairs):
            left_image_path = list_images_paths_left_camera[idx]
            right_image_path = list_images_paths_right_camera[idx]

            timed_matching_path_pair = TimedPathPair(timestamp, left_image_path, right_image_path)
            self._persistent_storage_list_timed_matching_image_path_pair.append(timed_matching_path_pair)

            timestamp += self._delta_time_per_image

    def _get_pair_lists_of_sorted_images_path(self) -> Tuple:
        list_images_paths_left_camera = self._get_images_paths_from_camera(CameraIdentifier.LEFT_CAMERA)
        list_images_paths_right_camera = self._get_images_paths_from_camera(CameraIdentifier.RIGHT_CAMERA)

        list_images_paths_left_camera.sort()
        list_images_paths_right_camera.sort()

        return list_images_paths_left_camera, list_images_paths_right_camera

    def is_valid(self):
        if (
            self._directory_images_left_camera is None
            or self._directory_images_right_camera is None
            or self._delta_time_per_image is None
        ):
            return False
        return self._directory_images_left_camera.is_dir() and self._directory_images_right_camera.is_dir()


def read_image(image_path: Union[str, Path], in_grayscale: bool = False) -> np.ndarray:
    return cv.imread(image_path, cv.IMREAD_GRAYSCALE if in_grayscale else cv.IMREAD_COLOR)
