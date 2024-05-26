import socket
import threading
import time


def send_data_to_server(data):
    try:
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        host = '192.168.2.14'  # IP Raspberry Pi
        port = 12345
        client_socket.connect((host, port))
        client_socket.sendall(data.encode('utf-8'))
        client_socket.close()
    except Exception as e:
        print(f"Error sending data to server: {e}")


def monitor_server_response():
    global isProcessRun
    while True:
        time.sleep(1)  # adjust sleep time as necessary
        if isProcessRun:
            try:
                client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                host = '192.168.2.14'  # IP Raspberry Pi
                port = 12345
                client_socket.connect((host, port))
                client_socket.sendall("Check Status".encode('utf-8'))
                response = client_socket.recv(1024).decode('utf-8')
                if response == "Fungsi Pedestrian Selesai":
                    isProcessRun = False
                    print("Fungsi pedestrian selesai. Anda dapat mengirim perintah lagi.")
                client_socket.close()
            except Exception as e:
                print(f"Error checking server response: {e}")
