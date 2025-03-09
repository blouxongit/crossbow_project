ALLOWED_IMAGE_FORMATS = [".jpg", ".png", ".jpeg", ".tif"]

VALID_JSON_SCHEMA = {
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
                "rotation": {
                    "type": "array",
                    "items": {"type": "array", "items": {"type": "number"}, "minItems": 3, "maxItems": 3},
                    "minItems": 3,
                    "maxItems": 3,
                },
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
                "rotation",
                "imagesFolderPath",
                "framerate",
            ],
        }
    },
}
