from copy import copy
from enum import Enum

import cv2 as cv
import numpy as np

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


def find_circles_in_image_coordinates(img_grayscale, min_radius=None, max_radius=None):
    circles = cv.HoughCircles(
        image=img_grayscale,
        method=cv.HOUGH_GRADIENT,
        dp=1,
        minDist=100,
        param1=100,
        param2=0.9,
        minRadius=min_radius or 5,
        maxRadius=max_radius or 50,
    )

    circles_center_coordinates = [[circle[0], circle[1]] for circle in circles]
    return circles_center_coordinates


def show_detected_circles(img_grayscale):
    circles = find_circles_in_image_coordinates(img_grayscale)
    if circles is None:
        return

    circles = np.uint16(np.around(circles))
    img_grayscale_copy = copy(img_grayscale)

    def draw_central_point(circle_center):
        cv.circle(img_grayscale_copy, circle_center, 1, (0, 100, 100), 3)

    def draw_circle_outline(circle_center, circle_radius):
        cv.circle(img_grayscale_copy, circle_center, circle_radius, (255, 0, 255), 3)

    for circle in circles[0, :]:
        center = (circle[0], circle[1])
        radius = circle[2]
        draw_central_point(center)
        draw_circle_outline(center, radius)

    cv.imshow("Detected circles", img_grayscale_copy)
