import numpy as np

from utils.utils import read_image


class Point2D:
    def __init__(self, x=np.nan, y=np.nan):
        self.x = x
        self.y = y

    def set_x(self, x):
        self.x = x

    def set_y(self, y):
        self.y = y

    def get_point(self):
        return np.array([self.x, self.y])

    def __eq__(self, other):
        if not isinstance(other, Point2D):
            return False
        return np.allclose(self.get_point(), other.get_point(), equal_nan=True)

    def is_default(self):
        return np.isnan(self.x) and np.isnan(self.y)

    def is_valid(self):
        return not (np.isnan(self.x) or np.isnan(self.y))


class Point3D(Point2D):
    def __init__(self, x=np.nan, y=np.nan, z=np.nan):
        super().__init__(x, y)
        self.z = z

    def __eq__(self, other):
        if not isinstance(other, Point3D):
            return False
        return np.allclose(self.get_point(), other.get_point(), equal_nan=True)

    def set_z(self, z):
        self.z = z

    def get_point(self):
        return np.array([self.x, self.y, self.z])

    def is_default(self):
        return np.isnan(self.z) and super().is_default()

    def is_valid(self):
        return (not np.isnan(self.z)) and super().is_valid()


class Pair:
    def __init__(self, left, right):
        self.left = left
        self.right = right

    def as_list(self):
        return [self.left, self.right]

    def as_array(self):
        return np.array([self.left, self.right])


class ImagePair(Pair):
    def __init__(self, left_image: np.ndarray, right_image: np.ndarray):
        super().__init__(left_image, right_image)


class Point2DPair(Pair):
    def __init__(self, left_point: Point2D, right_point: Point2D):
        super().__init__(left_point, right_point)


class TimedData:
    def __init__(self, timestamp=None, data=None):
        self.timestamp = timestamp
        self.data = data

    def set_timestamp(self, new_timestamp):
        self.timestamp = new_timestamp

    def set_data(self, new_data):
        self.data = new_data

    def get(self):
        return self.timestamp, self.data

    def get_timestamp(self):
        return self.timestamp

    def get_data(self):
        return self.data


class TimedPoint2D(TimedData):
    def __init__(self, timestamp=None, point2d: Point2D = Point2D()):
        super().__init__(timestamp, point2d)

    def set_point2d(self, new_point_2d: Point2D):
        super().set_data(new_point_2d)

    def get_point(self):
        return self.data.get_point()

    def get(self):
        return self.timestamp, self.data.get_point()


class TimedPoint3D(TimedData):
    def __init__(self, timestamp=None, point3d: Point3D = Point3D()):
        super().__init__(timestamp, point3d)

    def set_point3d(self, new_point_3d: Point3D):
        super().set_data(new_point_3d)

    def get_point(self):
        return self.data.get_point()

    def get(self):
        return self.timestamp, self.data.get_point()


class TimedPathPair(TimedData):
    def __init__(self, timestamp, left_path: str, right_path: str):
        path_pair = Pair(left_path, right_path)
        super().__init__(timestamp, path_pair)


class TimedImage(TimedData):
    def __init__(self, timestamp, image: np.ndarray):
        super().__init__(timestamp, image)


class TimedImagePair(TimedData):
    def __init__(self, timestamp, left_image: np.ndarray, right_image: np.ndarray):
        images_pair = ImagePair(left_image, right_image)
        super().__init__(timestamp, images_pair)

    @classmethod
    def from_timed_path_pair(cls, timed_path_pair: TimedPathPair):
        timestamp, path_pair = timed_path_pair.get()
        left_image = read_image(path_pair.left)
        right_image = read_image(path_pair.right)
        return cls(timestamp, left_image, right_image)


class TimedPoint2DPair(TimedData):
    def __init__(self, timestamp, left_point2d: Point2D, right_point2d: Point2D):
        points2d_pair = Pair(left_point2d, right_point2d)
        super().__init__(timestamp, points2d_pair)
