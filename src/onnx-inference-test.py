import cv2
import onnxruntime as ort
import numpy as np
import time

# Load the ONNX model
onnx_model_path = '../models/ssd-model.onnx'

# Set session options
sess_options = ort.SessionOptions()
sess_options.log_severity_level = 1

# Configure the session to use the GPU
providers = ['CUDAExecutionProvider', 'CPUExecutionProvider']
session = ort.InferenceSession(onnx_model_path, providers=providers, sess_options=sess_options)

# Verify if the GPU is being used
print("ONNX Runtime providers:", session.get_providers())
print("Device being used:", ort.get_device())

# Assuming the model input size is known (e.g., 300x300)
input_height = 300
input_width = 300

# Get model input details
input_name = session.get_inputs()[0].name

# Define a function to preprocess the image
def preprocess(image):
    # Resize the image to the input shape of the model
    resized_image = cv2.resize(image, (input_width, input_height))
    # Convert to uint8
    input_data = resized_image.astype(np.uint8)
    # Convert to the required input shape
    input_data = np.expand_dims(input_data, axis=0)
    return input_data

# Define a function to draw bounding boxes on the image
def draw_boxes(image, boxes, scores, classes, threshold=0.5):
    h, w, _ = image.shape
    class_names = {1: 'car', 2: 'person'}
    for box, score, cls in zip(boxes, scores, classes):
        if score > threshold:
            # Convert the relative coordinates to absolute coordinates
            x1 = int(box[1] * w)
            y1 = int(box[0] * h)
            x2 = int(box[3] * w)
            y2 = int(box[2] * h)
            class_name = class_names.get(cls, 'unknown')
            cv2.rectangle(image, (x1, y1), (x2, y2), (0, 255, 0), 2)
            cv2.putText(image, f'{class_name}: {score:.2f}', (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

# Open a connection to the webcam
cap = cv2.VideoCapture(0)

while True:
    # Capture a frame from the webcam
    ret, frame = cap.read()
    if not ret:
        break

    # Preprocess the frame
    input_data = preprocess(frame)

    # Perform inference
    start_time = time.time()
    outputs = session.run(None, {input_name: input_data})
    end_time = time.time()

    # Print inference time
    print("Inference time: {:.4f} seconds".format(end_time - start_time))

    # Extract detection results
    detection_boxes = outputs[1][0]
    detection_scores = outputs[4][0]
    detection_classes = outputs[2][0]

    # Draw bounding boxes on the frame
    draw_boxes(frame, detection_boxes, detection_scores, detection_classes)

    # Display the frame
    cv2.imshow('Webcam Object Detection', frame)

    # Exit the loop if the 'q' key is pressed
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release the webcam and close the window
cap.release()
cv2.destroyAllWindows()
