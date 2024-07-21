import threading
import time
import logging
from detector_orang import detect_pedestrian, logger
from detector_mobil import detect_vehicle
from client import ServerConnection

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

total_pejalan_kaki = {"kiri": 0, "kanan": 0}
pejalan_kaki_detected = {"kiri": False, "kanan": False}
vehicle_detected = {"detected": False}

is_minimum_time_reach = False


def log_message(message):
    logger.info(message)


def set_is_minimum_time_reach(value):
    global is_minimum_time_reach
    is_minimum_time_reach = value


def central_log_and_check(client):
    last_log_time = None
    while True:
        with threading.Lock():
            total_orang = total_pejalan_kaki["kiri"] + total_pejalan_kaki["kanan"]
            orang_kiri = total_pejalan_kaki["kiri"]
            orang_kanan = total_pejalan_kaki["kanan"]
            process_running = client.is_pedestrian_running
            minimum_time_reach = client.is_minimum_time_reached

        if total_orang > 0:
            if last_log_time is None:
                last_log_time = time.time()
            current_time = time.time()
            elapsed_time = current_time - last_log_time

            if elapsed_time >= 5:
                if process_running:
                    message = "Siklus lampu sedang berjalan, tidak mengirim data ke server."
                    log_message(message)
                else:
                    if vehicle_detected["detected"]:
                        message = f"Terdeteksi [{total_orang} Orang ({orang_kiri} Cam Kiri - {orang_kanan} Cam Kanan)] (Dengan Mobil) selama 5 detik."
                        client.send_data(f"Terdeteksi {total_orang} Orang Di Penyebrangan (Dengan Mobil)")
                    else:
                        message = f"Terdeteksi [{total_orang} Orang ({orang_kiri} Cam Kiri - {orang_kanan} Cam Kanan)] (Tanpa Mobil) selama 5 detik."
                        client.send_data(f"Terdeteksi {total_orang} Orang Di Penyebrangan (Tanpa Mobil)")
                    log_message(message)
                with threading.Lock():
                    total_pejalan_kaki["kiri"] = 0
                    total_pejalan_kaki["kanan"] = 0
                    pejalan_kaki_detected["kiri"] = False
                    pejalan_kaki_detected["kanan"] = False
                last_log_time = None
        else:
            last_log_time = None
            if minimum_time_reach and process_running:
                client.send_data("Zebra Cross is Clear")
                with threading.Lock():
                    set_is_minimum_time_reach(False)

        time.sleep(0.1)


def start_detection_threads(weights, device, client):
    threading.Thread(target=detect_pedestrian, args=(
        weights, device, "kiri", pejalan_kaki_detected, vehicle_detected, total_pejalan_kaki, threading.Lock())).start()
    threading.Thread(target=detect_pedestrian, args=(
        weights, device, "kanan", pejalan_kaki_detected, vehicle_detected, total_pejalan_kaki, threading.Lock())).start()
    threading.Thread(target=detect_vehicle, args=(weights, device, vehicle_detected)).start()
    threading.Thread(target=central_log_and_check, args=(client,)).start()


# Start the server connection
server = ServerConnection('192.168.43.160', 60003)
server.connect()
server.start_receiving_thread()

# Start detection threads
weights = "../models/trisakti-batch_1-yolov8s-roboflow.pt"
device = "0"
start_detection_threads(weights, device, server)
