def calculate_overlap(box, roi):
    """
    Calculate the percentage overlap of a box with the ROI.
    Both box and ROI should be in pixel coordinates.
    Box and ROI are in (ymin, xmin, ymax, xmax) format.
    """
    dy = min(box[2], roi[2]) - max(box[0], roi[0])
    dx = min(box[3], roi[3]) - max(box[1], roi[1])
    if (dx >= 0) and (dy >= 0):
        area_overlap = dx * dy
        area_box = (box[2] - box[0]) * (box[3] - box[1])
        return area_overlap / area_box
    return 0
