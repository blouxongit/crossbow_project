def noop(pair_projectiles_coordinates_2d):
    return pair_projectiles_coordinates_2d


def circle_detector_post_processing(projectiles_coordinates_2d):
    left_detections = [detections[0] for detections in projectiles_coordinates_2d]
    right_detections = [detections[1] for detections in projectiles_coordinates_2d]

    left_cleaned_detections = circle_detector_post_processing_per_camera(left_detections)
    right_cleaned_detections = circle_detector_post_processing_per_camera(right_detections)

    cleaned_projectiles_coordinates_2d = [
        [left_cleaned_detection, right_cleaned_detection]
        for left_cleaned_detection, right_cleaned_detection in zip(left_cleaned_detections, right_cleaned_detections)
    ]

    return cleaned_projectiles_coordinates_2d


def circle_detector_post_processing_per_camera(detections):
    suspects = []
    invalid_detections = []

    for detection in detections:
        if len(detection) > 1:
            suspects.extend(detection)

    for suspect in suspects:
        if (
            suspects.count(suspect) > 2
        ):  # In theory, we could put 1, but we give a margin for error. We consider that if we get more than 2 times the exact same detection point, then it is not an actual detection point.
            invalid_detections.append(suspect)

    for invalid_detection in invalid_detections:
        for detection in detections:
            if invalid_detection in detection:
                detection.remove(invalid_detection)

    cleaned_detections = []
    for detection in detections:
        cleaned_detections.append(detection if len(detection) == 1 else [])

    return cleaned_detections
