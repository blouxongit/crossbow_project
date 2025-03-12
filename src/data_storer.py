import numpy as np
from typing import Union, List


class DataArray:

    def __init__(self):
        self.array: List[DataFormat] = None

    def get_timestamp_array(self):
        return np.array([data_sample.timestamp for data_sample in self.array])

    def get_data_array(self):
        return np.hstack([data_sample.get_data() for data_sample in self.array])


class DataFormat:
    def __init__(self):
        self.data: Union[Point2D, Point3D, np.ndarray] = None
        self.timestamp: float = -1.0

    def set_timestamp(self, new_timestamp):
        self.timestamp = new_timestamp

    def set_data(self, new_data):
        self.data = new_data

    def get_data(self):

        if isinstance(self.data, np.ndarray):
            return self.data
        else:
            return self.data.get_point()


class Point2D:
    def __init__(self, x=None, y=None):
        self.x = x
        self.y = y

    def set_x(self, x):
        self.x = x

    def set_y(self, y):
        self.y = y

    def get_point(self):
        return np.array([self.x, self.y]).transpose()


class Point3D(Point2D):
    def __init__(self, x=None, y=None, z=None):
        super.__init__(x, y)
        self.z = z

    def set_z(self, z):
        self.z = z

    def get_point(self):
        return np.array([self.x, self.y, self.z]).transpose()
