import socket
import threading
import time
import logging
import queue

logger = logging.getLogger('client')

# Create a queue for logging messages
log_queue = queue.Queue()

isProcessRun = False

def send_data_to_server(data):
    try:
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        host = '192.168.2.14'  # IP Raspberry Pi
        port = 12345
        client_socket.connect((host, port))
        client_socket.sendall(data.encode('utf-8'))
        client_socket.close()
        message = f"Mengirim data ke server: {data}"
        logger.info(message)
        log_message(message)
    except Exception as e:
        error_message = f"Error sending data to server: {e}"
        logger.error(error_message)
        log_message(error_message)

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
                    message = "Fungsi pedestrian selesai. Anda dapat mengirim perintah lagi."
                    logger.info(message)
                    log_message(message)
                client_socket.close()
            except Exception as e:
                error_message = f"Error checking server response: {e}"
                logger.error(error_message)
                log_message(error_message)

def log_message(message):
    log_queue.put(message)
