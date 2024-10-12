import cv2
import numpy as np
from utils import calculate_overlap


def process_frame(frame, model, roi=None, estimate_distance=False, distance_estimator=None):
    # Run inference
    results = model(frame)

    count_people_in_roi = 0
    vehicle_detected = None  # Initialize to None

    # Convert ROI from normalized to pixel coordinates
    if roi:
        roi_pixel = [roi[0] * frame.shape[0], roi[1] * frame.shape[1], roi[2] * frame.shape[0], roi[3] * frame.shape[1]]  # [ymin, xmin, ymax, xmax]

    for result in results:
        boxes = result.boxes.xyxy.cpu().numpy()  # [N, 4], (x1, y1, x2, y2)
        scores = result.boxes.conf.cpu().numpy()
        classes = result.boxes.cls.cpu().numpy().astype(int)

        for i in range(len(scores)):
            if scores[i] > 0.5:
                x1, y1, x2, y2 = boxes[i]
                class_id = classes[i]
                label = model.names.get(class_id, 'Unknown')

                # Debug print to check detected classes
                # print(f"Detected class_id: {class_id}, label: {label}")

                left, top, right, bottom = x1, y1, x2, y2
                frame = cv2.rectangle(frame, (int(left), int(top)), (int(right), int(bottom)), (0, 255, 0), 2)
                label_text = f"{label}: {scores[i]*100:.2f}%"
                frame = cv2.putText(frame, label_text, (int(left), int(top - 10)), cv2.FONT_HERSHEY_SIMPLEX,
                                    0.5, (255, 255, 255), 2)

                # Create box in (ymin, xmin, ymax, xmax) format
                box = [top, left, bottom, right]

                # Count people in ROI if applicable
                if class_id == 1 and roi:
                    overlap = calculate_overlap(box, roi_pixel)
                    if overlap > 0.5:
                        count_people_in_roi += 1

                # Check for vehicle detection
                if class_id == 0 and estimate_distance and distance_estimator:
                    # Perform distance estimation
                    pixel_width = abs(right - left)
                    estimated_distance = distance_estimator.estimate(pixel_width)

                    if estimated_distance:
                        # Display estimated distance
                        distance_text = f"Jarak: {estimated_distance:.2f} m"
                        frame = cv2.putText(frame, distance_text, (int(left), int(top - 25)),
                                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

                        # Update vehicle_detected with the minimum distance
                        if vehicle_detected is None or estimated_distance < vehicle_detected:
                            vehicle_detected = estimated_distance

    # Draw ROI and display count and coordinates if ROI is defined
    if roi:
        pt1 = (int(roi[1] * frame.shape[1]), int(roi[0] * frame.shape[0]))
        pt2 = (int(roi[3] * frame.shape[1]), int(roi[2] * frame.shape[0]))
        frame = cv2.rectangle(frame, pt1, pt2, (0, 255, 255), 2)  # Change color here to yellow
        frame = cv2.putText(frame, f"Count: {count_people_in_roi}", (pt1[0], pt1[1] - 10), cv2.FONT_HERSHEY_SIMPLEX,
                            0.5, (0, 255, 255), 2)
        coord_text = f"({roi[1]:.2f}, {roi[0]:.2f}), ({roi[3]:.2f}, {roi[2]:.2f})"
        frame = cv2.putText(frame, coord_text, (pt1[0], frame.shape[0] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5,
                            (0, 255, 255), 2)

    return frame, count_people_in_roi, vehicle_detected
