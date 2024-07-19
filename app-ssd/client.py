# server_communication.py
import datetime
import socket
import threading


class ServerConnection:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.socket = None
        self.connected = False
        self.is_pedestrian_running = False
        self.is_minimum_time_reached = False

    def connect(self):
        if not self.connected:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            try:
                self.socket.connect((self.host, self.port))
                self.connected = True
                print("Connected to server")
            except socket.error as e:
                print(f"Failed to connect to server: {e}")

    def send_data(self, message):
        if self.connected:
            try:
                self.socket.sendall(message.encode())
            except socket.error as e:
                print(f"Error sending data: {e}")

    def receive_data(self):
        while self.connected:
            try:
                data = self.socket.recv(1024).decode('utf-8')
                if "Pedestrian Process Finished" in data:
                    now = datetime.datetime.now()
                    timestamp = now.strftime("[%H:%M:%S.%f]")[:-3]
                    print(f"{timestamp}] Siklus lampu selesai. Anda dapat mengirim perintah lagi.")
                    self.is_pedestrian_running = False
                    self.is_minimum_time_reached = False
                elif "Pedestrian Process Started" in data:
                    self.is_pedestrian_running = True
                elif "Minimum Time is Reached" in data:
                    self.is_minimum_time_reached = True
            except socket.error as e:
                print(f"Error receiving data: {e}")
                break

    def start_receiving_thread(self):
        thread = threading.Thread(target=self.receive_data)
        thread.start()

    def close_connection(self):
        if self.connected:
            self.socket.close()
            self.connected = False
            print("Disconnected from server")
