import argparse
import cv2
from pathlib import Path
import numpy as np
from shapely.geometry import Polygon
from shapely.geometry.point import Point
from collections import defaultdict
from ultralytics import YOLO
from ultralytics.utils.plotting import Annotator, colors

# Global variable for tracking history and regions
track_history = defaultdict(list)
counting_regions = [
    {
        "name": "YOLOv8 Rectangle Region",
        "polygon": Polygon([(200, 250), (440, 250), (440, 550), (200, 550)]),
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

def run(
    weights="yolov8n.pt",
    source="0",
    device="cpu",
    view_img=True,
    classes=None,
    line_thickness=2,
    track_thickness=2,
    region_thickness=2,
):
    if source.isdigit():
        source = int(source)

    videocapture = cv2.VideoCapture(source)
    if not videocapture.isOpened():
        raise ValueError("Unable to open video source")

    model = YOLO(f"{weights}")
    model.to("cuda" if device == "0" else "cpu")

    while videocapture.isOpened():
        success, frame = videocapture.read()
        if not success:
            break

        results = model.track(frame, persist=True, classes=classes)
        annotator = Annotator(frame, line_width=line_thickness)

        if results[0].boxes.id is not None:
            boxes = results[0].boxes.xyxy.cpu().numpy()
            track_ids = results[0].boxes.id.cpu().tolist()
            clss = results[0].boxes.cls.cpu().tolist()

            for box, track_id, cls in zip(boxes, track_ids, clss):
                annotator.box_label(box, str(model.model.names[cls]), color=colors(cls, True))
                bbox_center = ((box[0] + box[2]) / 2, (box[1] + box[3]) / 2)

                track = track_history[track_id]
                track.append(bbox_center)
                if len(track) > 30:
                    track.pop(0)

                # Menggambar jalur tracking
                if len(track) > 1:  # Pastikan ada lebih dari satu titik untuk membentuk garis
                    points = np.array(track, dtype=np.int32)
                    cv2.polylines(frame, [points], isClosed=False, color=colors(cls, True), thickness=track_thickness)

                # Count objects within regions
                for region in counting_regions:
                    if region["polygon"].contains(Point(bbox_center)):
                        region["counts"] += 1

        # Draw regions and update frame annotations
        for region in counting_regions:
            region_label = str(region["counts"])
            region_color = region["region_color"]
            region_text_color = region["text_color"]

            polygon_coords = np.array(region["polygon"].exterior.coords, dtype=np.int32)
            centroid_x, centroid_y = int(region["polygon"].centroid.x), int(region["polygon"].centroid.y)

            cv2.polylines(frame, [polygon_coords], isClosed=True, color=region_color, thickness=region_thickness)
            cv2.putText(frame, region_label, (centroid_x, centroid_y), cv2.FONT_HERSHEY_SIMPLEX, 0.7, region_text_color, line_thickness)

        if view_img:
            cv2.imshow("YOLOv8 Region Counter", frame)
            cv2.setMouseCallback("YOLOv8 Region Counter", mouse_callback)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        # Reset counts after displaying
        for region in counting_regions:
            region["counts"] = 0

    videocapture.release()
    cv2.destroyAllWindows()

def parse_opt():
    parser = argparse.ArgumentParser()
    parser.add_argument("--weights", type=str, default="yolov8n.pt", help="initial weights path")
    parser.add_argument("--device", default="0", help="cuda device, i.e. 0 or cpu")
    parser.add_argument("--source", type=str, default="0", help="video file path or webcam index")
    parser.add_argument("--view-img", action="store_true", help="show results")
    parser.add_argument("--classes", nargs="+", type=int, help="filter by class")
    parser.add_argument("--line-thickness", type=int, default=2, help="bounding box thickness")
    parser.add_argument("--track-thickness", type=int, default=2, help="Tracking line thickness")
    parser.add_argument("--region-thickness", type=int, default=4, help="Region thickness")
    return parser.parse_args()

def main(opt):
    run(**vars(opt))

if __name__ == "__main__":
    opt = parse_opt()
    main(opt)
