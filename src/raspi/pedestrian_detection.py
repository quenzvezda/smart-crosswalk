import argparse
import signal
import socket
import sys
import threading
import time

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
        "polygon": Polygon([(176, 36), (416, 36), (416, 336), (176, 336)]),
        "counts": 0,
        "dragging": False,
        "region_color": (37, 255, 225),
        "text_color": (0, 0, 255),
    },
]

pejalan_kaki_detected = {"kiri": False, "kanan": False}


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


def detect_pedestrian(weights, source, device, region_side, classes=None, line_thickness=2, track_thickness=2,
                      region_thickness=2, duration=5):
    global pejalan_kaki_detected
    model = YOLO(f"{weights}")
    model.to("cuda" if device == "0" else "cpu")

    videocapture = cv2.VideoCapture(source)
    if not videocapture.isOpened():
        raise ValueError(f"Unable to open video source {source}")

    try:
        start_time = None
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
                    if len(track) > 60:
                        track.pop(0)

                    # Menggambar jalur tracking
                    if len(track) > 1:  # Pastikan ada lebih dari satu titik untuk membentuk garis
                        points = np.array(track, dtype=np.int32)
                        cv2.polylines(frame, [points], isClosed=False, color=colors(cls, True),
                                      thickness=track_thickness)

                    # Count objects within regions
                    for region in counting_regions:
                        if region["polygon"].contains(Point(bbox_center)):
                            region["counts"] += 1
                            if start_time is None:
                                start_time = time.time()
                            elif time.time() - start_time >= duration:
                                pejalan_kaki_detected[region_side] = True
                        else:
                            start_time = None

            # Draw regions and update frame annotations
            for region in counting_regions:
                region_label = str(region["counts"])
                region_color = region["region_color"]
                region_text_color = region["text_color"]

                polygon_coords = np.array(region["polygon"].exterior.coords, dtype=np.int32)
                centroid_x, centroid_y = int(region["polygon"].centroid.x), int(region["polygon"].centroid.y)

                cv2.polylines(frame, [polygon_coords], isClosed=True, color=region_color, thickness=region_thickness)
                cv2.putText(frame, region_label, (centroid_x, centroid_y), cv2.FONT_HERSHEY_SIMPLEX, 0.7,
                            region_text_color, line_thickness)

                # Display coordinates
                coords_text = "Coords: " + ', '.join([f"({int(x)}, {int(y)})" for x, y in polygon_coords])
                cv2.putText(frame, coords_text, (10, frame.shape[0] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5,
                            region_text_color, 1)

            cv2.imshow(f"YOLOv8 Region Counter - {region_side}", frame)
            cv2.setMouseCallback(f"YOLOv8 Region Counter - {region_side}", mouse_callback)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

            # Reset counts after displaying
            for region in counting_regions:
                region["counts"] = 0
    except KeyboardInterrupt:
        print("CTRL + C has been pressed")
    finally:
        videocapture.release()
        cv2.destroyAllWindows()


def detect_vehicle(weights, source, device, classes=None):
    global vehicle_detected
    model = YOLO(f"{weights}")
    model.to("cuda" if device == "0" else "cpu")

    videocapture = cv2.VideoCapture(source)
    if not videocapture.isOpened():
        raise ValueError(f"Unable to open video source {source}")

    try:
        while videocapture.isOpened():
            success, frame = videocapture.read()
            if not success:
                break

            results = model.track(frame, persist=True, classes=classes)
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

                    # Menggambar jalur tracking
                    if len(track) > 1:  # Pastikan ada lebih dari satu titik untuk membentuk garis
                        points = np.array(track, dtype=np.int32)
                        cv2.polylines(frame, [points], isClosed=False, color=colors(cls, True),
                                      thickness=2)

                    vehicle_detected = True

            cv2.imshow("YOLOv8 Vehicle Detection", frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
    except KeyboardInterrupt:
        print("CTRL + C has been pressed")
    finally:
        videocapture.release()
        cv2.destroyAllWindows()


def send_data_to_server(data):
    try:
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        host = '192.168.2.14'  # IP Raspberry Pi
        port = 12345
        client_socket.connect((host, port))
        client_socket.sendall(data.encode('utf-8'))
        client_socket.close()
    except Exception as e:
        print(f"Error sending data to server: {e}")


def monitor_pedestrian_and_vehicle(weights, device):
    pedestrian_thread_kiri = threading.Thread(target=detect_pedestrian, args=(weights, 1, device, "kiri"))
    pedestrian_thread_kanan = threading.Thread(target=detect_pedestrian, args=(weights, 2, device, "kanan"))
    vehicle_thread = threading.Thread(target=detect_vehicle, args=(weights, 0, device))

    pedestrian_thread_kiri.start()
    pedestrian_thread_kanan.start()
    vehicle_thread.start()

    while True:
        if pejalan_kaki_detected["kiri"] or pejalan_kaki_detected["kanan"]:
            if vehicle_detected:
                send_data_to_server("Terdeteksi Orang Di Penyebrangan (Dengan Mobil)")
            else:
                send_data_to_server("Terdeteksi Orang Di Penyebrangan (Tanpa Mobil)")
            pejalan_kaki_detected["kiri"] = False
            pejalan_kaki_detected["kanan"] = False
            vehicle_detected = False
        time.sleep(1)


def parse_opt():
    parser = argparse.ArgumentParser()
    parser.add_argument("--weights", type=str, default="yolov8n.pt", help="initial weights path")
    parser.add_argument("--device", default="0", help="cuda device, i.e. 0 or cpu")
    return parser.parse_args()


def signal_handler(sig, frame):
    print("You pressed Ctrl+C!")
    sys.exit(0)


if __name__ == "__main__":
    opt = parse_opt()
    signal.signal(signal.SIGINT, signal_handler)
    monitor_pedestrian_and_vehicle(opt.weights, opt.device)
