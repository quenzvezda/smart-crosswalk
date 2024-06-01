import threading
import time
import logging
from detector_orang import detect_pedestrian, logger
from detector_mobil import detect_vehicle

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

total_pejalan_kaki = {"kiri": 0, "kanan": 0}
lock = threading.Lock()


def log_message(message):
    logger.info(message)


def central_log_and_check(pejalan_kaki_detected, vehicle_detected):
    while True:
        time.sleep(5)
        total_orang = total_pejalan_kaki["kiri"] + total_pejalan_kaki["kanan"]
        if total_orang > 0:
            if vehicle_detected["detected"]:
                message = f"Terdeteksi total [{total_orang} Orang] dan Mobil selama 5 detik."
            else:
                message = f"Terdeteksi total [{total_orang} Orang] selama 5 detik."
            log_message(message)
            with lock:
                total_pejalan_kaki["kiri"] = 0
                total_pejalan_kaki["kanan"] = 0
            pejalan_kaki_detected["kiri"] = False
            pejalan_kaki_detected["kanan"] = False


def start_detection_threads(weights, device):
    pejalan_kaki_detected = {"kiri": False, "kanan": False}
    vehicle_detected = {"detected": False}
    threading.Thread(target=detect_pedestrian, args=(
    weights, device, "kiri", pejalan_kaki_detected, vehicle_detected, total_pejalan_kaki, lock)).start()
    threading.Thread(target=detect_pedestrian, args=(
    weights, device, "kanan", pejalan_kaki_detected, vehicle_detected, total_pejalan_kaki, lock)).start()
    threading.Thread(target=detect_vehicle, args=(weights, device, vehicle_detected)).start()
    threading.Thread(target=central_log_and_check, args=(pejalan_kaki_detected, vehicle_detected)).start()


# Start detection threads
weights = "../models/trisakti-batch_1-yolov8s-roboflow.pt"
device = "0"
start_detection_threads(weights, device)
