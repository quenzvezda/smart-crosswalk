import cv2
import tensorflow as tf
import numpy as np
import threading

# Load the pretrained TensorFlow model
model_path = '../models/ssd-new-dataset'
loaded_model = tf.saved_model.load(model_path)
infer = loaded_model.signatures['serving_default']

# Define class labels for the model
class_labels = {1: 'mobil', 2: 'pejalan kaki'}


# Function to process each video stream
def process_video(camera_index):
    cap = cv2.VideoCapture(camera_index)

    try:
        while True:
            # Capture frame-by-frame
            ret, frame = cap.read()
            if not ret:
                break

            # Preprocess the frame
            resized_frame = cv2.resize(frame, (640, 640))
            rgb_frame = cv2.cvtColor(resized_frame, cv2.COLOR_BGR2RGB)
            normalized_frame = np.clip(rgb_frame, 0, 255).astype(np.uint8)
            input_tensor = np.expand_dims(normalized_frame, axis=0)

            # Perform the detection
            output_dict = infer(input_tensor=tf.convert_to_tensor(input_tensor))

            # Post-processing
            boxes = output_dict['detection_boxes'][0].numpy()
            scores = output_dict['detection_scores'][0].numpy()
            classes = output_dict['detection_classes'][0].numpy()

            for i in range(len(scores)):
                if scores[i] > 0.5:  # confidence threshold
                    y_min, x_min, y_max, x_max = boxes[i]
                    class_id = int(classes[i])
                    label = class_labels.get(class_id, 'Unknown')
                    score = round(scores[i] * 100, 2)

                    (left, right, top, bottom) = (x_min * frame.shape[1], x_max * frame.shape[1],
                                                  y_min * frame.shape[0], y_max * frame.shape[0])
                    frame = cv2.rectangle(frame, (int(left), int(top)), (int(right), int(bottom)), (0, 255, 0), 2)
                    label_text = f"{label}: {score}%"
                    frame = cv2.putText(frame, label_text, (int(left), int(top - 10)), cv2.FONT_HERSHEY_SIMPLEX,
                                        0.5, (255, 255, 255), 2)

            # Display the resulting frame
            cv2.imshow(f'Frame from camera {camera_index}', frame)

            # Break the loop with 'q'
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
    finally:
        # When everything done, release the capture
        cap.release()
        cv2.destroyAllWindows()


# Start a thread for each camera
threads = []
camera_indexes = [0, 1, 2]
for index in camera_indexes:
    thread = threading.Thread(target=process_video, args=(index,))
    thread.start()
    threads.append(thread)

# Wait for all threads to finish
for thread in threads:
    thread.join()
