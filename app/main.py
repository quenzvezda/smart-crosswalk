import tkinter as tk
from tkinter import scrolledtext
import threading
import queue
import time
from detector import detect_pedestrian, detect_vehicle
from region import mouse_callback

# Create a queue for logging messages
log_queue = queue.Queue()

# Global flags
pejalan_kaki_detected = {"kiri": False, "kanan": False}
vehicle_detected = {"detected": False, "last_checked": time.time()}

# Function to update the log
def update_log(log_widget):
    while True:
        try:
            message = log_queue.get(block=False)
            log_widget.config(state='normal')
            log_widget.insert(tk.END, message + '\n')
            log_widget.config(state='disabled')
            log_widget.yview(tk.END)
        except queue.Empty:
            pass
        time.sleep(0.1)

# Function to add log messages to the queue
def log_message(message):
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    log_queue.put(f"[{timestamp}]: {message}")

# Function to start the pedestrian and vehicle detection threads
def start_detection_threads(weights, device):
    threading.Thread(target=detect_pedestrian, args=(weights, device, "kiri", pejalan_kaki_detected, vehicle_detected, log_message)).start()
    threading.Thread(target=detect_pedestrian, args=(weights, device, "kanan", pejalan_kaki_detected, vehicle_detected, log_message)).start()
    threading.Thread(target=detect_vehicle, args=(weights, device, vehicle_detected, log_message)).start()

# Tkinter GUI
root = tk.Tk()
root.title("Traffic Control Simulator")

# Log display
log_display = scrolledtext.ScrolledText(root, width=80, height=20, state='disabled')
log_display.grid(row=1, column=1)

# Start the thread to update the log
threading.Thread(target=update_log, args=(log_display,)).start()

# Start detection threads
weights = "../models/trisakti-batch_1-yolov8s-roboflow.pt"
device = "0"
start_detection_threads(weights, device)

root.mainloop()
