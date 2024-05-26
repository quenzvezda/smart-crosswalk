import cv2
import numpy as np
import time
from collections import defaultdict
from shapely.geometry import Point
from ultralytics import YOLO
from ultralytics.utils.plotting import Annotator, colors
from region import counting_regions_kiri, counting_regions_kanan, track_history_kiri, track_history_kanan, mouse_callback
import logging
from client import log_message

logger = logging.getLogger('detector')

def detect_pedestrian(weights, device, region_side, pejalan_kaki_detected):
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
        last_log_time = time.time()
        while videocapture.isOpened():
            success, frame = videocapture.read()
            if not success:
                break

            results = model.track(frame, persist=True)
            annotator = Annotator(frame, line_width=2)

            current_time = time.time()

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
                                start_time = current_time
                            elif current_time - start_time >= 5:
                                pejalan_kaki_detected[region_side] = True
                                if current_time - last_log_time >= 5:
                                    message = f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Pejalan kaki {track_id} terdeteksi di {region['name']} selama 5 detik."
                                    logger.info(message)
                                    log_message(message)
                                    last_log_time = current_time
                        else:
                            start_time = None

            # Draw regions and update frame annotations
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

            time.sleep(0.03)  # To reduce CPU usage

            # Show frame in OpenCV window
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

def detect_vehicle(weights, device, vehicle_detected):
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

            frame = cv2.flip(frame, -1)

            results = model.track(frame, persist=True)
            annotator = Annotator(frame, line_width=2)

            current_time = time.time()

            if results[0].boxes.id is not None:
                boxes = results[0].boxes.xyxy.cpu().numpy()
                track_ids = results[0].boxes.id.cpu().tolist()
                clss = results[0].boxes.cls.cpu().tolist()

                for box, track_id, cls in zip(boxes, track_ids, clss):
                    annotator.box_label(box, str(model.model.names[cls]), color=colors(cls, True))
                    bbox_center = ((box[0] + box[2]) / 2, (box[1] + box[3]) / 2)

                    track = track_history_kiri[track_id] if cls == "kiri" else track_history_kanan[track_id]
                    track.append(bbox_center)
                    if len(track) > 60:
                        track.pop(0)

                    if len(track) > 1:
                        points = np.array(track, dtype=np.int32)
                        cv2.polylines(frame, [points], isClosed=False, color=colors(cls, True), thickness=2)

                    vehicle_detected["detected"] = True

                    if current_time - last_log_time >= 5:
                        message = f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Mobil terdeteksi."
                        logger.info(message)
                        log_message(message)
                        last_log_time = current_time

            time.sleep(0.03)  # To reduce CPU usage

            window_name = "YOLOv8 Vehicle Detection"
            cv2.imshow(window_name, frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

    except KeyboardInterrupt:
        logger.info("CTRL + C has been pressed")
    finally:
        videocapture.release()
        cv2.destroyAllWindows()
