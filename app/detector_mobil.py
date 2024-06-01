import cv2
import time
from ultralytics import YOLO
from ultralytics.utils.plotting import Annotator, colors
import logging
from client import log_message

logger = logging.getLogger('detector')

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

            frame = cv2.flip(frame, -1)

            with suppress_logging(logging.WARNING):  # Suppress YOLO logs
                results = model.track(frame, persist=True)
            annotator = Annotator(frame, line_width=2)

            if results[0].boxes.id is not None:
                vehicle_detected["detected"] = True
            else:
                vehicle_detected["detected"] = False

            for box in results[0].boxes.xyxy:
                annotator.box_label(box, "Mobil", color=colors(2, True))

            annotated_frame = annotator.result()
            window_name = "YOLOv8 Vehicle Detection"
            cv2.imshow(window_name, annotated_frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

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
