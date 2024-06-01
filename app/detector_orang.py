import cv2
import numpy as np
import time
from collections import defaultdict
from shapely.geometry import Point
from ultralytics import YOLO
from ultralytics.utils.plotting import Annotator, colors
from region import counting_regions_kiri, counting_regions_kanan, track_history_kiri, track_history_kanan, \
    mouse_callback
import logging
# from client import log_message

logger = logging.getLogger('detector')


def detect_pedestrian(weights, device, region_side, pejalan_kaki_detected, vehicle_detected, total_pejalan_kaki, lock):
    model = YOLO(f"{weights}")
    model.to("cuda" if device == "0" else "cpu")

    source = 1 if region_side == "kiri" else 2
    videocapture = cv2.VideoCapture(source)
    if not videocapture.isOpened():
        raise ValueError(f"Unable to open video source {source}")

    track_history = track_history_kiri if region_side == "kiri" else track_history_kanan
    counting_regions = counting_regions_kiri if region_side == "kiri" else counting_regions_kanan

    try:
        start_time = None
        while videocapture.isOpened():
            success, frame = videocapture.read()
            if not success:
                break

            with suppress_logging(logging.WARNING):  # Suppress YOLO logs
                results = model.track(frame, persist=True)
            annotator = Annotator(frame, line_width=2)

            current_time = time.time()

            if results[0].boxes.id is not None:
                boxes = results[0].boxes.xyxy.cpu().numpy()
                track_ids = results[0].boxes.id.cpu().tolist()
                clss = results[0].boxes.cls.cpu().tolist()

                current_pejalan_kaki = set()

                for box, track_id, cls in zip(boxes, track_ids, clss):
                    annotator.box_label(box, str(model.model.names[cls]), color=colors(cls, True))
                    bbox_center = ((box[0] + box[2]) / 2, (box[1] + box[3]) / 2)

                    track = track_history[track_id]
                    track.append(bbox_center)
                    if len(track) > 30:
                        track.pop(0)

                    if len(track) > 1:
                        points = np.array(track, dtype=np.int32)
                        cv2.polylines(frame, [points], isClosed=False, color=colors(cls, True), thickness=2)

                    for region in counting_regions:
                        if region["polygon"].contains(Point(bbox_center)):
                            current_pejalan_kaki.add(track_id)
                            region["counts"] += 1
                            if start_time is None:
                                start_time = current_time
                            elif current_time - start_time >= 5:
                                pejalan_kaki_detected[region_side] = True
                                # if current_time - last_log_time >= 5:
                                #     # message = f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Pejalan kaki {track_id} terdeteksi di {region['name']} selama 5 detik."
                                #     # log_message(message)
                                #     # logger.info(message)  # Also log to file
                                #     last_log_time = current_time
                        else:
                            start_time = None

                # Update total_pejalan_kaki based on current detections
                with lock:
                    total_pejalan_kaki[region_side] = len(current_pejalan_kaki)
                    # print(len(current_pejalan_kaki), time.time(), region_side)  # Log Real Time Object Counting

            else:
                # When no boxes are detected, set the count to 0
                with lock:
                    total_pejalan_kaki[region_side] = 0
                    # print(0, time.time(), region_side)  # Log Real Time Object Counting

            for region in counting_regions:
                region_label = str(region["counts"])
                region_color = region["region_color"]
                region_text_color = region["text_color"]

                polygon_coords = np.array(region["polygon"].exterior.coords, dtype=np.int32)
                centroid_x, centroid_y = int(region["polygon"].centroid.x), int(region["polygon"].centroid.y)

                cv2.polylines(frame, [polygon_coords], isClosed=True, color=region_color, thickness=2)
                cv2.putText(frame, region_label, (centroid_x, centroid_y), cv2.FONT_HERSHEY_SIMPLEX, 0.7,
                            region_text_color, 2)

                coords_text = "Coords: " + ', '.join([f"({int(x)}, {int(y)})" for x, y in polygon_coords])
                cv2.putText(frame, coords_text, (10, frame.shape[0] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5,
                            region_text_color, 1)

            window_name = f"YOLOv8 Region Counter - {region_side}"
            cv2.imshow(window_name, frame)
            cv2.setMouseCallback(window_name, mouse_callback, counting_regions)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

            for region in counting_regions:
                region["counts"] = 0

    except KeyboardInterrupt:
        logger.info("CTRL + C has been pressed")
    finally:
        videocapture.release()
        cv2.destroyAllWindows()


# Function to suppress YOLO logging
from contextlib import contextmanager
import logging


@contextmanager
def suppress_logging(level=logging.WARNING):
    logger = logging.getLogger("ultralytics")
    previous_level = logger.getEffectiveLevel()
    logger.setLevel(level)
    try:
        yield
    finally:
        logger.setLevel(previous_level)
