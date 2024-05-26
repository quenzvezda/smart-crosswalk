import cv2
import numpy as np
import time
from collections import defaultdict
from shapely.geometry import Point
from ultralytics import YOLO
from ultralytics.utils.plotting import Annotator, colors
from region import counting_regions, track_history


def detect_pedestrian(weights, device, region_side, pejalan_kaki_detected):
    model = YOLO(f"{weights}")
    model.to("cuda" if device == "0" else "cpu")

    source = 1 if region_side == "kiri" else 2
    videocapture = cv2.VideoCapture(source)
    if not videocapture.isOpened():
        raise ValueError(f"Unable to open video source {source}")

    try:
        start_time = None
        while videocapture.isOpened():
            success, frame = videocapture.read()
            if not success:
                break

            results = model.track(frame, persist=True)
            annotator = Annotator(frame, line_width=2)

            if results[0].boxes.id is not None:
                boxes = results[0].boxes.xyxy.cpu().numpy()
                track_ids = results[0].boxes.id.cpu().tolist()
                clss = results[0].boxes.cls.cpu().tolist()

                for box, track_id, cls in zip(boxes, track_ids, clss):
                    annotator.box_label(box, str(model.model.names[cls]), color=colors(cls, True))
                    bbox_center = ((box[0] + box[2]) / 2, (box[1] + box[3]) / 2)

                    track = track_history[track_id]
                    track.append(bbox_center)
                    if len(track) > 60:
                        track.pop(0)

                    if len(track) > 1:
                        points = np.array(track, dtype=np.int32)
                        cv2.polylines(frame, [points], isClosed=False, color=colors(cls, True), thickness=2)

                    for region in counting_regions:
                        if region["polygon"].contains(Point(bbox_center)):
                            region["counts"] += 1
                            if start_time is None:
                                start_time = time.time()
                            elif time.time() - start_time >= 5:
                                pejalan_kaki_detected[region_side] = True
                        else:
                            start_time = None

            for region in counting_regions:
                region_label = str(region["counts"])
                region_color = region["region_color"]
                region_text_color = region["text_color"]

                polygon_coords = np.array(region["polygon"].exterior.coords, dtype=np.int32)
                centroid_x, centroid_y = int(region["polygon"].centroid.x), int(region["polygon"].centroid.y)

                cv2.polylines(frame, [polygon_coords], isClosed=True, color=region_color, thickness=2)
                cv2.putText(frame, region_label, (centroid_x, centroid_y), cv2.FONT_HERSHEY_SIMPLEX, 0.7,
                            region_text_color, 2)

            cv2.imshow(f"YOLOv8 Region Counter - {region_side}", frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

            for region in counting_regions:
                region["counts"] = 0
    except KeyboardInterrupt:
        print("CTRL + C has been pressed")
    finally:
        videocapture.release()
        cv2.destroyAllWindows()


def detect_vehicle(weights, device, vehicle_detected):
    model = YOLO(f"{weights}")
    model.to("cuda" if device == "0" else "cpu")

    source = 0
    videocapture = cv2.VideoCapture(source)
    if not videocapture.isOpened():
        raise ValueError(f"Unable to open video source {source}")

    try:
        while videocapture.isOpened():
            success, frame = videocapture.read()
            if not success:
                break

            results = model.track(frame, persist=True)
            annotator = Annotator(frame, line_width=2)

            if results[0].boxes.id is not None:
                boxes = results[0].boxes.xyxy.cpu().numpy()
                track_ids = results[0].boxes.id.cpu().tolist()
                clss = results[0].boxes.cls.cpu().tolist()

                for box, track_id, cls in zip(boxes, track_ids, clss):
                    annotator.box_label(box, str(model.model.names[cls]), color=colors(cls, True))
                    bbox_center = ((box[0] + box[2]) / 2, (box[1] + box[3]) / 2)

                    track = track_history[track_id]
                    track.append(bbox_center)
                    if len(track) > 60:
                        track.pop(0)

                    if len(track) > 1:
                        points = np.array(track, dtype=np.int32)
                        cv2.polylines(frame, [points], isClosed=False, color=colors(cls, True), thickness=2)

                    vehicle_detected = True

            cv2.imshow("YOLOv8 Vehicle Detection", frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
    except KeyboardInterrupt:
        print("CTRL + C has been pressed")
    finally:
        videocapture.release()
        cv2.destroyAllWindows()
