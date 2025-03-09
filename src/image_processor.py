from enum import Enum
from typing import List

import cv2 as cv
import numpy as np

from camera import HighSpeedCamera
from projectile_finder import ProjectileFinders
from src.camera import CameraSetup
from src.projectile_finder import AvailableProjectileFindersMethod


class ColorDomain(Enum):
    GRAYSCALE = 0
    RGB = 1


class ImageProcessor:
    def __init__(self):
        self.image: np.ndarray = None
        self.associated_camera: HighSpeedCamera = None
        self.projectile_finder_function: callable = None
        self.is_grayscale: bool = None
        self.find_projectile_in_color_domain: ColorDomain = None

    def set_image(self, new_image: np.ndarray):
        self.image = new_image
        self.is_grayscale = len(new_image.shape) == 2

    def get_image(self):
        return self.image

    def set_associated_camera(self, new_camera: HighSpeedCamera):
        self.associated_camera = new_camera

    def set_projectile_finder_function(self, projectile_finder_function: AvailableProjectileFindersMethod):
        self.projectile_finder_function = ProjectileFinders().get_projectile_finder_function(projectile_finder_function)

    def find_projectile(self, *args, **kwargs):
        if self.find_projectile_in_color_domain == ColorDomain.RGB:
            projectiles = self.projectile_finder_function(self.image, *args, **kwargs)
        else:
            projectiles = self.projectile_finder_function(self.image_to_grayscale(), *args, **kwargs)

        return projectiles

    def image_to_grayscale(self) -> np.ndarray:
        return self.image if self.is_grayscale else cv.cvtColor(self.image, cv.COLOR_BGR2GRAY)


class ImagesPairProcessor:
    def __init__(self):
        self.camera_setup: CameraSetup = None
        self._left_image_processor: ImageProcessor = None
        self._right_image_processor: ImageProcessor = None
        self.projectile_finder_method: AvailableProjectileFindersMethod = None
        self.find_projectile_in_color_domain: ColorDomain = None

    def set_camera_setup(self, new_camera_setup: CameraSetup):
        self.camera_setup = new_camera_setup
        self._left_image_processor.set_associated_camera(self.camera_setup.left_camera)
        self._right_image_processor.set_associated_camera(self.camera_setup.right_camera)

    def set_left_camera_image(self, image: np.ndarray):
        self._left_image_processor.set_image(image)

    def set_right_camera_image(self, image: np.ndarray):
        self._right_image_processor.set_image(image)

    def set_camera_pair_images(self, left_image, right_image):
        self.set_left_camera_image(left_image)
        self.set_right_camera_image(right_image)

    def set_find_projectile_in_color_domain(self, new_color_domain: ColorDomain):
        self.find_projectile_in_color_domain = new_color_domain

    def get_camera_setup(self):
        return self.camera_setup

    def set_left_image_processor(self, new_left_image_processor: ImageProcessor):
        self._left_image_processor = new_left_image_processor

    def set_right_image_processor(self, new_right_image_processor: ImageProcessor):
        self._right_image_processor = new_right_image_processor

    def set_projectile_finder_method(self, new_projectile_finder_method: AvailableProjectileFindersMethod):
        self._left_image_processor.set_projectile_finder_function(new_projectile_finder_method)
        self._right_image_processor.set_projectile_finder_function(new_projectile_finder_method)

    def find_projectiles_in_images(self, *args, **kwargs) -> List[np.ndarray, np.ndarray]:
        projectiles_in_left_image = self._left_image_processor.find_projectile(*args, **kwargs)
        projectiles_in_right_image = self._right_image_processor.find_projectile(*args, **kwargs)

        return [projectiles_in_left_image, projectiles_in_right_image]
