import cv2
import numpy as np
import time
from collections import defaultdict
from shapely.geometry import Point
from ultralytics import YOLO
from ultralytics.utils.plotting import Annotator, colors
from region import counting_regions, track_history
import logging
from datetime import datetime, timedelta
from contextlib import contextmanager

logger = logging.getLogger('detector')

# Global variable for region entry times
region_entry_times = defaultdict(lambda: defaultdict(datetime))

@contextmanager
def suppress_logging(level=logging.WARNING):
    logger = logging.getLogger("ultralytics")
    previous_level = logger.getEffectiveLevel()
    logger.setLevel(level)
    try:
        yield
    finally:
        logger.setLevel(previous_level)

def detect_pedestrian(weights, device, region_side, pejalan_kaki_detected, log_message):
    model = YOLO(f"{weights}")
    model.to("cuda" if device == "0" else "cpu")

    source = 1 if region_side == "kiri" else 2
    videocapture = cv2.VideoCapture(source)
    if not videocapture.isOpened():
        raise ValueError(f"Unable to open video source {source}")

    try:
        while videocapture.isOpened():
            success, frame = videocapture.read()
            if not success:
                break

            with suppress_logging(logging.WARNING):
                results = model.track(frame, persist=True)

            annotator = Annotator(frame, line_width=2)
            current_time = datetime.now()

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
                            if track_id not in region_entry_times[region["name"]]:
                                region_entry_times[region["name"]][track_id] = current_time
                            else:
                                time_in_region = current_time - region_entry_times[region["name"]][track_id]
                                if time_in_region >= timedelta(seconds=5):
                                    message = f"Pejalan kaki {track_id} terdeteksi di {region['name']} selama 5 detik."
                                    logger.info(message)
                                    log_message(message)
                        else:
                            if track_id in region_entry_times[region["name"]]:
                                del region_entry_times[region["name"]][track_id]

            for region in counting_regions:
                region_label = str(region["counts"])
                region_color = region["region_color"]
                region_text_color = region["text_color"]

                polygon_coords = np.array(region["polygon"].exterior.coords, dtype=np.int32)
                centroid_x, centroid_y = int(region["polygon"].centroid.x), int(region["polygon"].centroid.y)

                cv2.polylines(frame, [polygon_coords], isClosed=True, color=region_color, thickness=2)
                cv2.putText(frame, region_label, (centroid_x, centroid_y), cv2.FONT_HERSHEY_SIMPLEX, 0.7,
                            region_text_color, 2)

            time.sleep(0.03)  # To reduce CPU usage

            for region in counting_regions:
                region["counts"] = 0

            # Show frame in OpenCV window
            cv2.imshow(f"YOLOv8 Region Counter - {region_side}", frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

    except KeyboardInterrupt:
        logger.info("CTRL + C has been pressed")
    finally:
        videocapture.release()
        cv2.destroyAllWindows()


def detect_vehicle(weights, device, vehicle_detected, log_message):
    model = YOLO(f"{weights}")
    model.to("cuda" if device == "0" else "cpu")

    source = 0
    videocapture = cv2.VideoCapture(source)
    if not videocapture.isOpened():
        raise ValueError(f"Unable to open video source {source}")

    try:
        last_log_time = time.time()
        while videocapture.isOpened():
            success, frame = videocapture.read()
            if not success:
                break

            # Flip frame vertically
            frame = cv2.flip(frame, -1)

            with suppress_logging(logging.WARNING):
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
                    if time.time() - last_log_time >= 2:  # Log every 2 seconds
                        message = "Mobil terdeteksi."
                        logger.info(message)
                        log_message(message)
                        last_log_time = time.time()

            time.sleep(0.03)  # To reduce CPU usage

            # Show frame in OpenCV window
            cv2.imshow("YOLOv8 Vehicle Detection", frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

    except KeyboardInterrupt:
        logger.info("CTRL + C has been pressed")
    finally:
        videocapture.release()
        cv2.destroyAllWindows()
