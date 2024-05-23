from ultralytics import YOLO
import cv2
import math
import threading

# Load model
model = YOLO("../models/trisakti-batch_1-yolov8s-roboflow.pt")
model.to('cuda')

# Object classes
classNames = ["mobil", "pejalan kaki"]

# Set a confidence threshold
confidence_threshold = 0.5


def process_webcam(index, flip=False):
    # Start webcam
    cap = cv2.VideoCapture(index)
    cap.set(3, 640)  # Width
    cap.set(4, 480)  # Height

    while True:
        success, img = cap.read()
        if not success:
            break

        # Flip the image if required
        if flip:
            img = cv2.flip(img, -1)  # Flip vertically and horizontally

        results = model(img, stream=True)

        # Process each result
        for r in results:
            boxes = r.boxes

            for box in boxes:
                # Extract bounding box coordinates
                x1, y1, x2, y2 = box.xyxy[0]
                x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)  # Convert to integer

                # Calculate confidence
                conf = math.ceil(box.conf[0] * 100) / 100

                if conf >= confidence_threshold:
                    # Draw bounding box on the image
                    cv2.rectangle(img, (x1, y1), (x2, y2), (255, 0, 255), 3)
                    print("Confidence --->", conf)

                    # Get class ID and name
                    cls = int(box.cls[0])
                    print("Class name -->", classNames[cls])

                    # Label the object
                    org = (x1, y1)
                    font = cv2.FONT_HERSHEY_SIMPLEX
                    fontScale = 1
                    color = (255, 0, 0)
                    thickness = 2
                    cv2.putText(img, f"{classNames[cls]} {conf:.2f}", org, font, fontScale, color, thickness)

        # Display the image with detections
        cv2.imshow(f'Webcam {index}', img)
        if cv2.waitKey(1) == ord('q'):
            break

    # Release resources
    cap.release()
    cv2.destroyAllWindows()


# Create threads for each webcam
thread1 = threading.Thread(target=process_webcam, args=(0, True))  # Only flip webcam 0
thread2 = threading.Thread(target=process_webcam, args=(1,))
thread3 = threading.Thread(target=process_webcam, args=(2,))

# Start threads
thread1.start()
thread2.start()
thread3.start()

# Join threads to the main thread
thread1.join()
thread2.join()
thread3.join()
