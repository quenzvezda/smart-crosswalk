import tkinter as tk
from tkinter import ttk
import cv2
from PIL import Image, ImageTk
import torch

# Load model YOLO
model = torch.hub.load('ultralytics/yolov8', 'custom', path='best.ptn')  # Sesuaikan path
model.eval()

# Fungsi untuk melakukan deteksi objek
def detect_objects(img):
    results = model(img)
    return results.render()[0]

# Fungsi untuk mengambil frame dari webcam dan memprosesnya
def show_frame():
    _, frame = cap.read()
    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    frame = detect_objects(frame)
    img = Image.fromarray(frame)
    imgtk = ImageTk.PhotoImage(image=img)
    lmain.imgtk = imgtk
    lmain.configure(image=imgtk)
    lmain.after(10, show_frame)

# Fungsi untuk memilih kamera
def select_camera(event):
    global cap
    if cap is not None:
        cap.release()
    camera_index = camera_select.current()
    cap = cv2.VideoCapture(camera_index)
    show_frame()

# Setup GUI
root = tk.Tk()
root.title("Object Detection")

# Dropdown menu untuk memilih kamera
camera_options = [0, 1, 2]  # Contoh untuk indeks kamera
camera_select = ttk.Combobox(root, values=camera_options, width=15)
camera_select.grid(column=0, row=0, padx=10, pady=10)
camera_select.current(0)
camera_select.bind("<<ComboboxSelected>>", select_camera)

# Label untuk menampilkan gambar
lmain = tk.Label(root)
lmain.grid(column=0, row=1)

cap = cv2.VideoCapture(0)
show_frame()

root.mainloop()
