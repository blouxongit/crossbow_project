from typing import List

import cv2 as cv
import numpy as np

from camera import HighSpeedCamera
from constants import AvailableProjectileFinderMethods
from data_types import ImagePair, Pair, Point2D, Point2DPair
from projectile_finder import ProjectileFinders
from src.camera import CameraSetup
from src.constants import ColorDomain


class ImageProcessor:
    def __init__(self):
        self.image: np.ndarray = None
        self.associated_camera: HighSpeedCamera = None
        self.projectile_finder_function: callable = None
        self.is_grayscale: bool = None
        self.color_domain_to_find_projectile: ColorDomain = None

    def set_image(self, new_image: np.ndarray):
        self.image = new_image
        self.is_grayscale = len(new_image.shape) == 2

    def get_image(self):
        return self.image

    def set_associated_camera(self, new_camera: HighSpeedCamera):
        self.associated_camera = new_camera

    def set_projectile_finder_function(self, projectile_finder_function: AvailableProjectileFinderMethods):
        self.projectile_finder_function = ProjectileFinders().get_projectile_finder_function(projectile_finder_function)

    def find_projectile(self, *args, **kwargs) -> Point2D:
        if self.color_domain_to_find_projectile == ColorDomain.RGB:
            projectile = self.projectile_finder_function(self.image, *args, **kwargs)
        else:
            projectile = self.projectile_finder_function(self.image_to_grayscale(), *args, **kwargs)

        return projectile

    def image_to_grayscale(self) -> np.ndarray:
        return self.image if self.is_grayscale else cv.cvtColor(self.image, cv.COLOR_BGR2GRAY)


class ImagePairProcessor:
    def __init__(self):
        self.camera_setup: CameraSetup = None
        self._pair_image_processor = Pair(ImageProcessor(), ImageProcessor())
        self.projectile_finder_method: AvailableProjectileFinderMethods = None

    def set_camera_setup(self, new_camera_setup: CameraSetup):
        self.camera_setup = new_camera_setup
        self._pair_image_processor.left.set_associated_camera(self.camera_setup.left_camera)
        self._pair_image_processor.right.set_associated_camera(self.camera_setup.right_camera)

    def set_left_camera_image(self, image: np.ndarray):
        self._pair_image_processor.left.set_image(image)

    def set_right_camera_image(self, image: np.ndarray):
        self._pair_image_processor.right.set_image(image)

    def set_image_pair_to_camera_pair(self, image_pair: ImagePair):
        self.set_left_camera_image(image_pair.left)
        self.set_right_camera_image(image_pair.right)

    def set_color_domain_to_find_projectile(self, new_color_domain: ColorDomain):
        self._pair_image_processor.left.color_domain_to_find_projectile = new_color_domain
        self._pair_image_processor.right.color_domain_to_find_projectile = new_color_domain

    def get_camera_setup(self):
        return self.camera_setup

    def set_left_image_processor(self, new_left_image_processor: ImageProcessor):
        self._pair_image_processor.left = new_left_image_processor

    def set_right_image_processor(self, new_right_image_processor: ImageProcessor):
        self._pair_image_processor.right = new_right_image_processor

    def set_projectile_finder_method(self, new_projectile_finder_method: AvailableProjectileFinderMethods):
        self._pair_image_processor.left.set_projectile_finder_function(new_projectile_finder_method)
        self._pair_image_processor.right.set_projectile_finder_function(new_projectile_finder_method)

    def find_projectile_in_images(self, *args, **kwargs) -> Point2DPair:
        projectile_in_left_image = self._pair_image_processor.left.find_projectile(*args, **kwargs)
        projectile_in_right_image = self._pair_image_processor.right.find_projectile(*args, **kwargs)

        return Point2DPair(projectile_in_left_image, projectile_in_right_image)
