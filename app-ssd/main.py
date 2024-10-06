import datetime
import threading
import time
import cv2
import tensorflow as tf
from camera_processor import process_frame
from mouse_controller import MouseController
from client import ServerConnection

# Mapping of camera indexes to their roles
camera_roles = {
    0: 'vehicle',  # Kamera mobil yang perlu dibalik
    1: 'left',     # Kamera orang kiri
    2: 'right'     # Kamera orang kanan
}

# Setup server connection
server = ServerConnection('192.168.2.101', 60003)
server.connect()
server.start_receiving_thread()

# Index yang harus dibalik
index_to_flip = 0

mouse_controller = MouseController()
mouse_controller.setup_roi(1, [0.25, 0.26, 0.73, 0.63])  # ymin, xmin, ymax, xmax for camera 1
mouse_controller.setup_roi(2, [0.15, 0.30, 0.61, 0.65])  # ymin, xmin, ymax, xmax for camera 2

# Global variables
total_orang_kiri = 0
total_orang_kanan = 0
vehicle_detected = None
is_pedestrian_run = server.is_pedestrian_running
is_minimum_time_reach = server.is_minimum_time_reached

# Initialize lock
lock = threading.Lock()


def camera_thread(camera_index, infer, mouse_controller, flip=False):
    global total_orang_kiri, total_orang_kanan, vehicle_detected
    cap = cv2.VideoCapture(camera_index)
    ret, frame = cap.read()
    if not ret:
        print(f"Failed to read from camera {camera_index}")
        return
    cv2.namedWindow(f'Camera {camera_index}')
    cv2.setMouseCallback(f'Camera {camera_index}', mouse_controller.mouse_event,
                         param=(camera_index, frame.shape))

    camera_role = camera_roles[camera_index]

    while True:
        ret, frame = cap.read()
        if not ret:
            break
        if flip:
            frame = cv2.flip(frame, -1)
        roi = mouse_controller.get_roi(camera_index)

        # Set estimate_distance to True only for the 'vehicle' camera
        estimate_distance = (camera_role == 'vehicle')

        frame, count_people_in_roi, vehicle_detected_in_frame = process_frame(
            frame, infer, {1: 'mobil', 2: 'orang'}, roi, estimate_distance=estimate_distance)

        # Update global variables with lock
        with lock:
            if camera_role == 'left':
                total_orang_kiri = count_people_in_roi
            elif camera_role == 'right':
                total_orang_kanan = count_people_in_roi
            elif camera_role == 'vehicle':
                vehicle_detected = vehicle_detected_in_frame  # Now holds the closest distance

        cv2.imshow(f'Camera {camera_index}', frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()


def central_log():
    global total_orang_kiri, total_orang_kanan, vehicle_detected
    last_log_time = time.time()

    while True:
        with lock:
            total_orang = total_orang_kiri + total_orang_kanan
            current_vehicle_distance = vehicle_detected  # None or distance in meters

        current_time = time.time()

        if total_orang > 0:
            if not server.is_pedestrian_running:
                if (current_time - last_log_time) >= 5:
                    now = datetime.datetime.now()
                    timestamp = now.strftime("[%H:%M:%S.%f]")[:-3]
                    if current_vehicle_distance is not None:
                        server.send_data(f"Terdeteksi {total_orang} Orang Di Penyebrangan (Dengan Mobil) {current_vehicle_distance:.2f} cm")
                        print(f"{timestamp}] Terdeteksi [{total_orang} Orang ({total_orang_kiri} Cam Kiri - {total_orang_kanan} Cam Kanan)] (Dengan Mobil) {current_vehicle_distance:.2f} cm selama 5 detik.")
                    else:
                        server.send_data(f"Terdeteksi {total_orang} Orang Di Penyebrangan (Tanpa Mobil)")
                        print(f"{timestamp}] Terdeteksi [{total_orang} Orang ({total_orang_kiri} Cam Kiri - {total_orang_kanan} Cam Kanan)] (Tanpa Mobil) selama 5 detik.")
                    last_log_time = current_time  # Reset timer
        else:
            last_log_time = current_time  # Reset timer if no people are detected
            if server.is_minimum_time_reached:
                now = datetime.datetime.now()
                timestamp = now.strftime("[%H:%M:%S.%f]")[:-3]
                server.send_data("Zebra Cross is Clear")
                server.is_minimum_time_reached = False
                print(f"{timestamp}] Zebra Cross is Clear")

        time.sleep(0.1)  # Reduce CPU usage


# Define your TensorFlow model here
model_path = '../models/ssd-new-dataset'
loaded_model = tf.saved_model.load(model_path)
infer = loaded_model.signatures['serving_default']

# Start threads for each camera using the list of camera indexes
threads = []
for index in camera_roles.keys():
    flip = (index == index_to_flip)
    thread = threading.Thread(target=camera_thread, args=(index, infer, mouse_controller, flip))
    thread.start()
    threads.append(thread)

# Setup and start the central log thread
log_thread = threading.Thread(target=central_log)
log_thread.start()

# Wait for all threads to finish
for thread in threads:
    thread.join()
log_thread.join()
