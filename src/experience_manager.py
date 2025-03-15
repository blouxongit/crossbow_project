from typing import List

import cv2
import numpy as np
from matplotlib import pyplot as plt

from camera import CameraSetup
from configuration_reader import Config
from files_manager import FilesManager
from image_processor import ImagesPairProcessor
from post_detecting_functions import noop
from projectile_finder import AvailableProjectileFindersMethod
from src.constants import ColorDomain
from src.data_types import ImagePair, Point2DPair, Point3D, TimedPoint2DPair, TimedPoint3D


class ExperienceManager:
    def __init__(self, configuration_file_path):
        self.configuration = Config(config_path=configuration_file_path)

        self.camera_setup = CameraSetup()
        self.camera_setup.update_from_config(config=self.configuration)

        self.images_pair_processor = ImagesPairProcessor()
        self.images_pair_processor.set_camera_setup(self.camera_setup)

        # By default, we use opencv findCircles method, that find circles in grayscale images
        self.images_pair_processor.set_projectile_finder_method(AvailableProjectileFindersMethod.FIND_CIRCLES)
        self.images_pair_processor.set_color_domain_to_find_projectile(ColorDomain.GRAYSCALE)

        self.files_manager = FilesManager()
        self.files_manager.update_from_config(config=self.configuration)

        self.timed_pair_projectile_coordinates_2d: List[TimedPoint2DPair] = []

        # Ultimately, this is what we are looking for
        self.timed_projectile_coordinates_3d: List[TimedPoint3D] = []
        self.timed_projectile_speed_3d: List[TimedPoint3D] = []
        self.timed_projectile_acceleration_3d: List[TimedPoint3D] = []

    def set_projectile_finder_method(self, projectile_finder_method: AvailableProjectileFindersMethod):
        self.images_pair_processor.set_projectile_finder_method(projectile_finder_method)

    def set_color_domain_to_find_projectile(self, new_color_domain: ColorDomain):
        self.images_pair_processor.set_color_domain_to_find_projectile(new_color_domain)

    def assign_images(self, matching_image_pair: ImagePair):
        self.images_pair_processor.set_camera_pair_images(matching_image_pair)

    def extract_projectiles_2d_coordinates(self, post_detecting_function: callable = noop):
        list_non_postprocessed_pair_2d_coordinates = []

        list_timed_matching_image_pair = self.files_manager.get_list_timed_matching_image_pair()
        for timed_matching_image_pair in list_timed_matching_image_pair:
            self.assign_images(matching_image_pair=timed_matching_image_pair.get_data())

            projectiles_found_in_pair_of_images = self.images_pair_processor.find_projectiles_in_images()
            list_non_postprocessed_pair_2d_coordinates.append(projectiles_found_in_pair_of_images)

        list_pair_2d_coordinates = post_detecting_function(list_non_postprocessed_pair_2d_coordinates)
        self.timed_pair_projectile_coordinates_2d = list_pair_2d_coordinates

    def compute_3d_coords_from_2d_coords_pair(self, pair_coords_2d: Point2DPair) -> Point3D:
        if not can_be_reconstructed(pair_coords_2d):
            return Point3D()

        reconstructed_point3d = cv2.triangulatePoints(
            projMatr1=self.camera_setup.left_camera.get_projection_matrix(),
            projMatr2=self.camera_setup.right_camera.get_projection_matrix(),
            projPoints1=pair_coords_2d.pair.left.get_point(),
            projPoints2=pair_coords_2d.pair.right.get_point(),
        )
        return Point3D(*reconstructed_point3d)

    def compute_trajectory(self):
        for projectile_coords_pair_2d in self.timed_pair_projectile_coordinates_2d:
            projectile_3d_coords = self.compute_3d_coords_from_2d_coords_pair(projectile_coords_pair_2d.get_data())
            if not projectile_3d_coords.is_default():
                timed_point_3d = TimedPoint3D(projectile_coords_pair_2d.get_timestamp(), projectile_3d_coords)
                self.timed_projectile_coordinates_3d.append(timed_point_3d)

    def plot_speed_vector(self):
        list_3d_positions = np.hstack(
            [timed_point_3d.get_point() for timed_point_3d in self.timed_projectile_coordinates_3d]
        )
        x_position_vector = list_3d_positions[0, :]
        y_position_vector = list_3d_positions[1, :]
        z_position_vector = list_3d_positions[2, :]

        list_3d_speeds = np.hstack([timed_speed_3d.get_point() for timed_speed_3d in self.timed_projectile_speed_3d])
        x_speed_vector = list_3d_speeds[0, :]
        y_speed_vector = list_3d_speeds[1, :]
        z_speed_vector = list_3d_speeds[2, :]

        fig = plt.figure()
        ax = fig.add_subplot(111, projection="3d")
        ax.scatter(x_position_vector, y_position_vector, z_position_vector, label="Trajectory", color="b", s=30)
        ax.quiver(
            x_position_vector[:-1],
            y_position_vector[:-1],
            z_position_vector[:-1],
            x_speed_vector,
            y_speed_vector,
            z_speed_vector,
            color="r",
            length=0.1,
        )
        ax.set_xlabel("X")
        ax.set_ylabel("Y")
        ax.set_zlabel("Z")
        ax.set_title("Speed over time")
        ax.legend()
        plt.show()

    def compute_speed_vector(self):
        for idx in range(len(self.timed_projectile_coordinates_3d) - 1):
            current_timed_3d_point = self.timed_projectile_coordinates_3d[idx]
            next_timed_3d_point = self.timed_projectile_coordinates_3d[idx + 1]

            dt = next_timed_3d_point.timestamp - current_timed_3d_point.timestamp
            speed = (next_timed_3d_point.get_point() - current_timed_3d_point.get_point()) / dt

            speed_point = TimedPoint3D(current_timed_3d_point.timestamp, speed)
            self.timed_projectile_speed_3d.append(speed_point)

    def compute_accelerations_vector(self):
        for idx in range(len(self.timed_projectile_speed_3d) - 1):
            current_timed_3d_speed = self.timed_projectile_speed_3d[idx]
            next_timed_3d_speed = self.timed_projectile_speed_3d[idx + 1]

            dt = next_timed_3d_speed.timestamp - current_timed_3d_speed.timestamp
            acceleration = (next_timed_3d_speed.get_point() - current_timed_3d_speed.get_point()) / dt

            acceleration_point = TimedPoint3D(current_timed_3d_speed.timestamp, acceleration)
            self.timed_projectile_acceleration_3d.append(acceleration_point)

    def plot_speed_magnitude(self):
        fig = plt.figure()
        ax = fig.add_subplot(111)

        time_vector = [timed_speed_3d.get_timestamp() for timed_speed_3d in self.timed_projectile_speed_3d]
        speed_vector = np.hstack([timed_speed_3d.get_point() for timed_speed_3d in self.timed_projectile_speed_3d])
        speed_magnitude = np.sqrt(speed_vector.transpose() * speed_vector)

        plt.plot(time_vector, speed_magnitude)
        plt.title("Speed magnitude over time")
        ax.set_xlabel("Speed (m/s)")
        ax.set_xlabel("Time (s)")
        ax.legend()
        plt.show()

    def plot_acceleration_magnitude(self):
        fig = plt.figure()
        ax = fig.add_subplot(111)

        time_vector = [
            timed_acceleration_3d.get_timestamp() for timed_acceleration_3d in self.timed_projectile_acceleration_3d
        ]
        acceleration_vector = np.hstack(
            [timed_acceleration_3d.get_point() for timed_acceleration_3d in self.timed_projectile_acceleration_3d]
        )
        acceleration_magnitude = np.sqrt(acceleration_vector.transpose() * acceleration_vector)

        plt.plot(time_vector, acceleration_magnitude)
        plt.title("Acceleration magnitude over time")
        ax.set_xlabel("Speed (m/s)")
        ax.set_xlabel("Time (s)")
        ax.legend()
        plt.show()

    def save_results_as_csv(self, save_to: str = "results.csv"):
        time_vector = np.array(
            [timed_position_3d.get_timestamp() for timed_position_3d in self.timed_projectile_coordinates_3d]
        )

        positions_vectors = np.hstack(
            [timed_positions_3d.get_point() for timed_positions_3d in self.timed_projectile_coordinates_3d]
        )
        number_positions = positions_vectors.shape[1]

        speeds_vectors = np.hstack([timed_speed_3d.get_point() for timed_speed_3d in self.timed_projectile_speed_3d])
        number_speeds = speeds_vectors.shape[1]
        nan_speed_points = np.full(
            (3, number_positions - number_speeds), np.nan
        )  # In order to have the same size as the positions (the dimension is 1 less because of the discretized gradient)
        speeds_vectors = np.hstack([speeds_vectors, nan_speed_points])

        accelerations_vectors = np.hstack(
            [timed_acceleration_3d.get_point() for timed_acceleration_3d in self.timed_projectile_acceleration_3d]
        )
        number_accelerations = accelerations_vectors.shape[1]
        nan_acceleration_points = np.full(
            (3, number_positions - number_accelerations), np.nan
        )  # In order to have the same size as the positions (the dimension is 2 less because of the discretized gradients)
        accelerations_vectors = np.hstack([accelerations_vectors, nan_acceleration_points])

        data = np.column_stack(
            (
                time_vector,
                positions_vectors[0, :],
                positions_vectors[1, :],
                positions_vectors[2, :],
                speeds_vectors[0, :],
                speeds_vectors[1, :],
                speeds_vectors[2, :],
                accelerations_vectors[0, :],
                accelerations_vectors[1, :],
                accelerations_vectors[2, :],
            )
        )

        file_name = save_to if save_to.endswith(".csv") else save_to + ".csv"
        np.savetxt(
            file_name,
            data,
            delimiter=",",
            header="time,x_position,y_position,z_position,x_speed,y_speed,z_speed,x_acceleration,y_acceleration,z_acceleration",
            comments="",
        )


def can_be_reconstructed(pair_coords_2d: Point2DPair) -> bool:
    VALID_SHAPES = [(2, 1), (2,)]
    if (
        pair_coords_2d.pair.left.get_point().shape not in VALID_SHAPES
        or pair_coords_2d.pair.right.get_point().shape not in VALID_SHAPES
    ):
        return False
    return True
