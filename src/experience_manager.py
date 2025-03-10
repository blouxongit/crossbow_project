from pathlib import Path
from typing import List, Union

import cv2
import numpy as np

from camera import CameraSetup
from configuration_reader import Config
from files_manager import FilesManager, read_image
from image_processor import ColorDomain, ImagesPairProcessor
from post_detecting_functions import noop
from projectile_finder import AvailableProjectileFindersMethod


class ExperienceManager:
    def __init__(self, configuration_file_path):
        self.configuration = Config(config_path=configuration_file_path)

        self.camera_setup = CameraSetup()
        self.camera_setup.update_from_config(config=self.configuration)

        self.images_pair_processor = ImagesPairProcessor()
        self.images_pair_processor.set_camera_setup(self.camera_setup)

        # By default, we use opencv findCircles method, that find circles in grayscale images
        self.images_pair_processor.set_projectile_finder_method(AvailableProjectileFindersMethod.FIND_CIRCLES)
        self.images_pair_processor.set_find_projectile_in_color_domain(ColorDomain.GRAYSCALE)

        self.files_manager = FilesManager()
        self.files_manager.update_from_config(config=self.configuration)

        self.projectiles_coordinates_2d = []
        # The value at index i contains a list of 2 elements:
        # - At index 0: The np.ndarray of the 2d coordinates in the left image
        # - At index 1: The np.ndarray of the 2d coordinates in the right image

        self.projectile_trajectory = []
        # A list of the size of projectiles_coordinates_2d.
        # The value at index i corresponds to the 3d coordinates of the projectile point (using both 2d coordinates of the cameras) for the i_th picture taken by both cameras

    def set_projectile_finder_method(self, projectile_finder_method: AvailableProjectileFindersMethod):
        self.images_pair_processor.set_projectile_finder_method(projectile_finder_method)

    def set_find_projectile_in_color_domain(self, new_color_domain: ColorDomain):
        self.images_pair_processor.set_find_projectile_in_color_domain(new_color_domain)

    def assign_images(self, matching_images_pair: List[Union[str, Path], Union[str, Path]]):
        left_image = read_image(matching_images_pair[0])
        right_image = read_image(matching_images_pair[1])

        self.images_pair_processor.set_camera_pair_images(left_image, right_image)

    def extract_projectiles_2d_coordinates(self, post_detecting_function: callable = noop):
        images_sequence = self.files_manager.get_matching_images_path()
        for matching_images_pair_path in images_sequence:
            self.assign_images(matching_images_pair=matching_images_pair_path)

            projectiles_found_in_pair_of_images = self.images_pair_processor.find_projectiles_in_images()
            self.projectiles_coordinates_2d.append(projectiles_found_in_pair_of_images)

        self.projectiles_coordinates_2d = post_detecting_function(self.projectiles_coordinates_2d)

    def compute_3d_coords_from_2d_coords_pair(self, pair_coords_2d: List[np.ndarray, np.ndarray]) -> np.ndarray:
        if not can_be_reconstructed(pair_coords_2d):
            return []

        return cv2.triangulatePoints(
            projMatr1=self.camera_setup.left_camera.get_projection_matrix(),
            projMatr2=self.camera_setup.right_camera.get_projection_matrix(),
            projPoints1=pair_coords_2d[0],
            projPoints2=pair_coords_2d[1],
        )

    def compute_trajectory(self):
        for projectile_coords_pair_2d in self.projectiles_coordinates_2d:
            projectile_3d_coords = self.compute_3d_coords_from_2d_coords_pair(projectile_coords_pair_2d)
            self.projectile_trajectory.append(projectile_3d_coords)


def can_be_reconstructed(pair_coords_2d: List[np.ndarray, np.ndarray]) -> bool:
    left_2d_coords = pair_coords_2d[0]
    right_2d_coords = pair_coords_2d[1]

    valid_shapes = [(2, 1), (2,)]

    if left_2d_coords.shape not in valid_shapes or right_2d_coords.shape not in valid_shapes:
        return False
    return True
