import os
import xml.etree.ElementTree as ET
import tensorflow as tf
import numpy as np
from sklearn.metrics import confusion_matrix, classification_report
import matplotlib.pyplot as plt
import seaborn as sns
import cv2

# Load the pretrained TensorFlow model
model_path = '../../models/ssd-new-dataset'
loaded_model = tf.saved_model.load(model_path)
infer = loaded_model.signatures['serving_default']

# Define class labels for the model
class_labels = {1: 'Mobil', 2: 'Orang'}

# Define dataset path
dataset_path = '../../data/test'

# Define the class names
class_names = ["Mobil", "Orang"]


# Function to parse XML file
def parse_xml(xml_file):
    tree = ET.parse(xml_file)
    root = tree.getroot()

    objects = []
    for obj in root.findall('object'):
        name = obj.find('name').text
        bndbox = obj.find('bndbox')
        xmin = int(bndbox.find('xmin').text)
        ymin = int(bndbox.find('ymin').text)
        xmax = int(bndbox.find('xmax').text)
        ymax = int(bndbox.find('ymax').text)
        objects.append((name, xmin, ymin, xmax, ymax))
    return objects


# Lists to store ground truth and predictions
y_true = []
y_pred = []

# Iterate through dataset
for filename in os.listdir(dataset_path):
    if filename.endswith('.jpg'):
        # Image path
        img_path = os.path.join(dataset_path, filename)

        # Corresponding XML file
        xml_path = os.path.join(dataset_path, filename.replace('.jpg', '.xml'))

        # Get ground truth annotations
        ground_truths = parse_xml(xml_path)

        # Read and preprocess the image
        frame = cv2.imread(img_path)
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

        predictions = []
        for i in range(len(scores)):
            if scores[i] > 0.5:  # confidence threshold
                class_id = int(classes[i])
                label = class_labels.get(class_id, 'Unknown')
                predictions.append(label)

        # Add ground truth and predictions to the lists
        for gt in ground_truths:
            gt_name, _, _, _, _ = gt
            y_true.append(gt_name)

        for pred in predictions:
            y_pred.append(pred)

# Ensure that y_true and y_pred have the same length
min_length = min(len(y_true), len(y_pred))
y_true = y_true[:min_length]
y_pred = y_pred[:min_length]

# Create confusion matrix
cm = confusion_matrix(y_true, y_pred, labels=class_names)

# Normalize confusion matrix
cm_normalized = cm.astype('float') / cm.sum(axis=1)[:, np.newaxis]

# Print confusion matrix
print("Confusion Matrix:")
print(cm)
print("\nNormalized Confusion Matrix:")
print(cm_normalized)
print("\nClassification Report:")
report = classification_report(y_true, y_pred, target_names=class_names)
print(report)

# Plot normalized confusion matrix
plt.figure(figsize=(10, 7))
sns.heatmap(cm_normalized, annot=True, fmt=".2f", cmap="Blues", xticklabels=class_names, yticklabels=class_names)
plt.xlabel('Predicted Values')
plt.ylabel('Actual Values')
plt.title('Confusion Matrix for SSD MobileNet V2')
plt.show()
