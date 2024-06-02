import cv2
import time
from ultralytics import YOLO
from ultralytics.utils.plotting import Annotator, colors
import logging

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

            vehicle_detected["detected"] = False  # Default to False, set to True if any vehicle detected

            for result in results:
                for box in result.boxes:
                    cls = int(box.cls[0])  # Class index
                    xyxy = box.xyxy[0]  # Bounding box coordinates
                    if cls == 0:  # Assuming class '0' is 'mobil'
                        vehicle_detected["detected"] = True
                        annotator.box_label(xyxy, "mobil", color=colors(2, True))
                    else:
                        annotator.box_label(xyxy, "orang", color=colors(1, True))

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
