import socket
import threading
import logging
import time

logger = logging.getLogger('client')
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

server_address = ('192.168.2.14', 60003)
isProcessRun = False
lock = threading.Lock()
connected = False
client_socket = None


def connect_to_server():
    global client_socket, connected
    while not connected:
        try:
            client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client_socket.connect(server_address)
            connected = True
            logger.info("Terhubung ke server")
        except Exception as e:
            logger.error(f"Gagal menghubungkan ke server: {e}")
            time.sleep(5)  # Coba lagi setelah 5 detik


def send_data_to_server(data):
    global isProcessRun
    with lock:
        if isProcessRun:
            logger.info("Fungsi Pedestrian Sedang Berjalan. Tidak Mengirim Pesan . . .")
            return
    try:
        client_socket.sendall(data.encode('utf-8'))
        logger.info(f"Mengirim data ke server: {data}")
        response = client_socket.recv(1024).decode('utf-8')
        logger.info(f"Menerima Pesan dari Server: {response}")
        if response == "Pedestrian Process Started":
            with lock:
                isProcessRun = True
        elif response == "Pedestrian Process Finished":
            with lock:
                isProcessRun = False
    except Exception as e:
        logger.error(f"Error sending data to server: {e}")
        connect_to_server()


def monitor_server_response():
    global isProcessRun, connected
    while True:
        time.sleep(1)
        if isProcessRun:
            try:
                client_socket.sendall("Check Status".encode('utf-8'))
                response = client_socket.recv(1024).decode('utf-8')
                if response == "Pedestrian Process Finished":
                    with lock:
                        isProcessRun = False
                    logger.info("Fungsi pedestrian selesai. Anda dapat mengirim perintah lagi.")
            except Exception as e:
                logger.error(f"Error checking server response: {e}")
                connected = False
                connect_to_server()


# Start the thread to monitor server response
threading.Thread(target=monitor_server_response, daemon=True).start()
connect_to_server()
