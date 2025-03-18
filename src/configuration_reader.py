import json
from pathlib import Path

import numpy as np
from jsonschema import ValidationError, validate
from scipy.spatial.transform import Rotation as Rot

from constants import VALID_CONFIGURATION_JSON_SCHEMA
from src.constants import CameraIdentifier


class Config:
    def __init__(self, config_path):
        self._config_as_map = None
        self._read_config_file(config_path)

        assert self.is_valid(), "The configuration file given is incorrect."

        class ConfigCamera:
            def __init__(
                self, intrinsic_matrix: np.ndarray, extrinsic_matrix: np.ndarray, framerate, directory_path: str
            ):
                self.intrinsic_matrix = intrinsic_matrix
                self.extrinsic_matrix = extrinsic_matrix
                self.framerate = framerate
                self.directory_path = directory_path

            def set_intrinsic_matrix(self, new_intrinsic_matrix: np.ndarray):
                self.intrinsic_matrix = new_intrinsic_matrix

            def set_extrinsic_matrix(self, new_extrinsic_matrix: np.ndarray):
                self.extrinsic_matrix = new_extrinsic_matrix

            def set_directory_path(self, new_directory_path: str):
                self.directory_path = new_directory_path

        self.left_camera_config = ConfigCamera(*self._extract_camera_config(CameraIdentifier.LEFT_CAMERA))
        self.right_camera_config = ConfigCamera(*self._extract_camera_config(CameraIdentifier.RIGHT_CAMERA))

    def _get_intrinsic_matrix_from_params(self, focal_x, focal_y, skew, principal_point_x, principal_point_y):
        return np.array([[focal_x, skew, principal_point_x], [0, focal_y, principal_point_y], [0, 0, 1]])

    def _get_extrinsic_matrix_from_params(self, rotation, translation: np.ndarray):
        translation = -np.reshape(translation, (3, 1))
        return np.hstack([rotation, translation])

    def _extract_camera_config(self, camera_identifier: CameraIdentifier):
        if camera_identifier == CameraIdentifier.LEFT_CAMERA:
            camera_key = "leftCamera"
        else:
            camera_key = "rightCamera"

        config_camera = self._config_as_map[camera_key]
        focal_x = config_camera["focalX"]
        focal_y = config_camera["focalY"]
        skew = config_camera["skew"]
        ppx = config_camera["principalPointX"]
        ppy = config_camera["principalPointY"]
        translation = np.array(config_camera["position"])
        alpha = config_camera["alpha"]
        beta = config_camera["beta"]
        gamma = config_camera["gamma"]
        framerate = config_camera["framerate"]
        images_folder_path = config_camera["imagesFolderPath"]

        rotation = Rot.from_euler("xyz", [alpha, beta, gamma], degrees=True).as_matrix()

        intrinsic_matrix = self._get_intrinsic_matrix_from_params(focal_x, focal_y, skew, ppx, ppy)
        extrinsinc_matrix = self._get_extrinsic_matrix_from_params(rotation, translation)

        return intrinsic_matrix, extrinsinc_matrix, framerate, images_folder_path

    def _read_config_file(self, config_path):
        file_path = Path(config_path)
        if file_path.exists() and file_path.is_file():
            with open(file_path, "r") as f:
                self._config_as_map = json.load(f)

    def is_valid(self):
        try:
            validate(self._config_as_map, VALID_CONFIGURATION_JSON_SCHEMA)
        except ValidationError:
            return False

        return True
