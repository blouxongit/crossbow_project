from enum import Enum


# This is the enumeration to be modified in case you want to add your own method.
class AvailableProjectileFinderMethods(Enum):
    FIND_CIRCLES = 1
    DUMMY_METHOD_EXAMPLE = 99


class CameraIdentifier(Enum):
    LEFT_CAMERA = 0
    RIGHT_CAMERA = 1
    UNDEFINED = 2


class ColorDomain(Enum):
    GRAYSCALE = 0
    RGB = 1


ALLOWED_IMAGE_FORMATS = [".jpg", ".png", ".jpeg", ".tif"]


VALID_CONFIGURATION_JSON_SCHEMA = {
    "type": "object",
    "properties": {"leftCamera": {"$ref": "#/definitions/camera"}, "rightCamera": {"$ref": "#/definitions/camera"}},
    "required": ["leftCamera", "rightCamera"],
    "definitions": {
        "camera": {
            "type": "object",
            "properties": {
                "focalX": {"type": "number"},
                "focalY": {"type": "number"},
                "skew": {"type": "number"},
                "principalPointX": {"type": "number"},
                "principalPointY": {"type": "number"},
                "position": {"type": "array", "items": {"type": "number"}, "minItems": 3, "maxItems": 3},
                "yaw": {"type": "number"},
                "pitch": {"type": "number"},
                "roll": {"type": "number"},
                "imagesFolderPath": {"type": "string"},
                "framerate": {"type": "number"},
            },
            "required": [
                "focalX",
                "focalY",
                "skew",
                "principalPointX",
                "principalPointY",
                "position",
                "yaw",
                "pitch",
                "roll",
                "imagesFolderPath",
                "framerate",
            ],
        }
    },
}
