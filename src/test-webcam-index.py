# import cv2
#
# def detect_webcams():
#     index = 0
#     arr = []
#     while True:
#         cap = cv2.VideoCapture(index)
#         if not cap.read()[0]:
#             cap.release()
#             break
#         else:
#             arr.append(index)
#             cap.release()
#             index += 1
#     return arr
#
# webcams = detect_webcams()
# for idx in webcams:
#     print(f"Webcam Index: {idx}")

##############

# import win32com.client
#
# def list_video_devices():
#     wmi = win32com.client.GetObject("winmgmts:")
#     devices = wmi.InstancesOf("Win32_PnPEntity")
#     video_devices = [device.Name for device in devices if device.Name and ('camera' in device.Name.lower() or 'webcam' in device.Name.lower())]
#     return video_devices
#
# # Menampilkan daftar webcam
# webcams = list_video_devices()
# if webcams:
#     for webcam in webcams:
#         print(f"Webcam Device Name: {webcam}")
# else:
#     print("No webcams found.")

###############

# import cv2
# import win32com.client
#
# def list_video_devices():
#     wmi = win32com.client.GetObject("winmgmts:")
#     devices = wmi.InstancesOf("Win32_PnPEntity")
#     video_devices = [device.Name for device in devices if device.Name and ('camera' in device.Name.lower() or 'webcam' in device.Name.lower()) and 'microphone' not in device.Name.lower()]
#     return video_devices
#
# def match_webcams_to_indices(video_devices):
#     index = 0
#     matched_devices = []
#     while True:
#         cap = cv2.VideoCapture(index)
#         if not cap.read()[0]:
#             cap.release()
#             break
#         else:
#             # Kita tidak bisa mendapatkan nama perangkat dari OpenCV, jadi kita hanya mengasumsikan urutan
#             if index < len(video_devices):
#                 matched_devices.append((index, video_devices[index]))
#             else:
#                 matched_devices.append((index, "Unknown device"))
#             cap.release()
#         index += 1
#     return matched_devices
#
# # Daftar nama perangkat video yang tidak termasuk microphone
# video_devices = list_video_devices()
#
# # Cocokkan indeks OpenCV dengan nama perangkat
# webcam_matches = match_webcams_to_indices(video_devices)
# for webcam in webcam_matches:
#     print(f"OpenCV Index: {webcam[0]}, Device Name: {webcam[1]}")


#############

import cv2

def capture_images_from_webcams():
    index = 0
    while True:
        cap = cv2.VideoCapture(index)
        ret, frame = cap.read()
        if not ret:
            cap.release()
            break
        else:
            cv2.imwrite(f"webcam_{index}.jpg", frame)
            print(f"Captured image from webcam index: {index}")
        cap.release()
        index += 1

capture_images_from_webcams()

##############