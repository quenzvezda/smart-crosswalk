import numpy as np

def is_within_roi(box, roi):
    """
    Determine if the center of a box is within the specified ROI.
    Box and ROI should be (ymin, xmin, ymax, xmax) format.
    """
    box_center = ((box[2] + box[0]) / 2, (box[3] + box[1]) / 2)
    return roi[0] <= box_center[0] <= roi[2] and roi[1] <= box_center[1] <= roi[3]

def calculate_overlap(box, roi):
    """
    Calculate the percentage overlap of a box with the ROI.
    """
    dy = min(box[2], roi[2]) - max(box[0], roi[0])
    dx = min(box[3], roi[3]) - max(box[1], roi[1])
    if (dx >= 0) and (dy >= 0):
        area_overlap = dx * dy
        area_box = (box[2] - box[0]) * (box[3] - box[1])
        return area_overlap / area_box
    return 0
