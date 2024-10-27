import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter import ttk
from PIL import Image, ImageTk
import cv2
import os
import numpy as np
from ultralytics import YOLO
import tensorflow as tf


class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Aplikasi Inferensi Model")
        # Inisialisasi variabel
        self.model_selection = tk.StringVar()
        self.model_selection.set("YOLO")
        self.image_folder = "../data/image-test"
        self.image_list = []
        self.selected_image = None
        self.model_loaded = None
        self.yolo_model = None
        self.ssd_model = None
        self.infer_function = None
        self.root.geometry("800x600")

        # Bangun GUI
        self.build_gui()

    def build_gui(self):
        # Dropdown untuk pemilihan model
        model_label = tk.Label(self.root, text="Pilih Model:")
        model_label.pack(pady=5)
        model_dropdown = ttk.Combobox(self.root, textvariable=self.model_selection, values=["YOLO", "SSD"])
        model_dropdown.pack(pady=5)

        # Tombol untuk memilih folder
        folder_button = tk.Button(self.root, text="Pilih Folder Gambar", command=self.select_folder)
        folder_button.pack(pady=5)

        # Listbox untuk menampilkan gambar
        self.image_listbox = tk.Listbox(self.root, height=10)
        self.image_listbox.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        self.image_listbox.bind('<<ListboxSelect>>', self.on_image_select)

        # Label untuk menampilkan gambar yang dipilih
        self.image_label = tk.Label(self.root)
        self.image_label.pack(pady=5)

        # Tombol untuk melakukan inferensi
        infer_button = tk.Button(self.root, text="Jalankan Inferensi", command=self.run_inference)
        infer_button.pack(pady=5)

        # Label untuk menampilkan hasil inferensi
        self.result_label = tk.Label(self.root)
        self.result_label.pack(pady=5)

    def select_folder(self):
        folder_selected = filedialog.askdirectory(initialdir=self.image_folder, title="Pilih Folder Gambar")
        if folder_selected:
            self.image_folder = folder_selected
            self.load_images()

    def load_images(self):
        # Daftar gambar dalam folder
        self.image_list = [f for f in os.listdir(self.image_folder) if
                           f.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp'))]
        self.image_listbox.delete(0, tk.END)
        for img_name in self.image_list:
            self.image_listbox.insert(tk.END, img_name)

    def on_image_select(self, event):
        selection = event.widget.curselection()
        if selection:
            index = selection[0]
            img_name = self.image_listbox.get(index)
            self.selected_image = os.path.join(self.image_folder, img_name)
            self.display_image(self.selected_image)

    def display_image(self, image_path):
        # Buka gambar dan ubah ukurannya untuk ditampilkan
        img = Image.open(image_path)
        img.thumbnail((400, 400))
        self.photo = ImageTk.PhotoImage(img)
        self.image_label.config(image=self.photo)
        self.image_label.image = self.photo  # Simpan referensi

    def run_inference(self):
        if not self.selected_image:
            messagebox.showwarning("Peringatan", "Silakan pilih gambar.")
            return
        model_name = self.model_selection.get()
        if model_name == "YOLO":
            self.load_yolo_model()
            self.run_yolo_inference()
        elif model_name == "SSD":
            self.load_ssd_model()
            self.run_ssd_inference()

    def load_yolo_model(self):
        if self.yolo_model is None:
            model_path = '../models/trisakti-yolov8m-roboflow.pt'
            self.yolo_model = YOLO(model_path)

    def load_ssd_model(self):
        if self.ssd_model is None:
            model_path = '../models/ssd-new-dataset'
            self.ssd_model = tf.saved_model.load(model_path)
            self.infer_function = self.ssd_model.signatures['serving_default']

    def run_yolo_inference(self):
        # Baca gambar
        frame = cv2.imread(self.selected_image)
        if frame is None:
            messagebox.showerror("Error", "Gagal membaca gambar.")
            return
        # Jalankan inferensi
        results = self.yolo_model(frame)
        # Proses hasil
        for result in results:
            boxes = result.boxes.xyxy.cpu().numpy()
            scores = result.boxes.conf.cpu().numpy()
            classes = result.boxes.cls.cpu().numpy().astype(int)
            for i in range(len(scores)):
                if scores[i] > 0.5:
                    x1, y1, x2, y2 = boxes[i]
                    class_id = classes[i]
                    label = self.yolo_model.names.get(class_id, 'Unknown')
                    # Gambar bounding box
                    cv2.rectangle(frame, (int(x1), int(y1)), (int(x2), int(y2)), (0, 255, 0), 2)
                    label_text = f"{label}: {scores[i] * 100:.2f}%"
                    cv2.putText(frame, label_text, (int(x1), int(y1) - 10), cv2.FONT_HERSHEY_SIMPLEX,
                                0.5, (255, 255, 255), 2)
        # Tampilkan hasil
        self.display_result(frame)

    def run_ssd_inference(self):
        # Baca gambar
        frame = cv2.imread(self.selected_image)
        if frame is None:
            messagebox.showerror("Error", "Gagal membaca gambar.")
            return
        # Preprocessing gambar
        resized_frame = cv2.resize(frame, (640, 640))
        rgb_frame = cv2.cvtColor(resized_frame, cv2.COLOR_BGR2RGB)
        input_tensor = np.expand_dims(rgb_frame, axis=0)
        # Jalankan inferensi
        output_dict = self.infer_function(input_tensor=tf.constant(input_tensor))
        # Ekstrak hasil
        boxes = output_dict['detection_boxes'][0].numpy()
        scores = output_dict['detection_scores'][0].numpy()
        classes = output_dict['detection_classes'][0].numpy().astype(int)
        # Pemetaan label kelas
        class_labels = {1: 'mobil', 2: 'orang'}
        # Gambar hasil
        for i in range(len(scores)):
            if scores[i] > 0.5:
                box = boxes[i]
                class_id = classes[i]
                label = class_labels.get(class_id, 'Unknown')
                ymin, xmin, ymax, xmax = box
                x1, y1 = int(xmin * frame.shape[1]), int(ymin * frame.shape[0])
                x2, y2 = int(xmax * frame.shape[1]), int(ymax * frame.shape[0])
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                label_text = f"{label}: {scores[i] * 100:.2f}%"
                cv2.putText(frame, label_text, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX,
                            0.5, (255, 255, 255), 2)
        # Tampilkan hasil
        self.display_result(frame)

    def display_result(self, frame):
        # Konversi BGR ke RGB
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        # Konversi ke PIL Image
        img = Image.fromarray(frame)
        img.thumbnail((400, 400))
        self.result_photo = ImageTk.PhotoImage(img)
        self.result_label.config(image=self.result_photo)
        self.result_label.image = self.result_photo  # Simpan referensi


if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()
