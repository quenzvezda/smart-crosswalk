import numpy as np
import cv2

# Define object specific variables
dist = 0
focal = 502  # Focal length (adjust this based on camera calibration)
pixels = 0
width = 3.5  # Real object width in cm
camera_index = 0

# Function to calculate distance
def get_dist(rectangle_params, image):
    # Find the number of pixels covered by the object
    pixels = rectangle_params[1][0]
    print(f"Pixels covered: {pixels}")

    # Calculate distance using the known object width, focal length, and the number of pixels
    dist = (width * focal) / pixels
    print(f"Calculated Distance: {dist} cm")

    # Write distance on the image
    image = cv2.putText(image, 'Distance from Camera in CM:', org, font, 1, color, 2, cv2.LINE_AA)
    image = cv2.putText(image, str(round(dist, 2)) + " cm", (110, 50), font, fontScale, color, 1, cv2.LINE_AA)
    return image

# Start video capture
cap = cv2.VideoCapture(camera_index)

# Basic constants for OpenCV functions
kernel = np.ones((3, 3), 'uint8')
font = cv2.FONT_HERSHEY_SIMPLEX
org = (0, 20)
fontScale = 0.6
color = (0, 0, 255)  # Red color for the text
thickness = 2

cv2.namedWindow('Object Dist Measure', cv2.WINDOW_NORMAL)
cv2.resizeWindow('Object Dist Measure', 700, 600)

# Loop to capture video frames
while True:
    ret, img = cap.read()

    if not ret:
        print("Failed to capture image")
        break

    # Convert to HSV color space
    hsv_img = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

    # Predefined mask for yellow color detection
    lower_yellow = np.array([20, 100, 100])  # Lower bound of yellow
    upper_yellow = np.array([30, 255, 255])  # Upper bound of yellow

    # Create mask for yellow
    mask = cv2.inRange(hsv_img, lower_yellow, upper_yellow)

    # Remove extra noise from the mask
    d_img = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel, iterations=5)

    # Find contours
    cont, hei = cv2.findContours(d_img, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cont = sorted(cont, key=cv2.contourArea, reverse=True)[:1]  # Take the largest contour

    for cnt in cont:
        # Check contour area
        if 100 < cv2.contourArea(cnt) < 306000:
            # Draw a rectangle around the largest contour
            rect = cv2.minAreaRect(cnt)
            box = cv2.boxPoints(rect)
            box = np.int0(box)
            cv2.drawContours(img, [box], -1, (255, 0, 0), 3)

            # Calculate distance and display on the image
            img = get_dist(rect, img)

    # Show the final image
    cv2.imshow('Object Dist Measure', img)

    # Break the loop when 'q' key is pressed
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cv2.destroyAllWindows()
cap.release()
