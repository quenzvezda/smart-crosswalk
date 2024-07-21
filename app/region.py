from shapely.geometry import Point, Polygon
from collections import defaultdict
import cv2

# Global variable for tracking history and regions
track_history_kiri = defaultdict(list)
track_history_kanan = defaultdict(list)

counting_regions_kiri = [
    {
        "name": "YOLOv8 Rectangle Region Kiri",
        "polygon": Polygon([(121, 45), (445, 45), (445, 345), (121, 345)]),
        "counts": 0,
        "dragging": False,
        "region_color": (37, 255, 225),
        "text_color": (0, 0, 255),
    },
]

counting_regions_kanan = [
    {
        "name": "YOLOv8 Rectangle Region Kanan",
        # A B C D [Kiri Atas - Kanan Atas - Kanan Bawah - Kiri Bawah]
        # X Y, X Y, X Y, X Y
        "polygon": Polygon([(72, 48), (443, 48), (443, 346), (72, 346)]),
        "counts": 0,
        "dragging": False,
        "region_color": (37, 255, 225),
        "text_color": (0, 0, 255),
    },
]

current_region = None

def mouse_callback(event, x, y, flags, param):
    global current_region
    counting_regions = param

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
