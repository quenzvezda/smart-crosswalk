import tkinter as tk
from tkinter import messagebox
import socket
import threading


class DummyClientUI:
    def __init__(self, master):
        self.master = master
        self.master.title("Dummy Client for Pedestrian and Vehicle Detection")
        self.master.geometry("480x480")

        self.server_ip_label = tk.Label(master, text="Server IP Address:")
        self.server_ip_label.pack()

        self.server_ip_entry = tk.Entry(master)
        self.server_ip_entry.pack()
        self.server_ip_entry.insert(0, "192.168.2.101")

        self.connect_button = tk.Button(master, text="Connect", command=self.connect_to_server)
        self.connect_button.pack()

        self.label = tk.Label(master, text="Jumlah Orang:")
        self.label.pack()

        self.jumlah_orang_entry = tk.Entry(master)
        self.jumlah_orang_entry.pack()
        self.jumlah_orang_entry.insert(0, "1")

        self.mobil_var = tk.BooleanVar()
        self.mobil_checkbox = tk.Checkbutton(master, text="Mobil Terdeteksi", variable=self.mobil_var)
        self.mobil_checkbox.pack()

        self.send_button = tk.Button(master, text="Kirim Data", command=self.send_data)
        self.send_button.pack()
        self.send_button.config(state=tk.DISABLED)  # Disabled until connected

        self.clear_button = tk.Button(master, text="Zebra Cross is Clear", command=self.send_clear_data)
        self.clear_button.pack()
        self.clear_button.config(state=tk.DISABLED)  # Disabled until conditions met

        self.quit_button = tk.Button(master, text="Keluar", command=master.quit)
        self.quit_button.pack()

        self.server_connection = None
        self.minimum_time_reached = False
        self.pedestrian_process_started = False

    def connect_to_server(self):
        server_ip = self.server_ip_entry.get()
        server_port = 60003

        self.server_connection = ServerConnection(server_ip, server_port, self)
        if self.server_connection.connect():
            messagebox.showinfo("Koneksi Berhasil", f"Terhubung ke server {server_ip}")
            self.send_button.config(state=tk.NORMAL)  # Enable send button
            threading.Thread(target=self.server_connection.listen_to_server).start()  # Start listening to server
        else:
            messagebox.showerror("Koneksi Gagal", f"Gagal terhubung ke server {server_ip}")

    def send_data(self):
        jumlah_orang = self.jumlah_orang_entry.get()
        mobil_terdeteksi = self.mobil_var.get()
        if not jumlah_orang.isdigit():
            messagebox.showerror("Input Error", "Jumlah orang harus berupa angka.")
            return

        data = f"Terdeteksi {jumlah_orang} Orang"
        if mobil_terdeteksi:
            data += " Di Penyebrangan (Dengan Mobil)"
        else:
            data += " Di Penyebrangan (Tanpa Mobil)"

        self.server_connection.send_data(data)
        messagebox.showinfo("Data Terkirim", f"Data terkirim ke server: {data}")

    def send_clear_data(self):
        data = "Zebra Cross is Clear"
        self.server_connection.send_data(data)
        messagebox.showinfo("Data Terkirim", f"Data terkirim ke server: {data}")
        self.clear_button.config(state=tk.DISABLED)  # Disable until conditions are met again

    def disable_send_button(self):
        self.send_button.config(state=tk.DISABLED)

    def enable_send_button(self):
        self.send_button.config(state=tk.NORMAL)

    def enable_clear_button(self):
        if self.pedestrian_process_started and self.minimum_time_reached:
            self.clear_button.config(state=tk.NORMAL)

    def set_pedestrian_process_started(self):
        self.pedestrian_process_started = True
        self.minimum_time_reached = False  # Reset minimum time reached
        self.clear_button.config(state=tk.DISABLED)  # Ensure clear button is disabled initially

    def set_minimum_time_reached(self):
        self.minimum_time_reached = True
        self.enable_clear_button()

    def set_pedestrian_process_finished(self):
        self.pedestrian_process_started = False
        self.minimum_time_reached = False
        self.clear_button.config(state=tk.DISABLED)


class ServerConnection:
    def __init__(self, host, port, ui):
        self.host = host
        self.port = port
        self.client_socket = None
        self.ui = ui

    def connect(self):
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.client_socket.connect((self.host, self.port))
            print("Terhubung ke server")
            return True
        except Exception as e:
            print(f"Gagal terhubung ke server: {e}")
            return False

    def send_data(self, data):
        try:
            self.client_socket.sendall(data.encode('utf-8'))
        except Exception as e:
            print(f"Error mengirim data: {e}")

    def listen_to_server(self):
        try:
            while True:
                data = self.client_socket.recv(1024).decode('utf-8')
                print(data)
                if "Pedestrian Process Started" in data:
                    self.ui.disable_send_button()
                    self.ui.set_pedestrian_process_started()
                elif "Minimum Time is Reached" in data:
                    self.ui.set_minimum_time_reached()
                elif "Pedestrian Process Finished" in data:
                    self.ui.enable_send_button()
                    self.ui.set_pedestrian_process_finished()
        except Exception as e:
            print(f"Error menerima data dari server: {e}")


def main():
    root = tk.Tk()
    app = DummyClientUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
