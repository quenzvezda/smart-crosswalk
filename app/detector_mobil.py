import cv2
import time
from ultralytics import YOLO
from ultralytics.utils.plotting import Annotator, colors
import logging
from src.distance.estimator import DistanceEstimator

logger = logging.getLogger('detector')

# Inisialisasi DistanceEstimator untuk mobil
focal = 502  # Panjang fokus kamera (hasil kalibrasi manual)
real_width = 3.5  # Lebar asli objek mobil dalam ukuran centi meter (cm)
distance_estimator = DistanceEstimator(focal_length=focal, real_width=real_width)


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
                    conf = box.conf[0]  # Confidence score
                    label = f"{model.model.names[cls]} {conf:.2f}"

                    # Estimasi jarak hanya untuk mobil (kelas 0)
                    if cls == 0:  # Assuming class '0' is 'mobil'
                        vehicle_detected["detected"] = True

                        # Hitung lebar bounding box dalam piksel
                        pixel_width = abs(xyxy[2] - xyxy[0])

                        # Estimasi jarak menggunakan DistanceEstimator
                        estimated_distance = distance_estimator.estimate(pixel_width)

                        if estimated_distance:
                            # Tampilkan jarak di atas bounding box
                            distance_label = f"Jarak: {estimated_distance:.2f} m"
                            label = f"{label} {distance_label}"

                        # Anotasi dengan label dan jarak
                        annotator.box_label(xyxy, label, color=colors(2, True))
                    else:
                        # Anotasi objek non-mobil dengan warna berbeda
                        annotator.box_label(xyxy, label, color=colors(1, True))

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
