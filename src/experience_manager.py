from enum import Enum
from pathlib import Path
from typing import List, Union

import cv2
import numpy as np
from matplotlib import pyplot as plt

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


    def compute_speed_vector(self):
        gradient = (
            np.array(self.projectile_trajectory[1:]) - np.array(self.projectile_trajectory[:-1])
        ) / self.camera_setup.left_camera.framerate
        return gradient

    def compute_accelerations_vector(self):
        speed = self.compute_speed_vector()
        gradient = (speed[1:] - speed[:-1]) / self.camera_setup.left_camera.framerate
        return gradient

    class VectorType(Enum):
        SPEED = 0
        ACCELERATION = 1

    def plot_speed_vector(self):
        position_x = [pos[0] for pos in self.projectile_trajectory[:, -1]]
        position_y = [pos[1] for pos in self.projectile_trajectory[:, -1]]
        position_z = [pos[2] for pos in self.projectile_trajectory[:, -1]]

        speed_vector = self.compute_speed_vector()
        speed_u = [speed[0] for speed in speed_vector]
        speed_v = [speed[1] for speed in speed_vector]
        speed_w = [speed[2] for speed in speed_vector]

        fig = plt.figure()
        ax = fig.add_subplot(111, projection="3d")
        ax.scatter(position_x, position_y, position_z, label="Trajectory", color="b", s=30)
        ax.quiver(position_x, position_y, position_z, speed_u, speed_v, speed_w, color="r", length=0.1)
        ax.set_xlabel("X")
        ax.set_ylabel("Y")
        ax.set_zlabel("Z")
        ax.set_title("Speed over time")
        ax.legend()
        plt.show()

    def plot_vector_magnitude(self, vector_type: VectorType):
        fig = plt.figure()
        ax = fig.add_subplot(111)

        if vector_type == self.VectorType.SPEED:
            vector = self.compute_speed_vector()
            title = "Speed magnitude over time"
        if vector_type == self.VectorType.ACCELERATION:
            vector = self.compute_accelerations_vector()
            title = "Acceleration magnitude over time"

        vector_magnitude = [np.sqrt(data * data.transpose()) for data in np.array(vector)]
        time_series = [i * self.camera_setup.left_camera.framerate for i in range(len(vector_magnitude))]

        plt.plot(time_series, vector_magnitude)
        plt.title(title)
        ax.set_xlabel("Speed (m/s)")
        ax.set_xlabel("Time (s)")
        ax.legend()
        plt.show()

    def save_trajetory(self, file_name: str = "results.csv"):
        if not Path(file_name).suffix == ".csv":
            file_name += ".csv"
        np.savetxt(file_name, self.projectile_trajectory, delimiter=",")


def can_be_reconstructed(pair_coords_2d: List[np.ndarray, np.ndarray]) -> bool:
    left_2d_coords = pair_coords_2d[0]
    right_2d_coords = pair_coords_2d[1]

    VALID_SHAPES = [(2, 1), (2,)]

    if left_2d_coords.shape not in VALID_SHAPES or right_2d_coords.shape not in VALID_SHAPES:
        return False
    return True



def can_be_reconstructed(pair_coords_2d: List[np.ndarray, np.ndarray]) -> bool:
    left_2d_coords = pair_coords_2d[0]
    right_2d_coords = pair_coords_2d[1]

    valid_shapes = [(2, 1), (2,)]

    if left_2d_coords.shape not in valid_shapes or right_2d_coords.shape not in valid_shapes:
        return False
    return True


