import cv2
import threading
from camera_processor import process_frame
from utils import is_within_roi, calculate_overlap
import tensorflow as tf

# Define the ROIs for each camera (example coordinates, you might need to adjust them)
rois = {
    1: [0.1, 0.1, 0.5, 0.5],  # ymin, xmin, ymax, xmax
    2: [0.2, 0.2, 0.6, 0.6]
}


def camera_thread(camera_index, infer):
    cap = cv2.VideoCapture(camera_index)
    roi = rois.get(camera_index, None)

    while True:
        ret, frame = cap.read()
        if not ret:
            break
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
    thread = threading.Thread(target=camera_thread, args=(index, infer))
    thread.start()
    threads.append(thread)

# Wait for all threads to finish
for thread in threads:
    thread.join()
