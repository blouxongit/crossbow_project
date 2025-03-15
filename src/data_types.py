import numpy as np


class Point2D:
    def __init__(self, x=None, y=None):
        self.x = x
        self.y = y

    def __eq__(self, other):
        return self.get_point() == other.get_point()

    def set_x(self, x):
        self.x = x

    def set_y(self, y):
        self.y = y

    def get_point(self):
        return np.array([self.x, self.y]).transpose()


class Point3D(Point2D):
    def __init__(self, x=None, y=None, z=None):
        super().__init__(x, y)
        self.z = z

    def __eq__(self, other):
        return self.get_point() == other.get_point()

    def set_z(self, z):
        self.z = z

    def get_point(self):
        return np.array([self.x, self.y, self.z]).transpose()

    def is_default(self):
        return self == Point3D()


class Pair:
    def __init__(self, left, right):
        self.left = left
        self.right = right

    def as_list(self):
        return [self.left, self.right]

    def as_array(self):
        return np.array([self.left, self.right])


class ImagePair:
    def __init__(self, left_image: np.ndarray, right_image: np.ndarray):
        self.left_image = left_image
        self.right_image = right_image

    def get_pair(self):
        return Pair(self.left_image, self.right_image)


class Point2DPair:
    def __init__(self, left_point: Point2D, right_point: Point2D):
        self.pair = Pair(left_point, right_point)


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


class TimedImage(TimedData):
    def __init__(self, timestamp, image: np.ndarray):
        super().__init__(timestamp, image)


class TimedImagePair(TimedData):
    def __init__(self, timestamp, left_image: np.ndarray, right_image: np.ndarray):
        images_pair = Pair(left_image, right_image)
        super.__init__(timestamp, images_pair)


class TimedPoint2DPair(TimedData):
    def __init__(self, timestamp, left_point2d: Point2D, right_point2d: Point2D):
        points2d_pair = Pair(left_point2d, right_point2d)
        super().__init__(timestamp, points2d_pair)
