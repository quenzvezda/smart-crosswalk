import os
import xml.etree.ElementTree as ET
from ultralytics import YOLO
from sklearn.metrics import confusion_matrix, classification_report
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# Load YOLO model
model = YOLO("../../models/trisakti-yolov8m-roboflow.pt")

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

        # Get predictions from YOLO model
        results = model(img_path)

        # Convert results to bounding boxes and class names
        predictions = []
        for result in results[0].boxes.data:
            xmin, ymin, xmax, ymax, conf, cls = result
            cls_name = class_names[int(cls)]
            predictions.append((cls_name, int(xmin), int(ymin), int(xmax), int(ymax)))

        # Add ground truth and predictions to the lists
        for gt in ground_truths:
            gt_name, _, _, _, _ = gt
            y_true.append(gt_name)

        for pred in predictions:
            pred_name, _, _, _, _ = pred
            y_pred.append(pred_name)

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
plt.title('Confusion Matrix for YOLOv8')
plt.show()
