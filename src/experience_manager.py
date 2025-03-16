from typing import List

import cv2
import numpy as np
import pandas as pd
from matplotlib import pyplot as plt

from camera import CameraSetup
from configuration_reader import Config
from constants import AvailableProjectileFinderMethods
from files_manager import FilesManager
from image_processor import ImagePairProcessor
from src.constants import ColorDomain
from src.data_types import ImagePair, Point2DPair, Point3D, TimedImagePair, TimedPoint2DPair, TimedPoint3D


class ExperienceManager:
    def __init__(self, configuration_file_path):
        self._configuration = Config(config_path=configuration_file_path)

        self._camera_setup = CameraSetup()
        self._camera_setup.update_from_config(config=self._configuration)

        self._image_pair_processor = ImagePairProcessor()
        self._image_pair_processor.set_camera_setup(self._camera_setup)

        # By default, we use opencv findCircles method, that find circles in grayscale images
        self._image_pair_processor.set_projectile_finder_method(AvailableProjectileFinderMethods.FIND_CIRCLES)
        self._image_pair_processor.set_color_domain_to_find_projectile(ColorDomain.GRAYSCALE)

        self._files_manager = FilesManager()
        self._files_manager.update_from_config(config=self._configuration)

        self._list_timed_pair_projectile_coordinates_2d: List[TimedPoint2DPair] = []

        # Ultimately, this is what we are looking for
        self._list_timed_projectile_coordinates_3d: List[TimedPoint3D] = []
        self._list_timed_projectile_speed_3d: List[TimedPoint3D] = []
        self._list_timed_projectile_acceleration_3d: List[TimedPoint3D] = []

    def set_projectile_finder_method(self, projectile_finder_method: AvailableProjectileFinderMethods):
        self._image_pair_processor.set_projectile_finder_method(projectile_finder_method)

    def set_color_domain_to_find_projectile(self, new_color_domain: ColorDomain):
        self._image_pair_processor.set_color_domain_to_find_projectile(new_color_domain)

    def _assign_images(self, matching_image_pair: ImagePair):
        self._image_pair_processor.set_image_pair_to_camera_pair(matching_image_pair)

    def _extract_projectile_2d_coordinates(self):
        for timed_matching_image_path_pair in self._files_manager.list_timed_matching_image_path_pair:
            timed_matching_image_pair = TimedImagePair.from_timed_path_pair(timed_matching_image_path_pair)
            self._assign_images(matching_image_pair=timed_matching_image_pair.get_data())

            projectile_found_in_pair_of_images = self._image_pair_processor.find_projectile_in_images()
            timed_projectile_found_in_pair_of_images = TimedPoint2DPair(
                timed_matching_image_pair.get_timestamp(),
                projectile_found_in_pair_of_images.left,
                projectile_found_in_pair_of_images.right,
            )

            self._list_timed_pair_projectile_coordinates_2d.append(timed_projectile_found_in_pair_of_images)

    def _compute_3d_coords_from_2d_coords_pair  (self, pair_coords_2d: Point2DPair) -> Point3D:
        if not _can_be_reconstructed(pair_coords_2d):
            return Point3D()

        reconstructed_point3d = cv2.triangulatePoints(
            projMatr1=self._camera_setup.left_camera.get_projection_matrix(),
            projMatr2=self._camera_setup.right_camera.get_projection_matrix(),
            projPoints1=pair_coords_2d.left.get_point(),
            projPoints2=pair_coords_2d.right.get_point(),
        )
        return Point3D(
            float(reconstructed_point3d[0]), float(reconstructed_point3d[1]), float(reconstructed_point3d[2])
        )

    def compute_trajectory(self):
        self._extract_projectile_2d_coordinates()

        for projectile_coords_pair_2d in self._list_timed_pair_projectile_coordinates_2d:
            projectile_3d_coords = self._compute_3d_coords_from_2d_coords_pair(projectile_coords_pair_2d.get_data())
            if projectile_3d_coords.is_valid():
                timed_point_3d = TimedPoint3D(projectile_coords_pair_2d.get_timestamp(), projectile_3d_coords)
                self._list_timed_projectile_coordinates_3d.append(timed_point_3d)

    def compute_speed(self):
        assert (
            self._list_timed_projectile_coordinates_3d
        ), "The projectile coordinates are not computed yet. You may use the compute_trajectory() function before calling compute_speed()"
        for idx in range(len(self._list_timed_projectile_coordinates_3d) - 1):
            current_timed_3d_point = self._list_timed_projectile_coordinates_3d[idx]
            next_timed_3d_point = self._list_timed_projectile_coordinates_3d[idx + 1]

            dt = next_timed_3d_point.timestamp - current_timed_3d_point.timestamp
            speed = (next_timed_3d_point.get_point() - current_timed_3d_point.get_point()) / dt

            timed_speed_point = TimedPoint3D(current_timed_3d_point.timestamp, Point3D(*np.squeeze(speed)))
            self._list_timed_projectile_speed_3d.append(timed_speed_point)

    def compute_acceleration(self):
        assert (
            self._list_timed_projectile_speed_3d
        ), "The speed coordinates are not computed yet. You may use the compute_speed() function before calling compute_acceleration()"
        for idx in range(len(self._list_timed_projectile_speed_3d) - 1):
            current_timed_3d_speed = self._list_timed_projectile_speed_3d[idx]
            next_timed_3d_speed = self._list_timed_projectile_speed_3d[idx + 1]

            dt = next_timed_3d_speed.timestamp - current_timed_3d_speed.timestamp
            acceleration = (next_timed_3d_speed.get_point() - current_timed_3d_speed.get_point()) / dt

            timed_acceleration_point = TimedPoint3D(
                current_timed_3d_speed.timestamp, Point3D(*np.squeeze(acceleration))
            )
            self._list_timed_projectile_acceleration_3d.append(timed_acceleration_point)

    def compute_kinematics(self):
        self.compute_trajectory()
        self.compute_speed()
        self.compute_acceleration()

    def plot_trajectory(self):
        list_3d_positions = np.vstack(
            [timed_point_3d.get_point() for timed_point_3d in self._list_timed_projectile_coordinates_3d]
        )
        x_position_vector = list_3d_positions[:, 0]
        y_position_vector = list_3d_positions[:, 1]
        z_position_vector = list_3d_positions[:, 2]

        fig = plt.figure()
        ax = fig.add_subplot(111, projection="3d")
        ax.scatter(x_position_vector, y_position_vector, z_position_vector, label="Trajectory", color="b", s=30)
        ax.set_xlabel("X")
        ax.set_ylabel("Y")
        ax.set_zlabel("Z")
        ax.set_title("Trajectory over time")
        ax.legend()
        plt.show()

    def plot_speed_vector(self):
        list_3d_positions = np.vstack(
            [timed_point_3d.get_point() for timed_point_3d in self._list_timed_projectile_coordinates_3d]
        )
        x_position_vector = list_3d_positions[:, 0]
        y_position_vector = list_3d_positions[:, 1]
        z_position_vector = list_3d_positions[:, 2]

        list_3d_speeds = np.vstack([timed_speed_3d.get_point() for timed_speed_3d in self._list_timed_projectile_speed_3d])
        x_speed_vector = list_3d_speeds[:, 0]
        y_speed_vector = list_3d_speeds[:, 1]
        z_speed_vector = list_3d_speeds[:, 2]

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
        ax.set_title("Speed vectors over time")
        ax.legend()
        plt.show()

    def plot_speed_magnitude(self):
        fig = plt.figure()
        ax = fig.add_subplot(111)

        time_vector = [timed_speed_3d.get_timestamp() for timed_speed_3d in self._list_timed_projectile_speed_3d]
        speeds_vectors = np.vstack([timed_speed_3d.get_point() for timed_speed_3d in self._list_timed_projectile_speed_3d])
        speed_magnitude = speed_magnitudes = np.linalg.norm(speeds_vectors, axis=1)

        plt.plot(time_vector, speed_magnitude)
        plt.title("Speed magnitude over time")
        ax.set_ylabel("Speed (m/s)")
        ax.set_xlabel("Time (s)")
        plt.show()

    def plot_acceleration_magnitude(self):
        fig = plt.figure()
        ax = fig.add_subplot(111)

        time_vector = [
            timed_acceleration_3d.get_timestamp() for timed_acceleration_3d in self._list_timed_projectile_acceleration_3d
        ]
        accelerations_vectors = np.vstack(
            [timed_acceleration_3d.get_point() for timed_acceleration_3d in self._list_timed_projectile_acceleration_3d]
        )
        acceleration_magnitude = np.linalg.norm(accelerations_vectors, axis=1)

        plt.plot(time_vector, acceleration_magnitude)
        plt.title("Acceleration magnitude over time")
        ax.set_ylabel("Acceleration (m/s^2)")
        ax.set_xlabel("Time (s)")
        plt.show()

    def save_results_as_csv(self, save_to: str = "results.csv"):
        assert (
            self._list_timed_projectile_coordinates_3d
            and self._list_timed_projectile_speed_3d
            and self._list_timed_projectile_acceleration_3d
        ), "The kinematics were not (or partially not) computed. You may run compute_kinematics before calling this function."

        time_vector = np.array(
            [timed_position_3d.get_timestamp() for timed_position_3d in self._list_timed_projectile_coordinates_3d]
        )

        positions_vectors = np.hstack(
            [
                timed_positions_3d.get_point().reshape((3, 1))
                for timed_positions_3d in self._list_timed_projectile_coordinates_3d
            ]
        )
        number_positions = positions_vectors.shape[1]

        speeds_vectors = np.hstack(
            [timed_speed_3d.get_point().reshape((3, 1)) for timed_speed_3d in self._list_timed_projectile_speed_3d]
        )
        number_speeds = speeds_vectors.shape[1]
        nan_speed_points = np.full(
            (3, number_positions - number_speeds), np.nan
        )  # In order to have the same size as the positions (the dimension is 1 less because of the discretized gradient)
        speeds_vectors = np.hstack([speeds_vectors, nan_speed_points])

        accelerations_vectors = np.hstack(
            [
                timed_acceleration_3d.get_point().reshape((3, 1))
                for timed_acceleration_3d in self._list_timed_projectile_acceleration_3d
            ]
        )
        number_accelerations = accelerations_vectors.shape[1]
        nan_acceleration_points = np.full(
            (3, number_positions - number_accelerations), np.nan
        )  # In order to have the same size as the positions (the dimension is 2 less because of the discretized gradients)
        accelerations_vectors = np.hstack([accelerations_vectors, nan_acceleration_points])

        data = {
            "time": time_vector,
            "x_position": positions_vectors[0, :],
            "y_position": positions_vectors[1, :],
            "z_position": positions_vectors[2, :],
            "x_speed": speeds_vectors[0, :],
            "y_speed": speeds_vectors[1, :],
            "z_speed": speeds_vectors[2, :],
            "x_acceleration": accelerations_vectors[0, :],
            "y_acceleration": accelerations_vectors[1, :],
            "z_acceleration": accelerations_vectors[2, :],
        }
        df = pd.DataFrame(data)
        file_name = save_to if save_to.endswith(".csv") else save_to + ".csv"

        df.to_csv(file_name, index=False, float_format="%.12f", na_rep="NaN")


def _can_be_reconstructed(pair_coords_2d: Point2DPair) -> bool:
    return pair_coords_2d.left.is_valid() and pair_coords_2d.right.is_valid()
