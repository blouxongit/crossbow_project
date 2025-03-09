from enum import Enum

import numpy as np

from configuration_reader import Config


class CameraIdentifier(Enum):
    LEFT_CAMERA = 0
    RIGHT_CAMERA = 1
    UNDEFINED = 2


class HighSpeedCamera:
    def __init__(self, intrinsic_matrix: np.ndarray = None, extrinsic_matrix: np.ndarray = None):
        self.intrinsic_matrix = intrinsic_matrix
        self.extrinsic_matrix = extrinsic_matrix
        self.framerate = None
        self.identifier = CameraIdentifier.UNDEFINED

    def set_intrinsic_matrix(self, new_intrinsic_matrix):
        assert new_intrinsic_matrix.shape == (
            3,
            3,
        ), f"Incorrect size: expected (3,3), got {new_intrinsic_matrix.shape}."
        self.intrinsic_matrix = new_intrinsic_matrix

    def set_extrinsic_matrix(self, new_extrinsic_matrix):
        assert new_extrinsic_matrix.shape == (
            3,
            4,
        ), f"Incorrect size: expected (3,4), got {new_extrinsic_matrix.shape}."
        self.extrinsic_matrix = new_extrinsic_matrix

    def set_framerate(self, new_framerate):
        self.framerate = new_framerate

    def set_identifier(self, new_identifier: CameraIdentifier):
        self.identifier = new_identifier

    def get_projection_matrix(self):
        return self.intrinsic_matrix @ self.extrinsic_matrix

    def get_camera_position_in_world_coordinates(self):
        return self.extrinsic_matrix[:, -1]


class CameraSetup:
    """
    Currently, this class is designed to control two high speed cameras.
    If we were to add another (that would be useful to this code), this class should be modified in consequence.
    """

    def __init__(self):
        self.left_camera: HighSpeedCamera = None
        self.right_camera: HighSpeedCamera = None

    def update_from_config(self, config: Config):
        self.left_camera = HighSpeedCamera(
            intrinsic_matrix=config.left_camera.intrinsic_matrix, extrinsic_matrix=config.left_camera.extrinsic_matrix
        )
        self.right_camera = HighSpeedCamera(
            intrinsic_matrix=config.right_camera.intrinsic_matrix, extrinsic_matrix=config.right_camera.extrinsic_matrix
        )

        self.left_camera.set_framerate(config.left_camera.framerate)
        self.right_camera.set_framerate(config.right_camera.framerate)

        self.left_camera.set_identifier(CameraIdentifier.LEFT_CAMERA)
        self.right_camera.set_identifier(CameraIdentifier.RIGHT_CAMERA)
