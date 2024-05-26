import threading
import signal
import sys
import time
from detector import detect_pedestrian, detect_vehicle
from client import send_data_to_server, monitor_server_response

# Global flags
pejalan_kaki_detected = {"kiri": False, "kanan": False}
vehicle_detected = False

def pedestrian_monitor(weights, device, region_side):
    global pejalan_kaki_detected
    detect_pedestrian(weights, device, region_side, pejalan_kaki_detected)

def vehicle_monitor(weights, device):
    global vehicle_detected
    detect_vehicle(weights, device, vehicle_detected)

def main(weights, device):
    pedestrian_thread_kiri = threading.Thread(target=pedestrian_monitor, args=(weights, device, "kiri"))
    pedestrian_thread_kanan = threading.Thread(target=pedestrian_monitor, args=(weights, device, "kanan"))
    vehicle_thread = threading.Thread(target=vehicle_monitor, args=(weights, device))
    server_thread = threading.Thread(target=monitor_server_response)

    pedestrian_thread_kiri.start()
    pedestrian_thread_kanan.start()
    vehicle_thread.start()
    server_thread.start()

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
    import argparse
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
    main(opt.weights, opt.device)
