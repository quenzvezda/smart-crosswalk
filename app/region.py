import cv2
from shapely import Point
from shapely.geometry import Polygon
from collections import defaultdict

# Global variable for tracking history and regions
track_history = defaultdict(list)
counting_regions = [
    {
        "name": "YOLOv8 Rectangle Region",
        "polygon": Polygon([(176, 36), (416, 36), (416, 336), (176, 336)]),
        "counts": 0,
        "dragging": False,
        "region_color": (37, 255, 225),
        "text_color": (0, 0, 255),
    },
]

def mouse_callback(event, x, y, flags, param):
    global current_region

    # Mouse left button down event
    if event == cv2.EVENT_LBUTTONDOWN:
        for region in counting_regions:
            if region["polygon"].contains(Point((x, y))):
                current_region = region
                current_region["dragging"] = True
                current_region["offset_x"] = x - region["polygon"].centroid.x
                current_region["offset_y"] = y - region["polygon"].centroid.y

    # Mouse move event
    elif event == cv2.EVENT_MOUSEMOVE:
        if current_region is not None and current_region["dragging"]:
            new_centroid_x = x - current_region["offset_x"]
            new_centroid_y = y - current_region["offset_y"]
            dx = new_centroid_x - current_region["polygon"].centroid.x
            dy = new_centroid_y - current_region["polygon"].centroid.y
            current_region["polygon"] = Polygon(
                [(p[0] + dx, p[1] + dy) for p in current_region["polygon"].exterior.coords]
            )

    # Mouse left button up event
    elif event == cv2.EVENT_LBUTTONUP:
        if current_region is not None and current_region["dragging"]:
            current_region["dragging"] = False
