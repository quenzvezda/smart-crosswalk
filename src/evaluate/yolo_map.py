import os
import xml.etree.ElementTree as ET
import numpy as np
from ultralytics import YOLO
from pycocotools.coco import COCO
from pycocotools.cocoeval import COCOeval
import matplotlib.pyplot as plt
import json

# Load YOLO model
model = YOLO("../../models/trisakti-yolov8m-roboflow.pt")

# Define dataset path
dataset_path = '../../data/test'
annotation_path = '../../data/test/annotations.json'


# Function to parse XML file and convert to COCO format
def parse_xml_to_coco(dataset_path):
    images = []
    annotations = []
    categories = [
        {"id": 1, "name": "Mobil"},
        {"id": 2, "name": "Orang"}
    ]
    ann_id = 1

    for idx, filename in enumerate(os.listdir(dataset_path)):
        if filename.endswith('.jpg'):
            img_id = idx + 1
            img_path = os.path.join(dataset_path, filename)

            # Corresponding XML file
            xml_path = os.path.join(dataset_path, filename.replace('.jpg', '.xml'))

            # Parse XML
            tree = ET.parse(xml_path)
            root = tree.getroot()

            size = root.find('size')
            width = int(size.find('width').text)
            height = int(size.find('height').text)

            images.append({
                "id": img_id,
                "file_name": filename,
                "width": width,
                "height": height
            })

            for obj in root.findall('object'):
                name = obj.find('name').text
                class_id = 1 if name == "Mobil" else 2

                bndbox = obj.find('bndbox')
                xmin = int(bndbox.find('xmin').text)
                ymin = int(bndbox.find('ymin').text)
                xmax = int(bndbox.find('xmax').text)
                ymax = int(bndbox.find('ymax').text)

                annotations.append({
                    "id": ann_id,
                    "image_id": img_id,
                    "category_id": class_id,
                    "bbox": [xmin, ymin, xmax - xmin, ymax - ymin],
                    "area": (xmax - xmin) * (ymax - ymin),
                    "iscrowd": 0
                })
                ann_id += 1

    return {
        "images": images,
        "annotations": annotations,
        "categories": categories
    }


# Create COCO formatted annotations
coco_annotations = parse_xml_to_coco(dataset_path)

# Save annotations to a JSON file
with open(annotation_path, 'w') as f:
    json.dump(coco_annotations, f)

# Load COCO annotations
coco = COCO(annotation_path)

# Lists to store predictions
predictions = []

# Iterate through dataset for predictions
for img_id, img_info in coco.imgs.items():
    img_path = os.path.join(dataset_path, img_info['file_name'])

    # Get predictions from YOLO model
    results = model(img_path)

    # Convert results to COCO format
    for result in results[0].boxes.data:
        xmin, ymin, xmax, ymax, conf, cls = result.tolist()
        cls_id = int(cls) + 1  # Adjust class id to match COCO format

        predictions.append({
            "image_id": img_id,
            "category_id": cls_id,
            "bbox": [xmin, ymin, xmax - xmin, ymax - ymin],
            "score": float(conf)
        })

# Save predictions to a JSON file
predictions_path = '../../data/test/predictions.json'
with open(predictions_path, 'w') as f:
    json.dump(predictions, f)

# Load COCO formatted predictions
coco_dt = coco.loadRes(predictions_path)

# Evaluate using COCOeval
coco_eval = COCOeval(coco, coco_dt, 'bbox')
coco_eval.evaluate()
coco_eval.accumulate()
coco_eval.summarize()

# Extract mAP values
map_50 = coco_eval.stats[1]  # mAP@0.5
map_50_95 = coco_eval.stats[0]  # mAP@[0.5:0.95]

# Print mAP values
print(f"mAP@0.5: {map_50}")
print(f"mAP@[0.5:0.95]: {map_50_95}")

# Extract mAP values at different IoU thresholds
precision = coco_eval.eval['precision']
# IoU thresholds: precision has shape (iou, recall, class, area, max_dets)
iou_thresholds = np.linspace(0.5, 0.95, 10)
map_values = np.mean(precision, axis=1)[:, 0, 0, 0]

# Plot mAP values
plt.figure(figsize=(10, 7))
plt.plot(iou_thresholds, map_values, marker='o')
plt.xlabel('IoU Threshold')
plt.ylabel('mAP')
plt.title('mAP at Different IoU Thresholds for YOLOv8')
plt.grid(True)
plt.show()
