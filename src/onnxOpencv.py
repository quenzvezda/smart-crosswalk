# BELUM SELESAI

import cv2
import numpy as np

# Load ONNX model using OpenCV
net = cv2.dnn.readNetFromONNX("../models/trisakti-yolov8n.onnx")

# Read an image
image = cv2.imread('../data/test.jpg')
blob = cv2.dnn.blobFromImage(image, 1/255.0, (640, 640), swapRB=True, crop=False)
net.setInput(blob)

# Forward pass to get the output
output = net.forward()

# Initialize lists to hold the detection parameters
boxes = []
confs = []
class_ids = []

# Process the output
for detection in output[0]:
    x_center, y_center, width, height, conf, *class_scores = detection
    class_id = np.argmax(class_scores)
    class_score = class_scores[class_id]

    if conf > 0.01:  # Threshold for confidence
        x = int((x_center - width / 2) * image.shape[1] / 640)  # Scale factor for original image size
        y = int((y_center - height / 2) * image.shape[0] / 640)
        w = int(width * image.shape[1] / 640)
        h = int(height * image.shape[0] / 640)

        boxes.append([x, y, w, h])
        confs.append(float(conf))
        class_ids.append(class_id)

        # For debugging: print each detected box with its confidence and class id
        print(f"Detected box: ({x}, {y}, {w}, {h}) with confidence {conf} and class id {class_id}")

# Apply non-max suppression to reduce overlapping boxes
indices = cv2.dnn.NMSBoxes(boxes, confs, 0.25, 0.45)

# Draw the results on the image
for i in indices:
    i = int(i)  # Convert any NumPy type or list to a plain Python int
    box = boxes[i]
    x, y, w, h = box
    cv2.rectangle(image, (x, y), (x + w, y + h), (0, 255, 0), 2)
    cv2.putText(image, f'{class_ids[i]} {confs[i]:.2f}', (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)

# Save or display the image
cv2.imwrite("your_result_image.jpg", image)
cv2.imshow("Detected Objects", image)
cv2.waitKey(0)
cv2.destroyAllWindows()
