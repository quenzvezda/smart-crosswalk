import threading
import time
import logging
from detector_orang import detect_pedestrian, logger
from detector_mobil import detect_vehicle
from client import send_data_to_server, isProcessRun, lock, monitor_server_response

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

total_pejalan_kaki = {"kiri": 0, "kanan": 0}
pejalan_kaki_detected = {"kiri": False, "kanan": False}
vehicle_detected = {"detected": False}


def log_message(message):
    logger.info(message)


def central_log_and_check(pejalan_kaki_detected, vehicle_detected):
    last_log_time = None
    while True:
        with lock:
            total_orang = total_pejalan_kaki["kiri"] + total_pejalan_kaki["kanan"]
            orang_kiri = total_pejalan_kaki["kiri"]
            orang_kanan = total_pejalan_kaki["kanan"]
            process_running = isProcessRun

        if total_orang > 0:
            if last_log_time is None:
                last_log_time = time.time()
            current_time = time.time()
            elapsed_time = current_time - last_log_time

            if elapsed_time >= 5:
                if process_running:
                    message = f"Siklus lampu sedang berjalan berjalan, tidak mengirim data ke server."
                    log_message(message)
                else:
                    if vehicle_detected["detected"]:
                        message = f"Terdeteksi [{total_orang} Orang ({orang_kiri} Cam Kiri - {orang_kanan} Cam Kanan)] (Dengan Mobil) selama 5 detik."
                        send_data_to_server(f"Terdeteksi {total_orang} Orang Di Penyebrangan (Dengan Mobil)")
                    else:
                        message = f"Terdeteksi [{total_orang} Orang ({orang_kiri} Cam Kiri - {orang_kanan} Cam Kanan)] (Tanpa Mobil) selama 5 detik."
                        send_data_to_server(f"Terdeteksi {total_orang} Orang Di Penyebrangan (Tanpa Mobil)")
                    log_message(message)
                with lock:
                    total_pejalan_kaki["kiri"] = 0
                    total_pejalan_kaki["kanan"] = 0
                    pejalan_kaki_detected["kiri"] = False
                    pejalan_kaki_detected["kanan"] = False
                last_log_time = None
        else:
            last_log_time = None

        time.sleep(0.1)


def start_detection_threads(weights, device):
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

# Start the thread to monitor server response
threading.Thread(target=monitor_server_response, daemon=True).start()
