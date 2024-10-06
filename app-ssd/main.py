import datetime
import threading
import time
import cv2
import tensorflow as tf
import configparser
from camera_processor import process_frame
from mouse_controller import MouseController
from client import ServerConnection
from src.distance.estimator import DistanceEstimator

# Initialize ConfigParser
config = configparser.ConfigParser()
config.read('config.ini')

# Read Camera indexes and roles
indexes = config.get('Camera', 'indexes').split(',')
indexes = [int(i.strip()) for i in indexes]
roles = config.get('Camera', 'roles').split(',')
roles = [role.strip() for role in roles]

camera_roles = {indexes[i]: roles[i] for i in range(len(indexes))}

# Read index_to_flip
index_to_flip = config.getint('Camera', 'index_to_flip')

# Initialize MouseController Object
mouse_controller = MouseController()

# Read and set up ROIs
for index in indexes:
    key = f'roi_{index}'
    if key in config['Camera']:
        roi_values = config.get('Camera', key).split(',')
        roi_values = [float(x.strip()) for x in roi_values]
        mouse_controller.setup_roi(index, roi_values)

# Read server settings
server_host = config.get('Server', 'host')
server_port = config.getint('Server', 'port')

# Setup server connection Object
server = ServerConnection(server_host, server_port)
server.connect()
server.start_receiving_thread()

# Read model path
model_path = config.get('Model', 'path')

# Define your TensorFlow model here
loaded_model = tf.saved_model.load(model_path)
infer = loaded_model.signatures['serving_default']

# Read DistanceEstimator settings
focal_length = config.getfloat('DistanceEstimator', 'focal_length')
real_width = config.getfloat('DistanceEstimator', 'real_width')

# Initialize DistanceEstimator
distance_estimator = DistanceEstimator(focal_length=focal_length, real_width=real_width)

# Global variables
total_orang_kiri = 0
total_orang_kanan = 0
vehicle_detected = None  # Changed to hold distance
is_pedestrian_run = server.is_pedestrian_running
is_minimum_time_reach = server.is_minimum_time_reached

# Initialize lock
lock = threading.Lock()


def camera_thread(camera_index, infer_param, mouse_controller_param, flip_param=False, distance_estimator_param=None):
    global total_orang_kiri, total_orang_kanan, vehicle_detected
    cap = cv2.VideoCapture(camera_index)
    ret, frame = cap.read()
    if not ret:
        print(f"Failed to read from camera {camera_index}")
        return
    cv2.namedWindow(f'Camera {camera_index}')
    cv2.setMouseCallback(f'Camera {camera_index}', mouse_controller_param.mouse_event,
                         param=(camera_index, frame.shape))

    camera_role = camera_roles[camera_index]

    while True:
        ret, frame = cap.read()
        if not ret:
            break
        if flip_param:
            frame = cv2.flip(frame, -1)
        roi = mouse_controller_param.get_roi(camera_index)

        # Set estimate_distance to True only for the 'vehicle' camera
        estimate_distance = (camera_role == 'vehicle')

        frame, count_people_in_roi, vehicle_detected_in_frame = process_frame(
            frame, infer_param, {1: 'mobil', 2: 'orang'}, roi, estimate_distance=estimate_distance,
            distance_estimator=distance_estimator_param)

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
                        server.send_data(
                            f"Terdeteksi {total_orang} Orang Di Penyebrangan (Dengan Mobil) {current_vehicle_distance:.2f} m")
                        print(
                            f"{timestamp}] Terdeteksi [{total_orang} Orang ({total_orang_kiri} Cam Kiri - {total_orang_kanan} Cam Kanan)] (Dengan Mobil) {current_vehicle_distance:.2f} m selama 5 detik.")
                    else:
                        server.send_data(f"Terdeteksi {total_orang} Orang Di Penyebrangan (Tanpa Mobil)")
                        print(
                            f"{timestamp}] Terdeteksi [{total_orang} Orang ({total_orang_kiri} Cam Kiri - {total_orang_kanan} Cam Kanan)] (Tanpa Mobil) selama 5 detik.")
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


# Start threads for each camera using the list of camera indexes
threads = []
for index in camera_roles.keys():
    flip = (index == index_to_flip)
    # Pass distance_estimator to the camera_thread
    thread = threading.Thread(target=camera_thread, args=(index, infer, mouse_controller, flip, distance_estimator))
    thread.start()
    threads.append(thread)

# Setup and start the central log thread
log_thread = threading.Thread(target=central_log)
log_thread.start()

# Wait for all threads to finish
for thread in threads:
    thread.join()
log_thread.join()
