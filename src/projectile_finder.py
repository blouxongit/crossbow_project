from enum import Enum
from typing import List

import cv2 as cv

from data_types import Point2D

# If you wish to add another function to find the projectiles you need to :
# 1- Add another enumeration type below
# 2- Add the function to the mapping dictionary in the ProjectileFinders class


class AvailableProjectileFindersMethod(Enum):
    FIND_CIRCLES = 1


class ProjectileFinders:
    def __init__(self):
        # This is the function mapping to be updated if you wish to add another projectile finder function
        self._finder_function_mapping = {
            AvailableProjectileFindersMethod.FIND_CIRCLES: find_circles_in_image_coordinates
        }

    def get_projectile_finder_function(self, finder_function: AvailableProjectileFindersMethod):
        assert (
            finder_function in self._finder_function_mapping.keys()
        ), "The function you are looking for seems to be not implemented yet."
        return self._finder_function_mapping[finder_function]


def find_circles_in_image_coordinates(img_grayscale, min_radius=None, max_radius=None) -> List[Point2D]:
    blurred_image = cv.GaussianBlur(img_grayscale, (9, 9), 2)

    circles = cv.HoughCircles(
        image=blurred_image,
        method=cv.HOUGH_GRADIENT,
        dp=1.25,
        minDist=100,
        minRadius=min_radius or 10,
        maxRadius=max_radius or 50,
    )

    circles_center_coordinates = [Point2D(circle[0], circle[1]) for circle in circles[0, :]]
    return circles_center_coordinates
