import os
import xml.etree.ElementTree as ET
from ultralytics import YOLO
from sklearn.metrics import confusion_matrix, classification_report
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd

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

# Generate classification report
report = classification_report(y_true, y_pred, target_names=class_names, output_dict=True)

# Convert report to DataFrame
report_df = pd.DataFrame(report).transpose()

# Print the classification report for each class
print("Classification Report for Each Class:")
print(report_df[['precision', 'recall', 'f1-score']])

# Extract precision, recall, and f1-score
metrics = report_df[['precision', 'recall', 'f1-score']].iloc[:-1]

# Plot precision, recall, and f1-score
metrics.plot(kind='bar', figsize=(10, 7))
plt.title('Precision, Recall, and F1 Score for YOLOv8')
plt.xlabel('Classes')
plt.ylabel('Score')
plt.ylim(0, 1)
plt.xticks(rotation=0)
plt.legend(loc='lower right')
plt.show()
