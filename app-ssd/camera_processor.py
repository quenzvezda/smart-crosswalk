import cv2
import numpy as np
from utils import is_within_roi, calculate_overlap

def process_frame(frame, infer, class_labels, roi=None):
    # Preprocessing
    resized_frame = cv2.resize(frame, (640, 640))
    rgb_frame = cv2.cvtColor(resized_frame, cv2.COLOR_BGR2RGB)
    normalized_frame = np.clip(rgb_frame, 0, 255).astype(np.uint8)
    input_tensor = np.expand_dims(normalized_frame, axis=0)

    # Detection
    output_dict = infer(input_tensor=input_tensor)

    # Post-processing
    boxes = output_dict['detection_boxes'][0].numpy()
    scores = output_dict['detection_scores'][0].numpy()
    classes = output_dict['detection_classes'][0].numpy()
    count_people_in_roi = 0

    for i in range(len(scores)):
        if scores[i] > 0.5:
            box = boxes[i]
            class_id = int(classes[i])
            if class_labels[class_id] == "orang" and roi:
                if calculate_overlap(box, roi) > 0.5:
                    count_people_in_roi += 1

            label = class_labels.get(class_id, 'Unknown')
            score = round(scores[i] * 100, 2)
            (left, right, top, bottom) = (box[1] * frame.shape[1], box[3] * frame.shape[1],
                                          box[0] * frame.shape[0], box[2] * frame.shape[0])
            frame = cv2.rectangle(frame, (int(left), int(top)), (int(right), int(bottom)), (0, 255, 0), 2)
            label_text = f"{label}: {score}%"
            frame = cv2.putText(frame, label_text, (int(left), int(top - 10)), cv2.FONT_HERSHEY_SIMPLEX,
                                0.5, (255, 255, 255), 2)

    # Draw ROI if it exists
    if roi:
        pt1 = (int(roi[1] * frame.shape[1]), int(roi[0] * frame.shape[0]))
        pt2 = (int(roi[3] * frame.shape[1]), int(roi[2] * frame.shape[0]))
        frame = cv2.rectangle(frame, pt1, pt2, (255, 0, 0), 2)
        frame = cv2.putText(frame, f"Count: {count_people_in_roi}", (pt1[0], pt1[1] - 10), cv2.FONT_HERSHEY_SIMPLEX,
                            0.5, (255, 0, 0), 2)

    return frame
