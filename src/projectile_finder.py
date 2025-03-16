import cv2 as cv

from constants import AvailableProjectileFinderMethods
from data_types import Point2D

# If you wish to add another function to find the projectiles you need to :
# 1- Add another enumeration type in the constants file
# 2- Add the function to the mapping dictionary in the ProjectileFinders class (see below)


class ProjectileFinders:
    def __init__(self):
        # This is the function mapping to be updated if you wish to add another projectile finder function
        self._finder_function_mapping = {
            AvailableProjectileFinderMethods.FIND_CIRCLES: find_circles_in_image_coordinates,
            AvailableProjectileFinderMethods.DUMMY_METHOD_EXAMPLE: dummy_example,
        }

    def get_projectile_finder_function(self, finder_function: AvailableProjectileFinderMethods):
        assert (
            finder_function in self._finder_function_mapping
        ), "The function you are looking for seems to be not implemented yet."
        return self._finder_function_mapping[finder_function]


def find_circles_in_image_coordinates(img_grayscale, min_radius=None, max_radius=None) -> Point2D:
    blurred_image = cv.GaussianBlur(img_grayscale, (9, 9), 2)

    circles = cv.HoughCircles(
        image=blurred_image,
        method=cv.HOUGH_GRADIENT,
        dp=1.25,
        minDist=100,
        minRadius=min_radius or 10,
        maxRadius=max_radius or 50,
        param1=100,
        param2=50,
    )

    if circles is None:
        return Point2D()

    # We are making a big assumption here. The opencv function returns a list of detected circles.
    # This list is ranked from "most perfect circle" to "worst circle".
    # Therefore, we consider that our target is always the 1st circle detected.
    # Anyway, the experience setup should not allow for any other circle in the image.
    return Point2D(circles[0, 0, 0], circles[0, 0, 1])


# Note: The sole purpose of this function is to serve as an exemple to help if someone wants to add its own.
#       It can be deleted if you wish to.
def dummy_example(img_grayscale):
    return Point2D(0, 0)
