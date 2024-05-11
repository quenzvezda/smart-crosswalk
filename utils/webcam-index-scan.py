import tkinter as tk
from tkinter import ttk
import cv2
from PIL import Image, ImageTk
import os
import shutil


# Fungsi untuk menghapus dan membuat folder baru
def prepare_folder(folder_path):
    if os.path.exists(folder_path):
        shutil.rmtree(folder_path)  # Hapus folder jika sudah ada
    os.makedirs(folder_path)  # Buat folder baru


# Fungsi untuk menangkap gambar dari webcam
def capture_images_from_webcams():
    folder_path = "../temp/web_scan"  # Path relatif dari folder /utils
    prepare_folder(folder_path)  # Persiapkan folder

    index = 0
    images = {}
    while True:
        cap = cv2.VideoCapture(index)  # Menggunakan backend default
        ret, frame = cap.read()
        if not ret:
            cap.release()
            break
        else:
            image_path = os.path.join(folder_path, f"webcam_{index}.jpg")
            cv2.imwrite(image_path, frame)
            images[index] = image_path
        cap.release()
        index += 1
    return images


# Fungsi untuk memperbarui GUI dengan gambar webcam
def update_gui(window, frame_container):
    for widget in frame_container.winfo_children():
        widget.destroy()

    images = capture_images_from_webcams()
    row = 0
    col = 0
    for index, image_file in images.items():
        if col >= 4:  # Setelah 4 gambar, mulai baris baru
            row += 1
            col = 0
        img = Image.open(image_file)
        img.thumbnail((160, 120), Image.Resampling.LANCZOS)
        photo = ImageTk.PhotoImage(img)

        frame = ttk.Frame(frame_container)
        frame.grid(row=row, column=col, padx=5, pady=5)

        label = ttk.Label(frame, text=f"Index: {index}")
        label.pack(side="top")

        canvas = tk.Canvas(frame, width=160, height=120)
        canvas.pack(side="top")
        canvas.create_image(0, 0, anchor="nw", image=photo)
        canvas.image = photo  # Keep a reference to avoid garbage collection

        col += 1


# Membuat GUI utama
def create_gui():
    window = tk.Tk()
    window.title("Webcam Scanner")
    window.geometry("695x300")  # Ukuran default

    frame_container = ttk.Frame(window)
    frame_container.pack(fill="both", expand=True)

    scan_button = ttk.Button(window, text="Scan Webcams", command=lambda: update_gui(window, frame_container))
    scan_button.pack(side="bottom", fill="x")

    window.mainloop()


create_gui()
