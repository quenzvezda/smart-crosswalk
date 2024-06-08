import cv2
import threading
from camera_processor import process_frame
from utils import is_within_roi, calculate_overlap
import tensorflow as tf
from mouse_controller import MouseController

mouse_controller = MouseController()
mouse_controller.setup_roi(1, [0.25, 0.26, 0.73, 0.63])  # ymin, xmin, ymax, xmax for camera 1
mouse_controller.setup_roi(2, [0.15, 0.30, 0.61, 0.65])  # ymin, xmin, ymax, xmax for camera 2


def camera_thread(camera_index, infer, mouse_controller):
    cap = cv2.VideoCapture(camera_index)
    cv2.namedWindow(f'Camera {camera_index}')
    cv2.setMouseCallback(f'Camera {camera_index}', mouse_controller.mouse_event,
                         param=(camera_index, cap.read()[1].shape))

    while True:
        ret, frame = cap.read()
        if not ret:
            break
        roi = mouse_controller.get_roi(camera_index)
        frame = process_frame(frame, infer, {1: 'mobil', 2: 'orang'}, roi)
        cv2.imshow(f'Camera {camera_index}', frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()


# Define your TensorFlow model here
model_path = '../models/ssd-new-dataset'
loaded_model = tf.saved_model.load(model_path)
infer = loaded_model.signatures['serving_default']

# Start threads for each camera
threads = []
for index in range(3):  # Adjust number of cameras here
    thread = threading.Thread(target=camera_thread, args=(index, infer, mouse_controller))
    thread.start()
    threads.append(thread)

# Wait for all threads to finish
for thread in threads:
    thread.join()
