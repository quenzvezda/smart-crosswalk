import socket
import threading
from setup_led import pejalan_kaki_kiri, pejalan_kaki_kanan, mobil
from pedestrian import handle_pedestrian_crossing
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('server')

crossing_flag = threading.Event()
lock = threading.Lock()
server_socket = None


def start_server():
    global server_socket
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    host = '0.0.0.0'  # IP Raspberry Pi
    port = 60003
    server_socket.bind((host, port))
    server_socket.listen(1)  # Dapat menangani hingga 1 koneksi dalam antrian
    logger.info("Menunggu koneksi dari laptop/desktop...")


def traffic_light_cycle():
    try:
        start_server()
        while True:
            mobil['hijau'].on()
            pejalan_kaki_kiri['merah'].on()
            pejalan_kaki_kanan['merah'].on()
            logger.info("Lampu Mobil Hijau, Pejalan Kaki Merah")

            client_socket, addr = server_socket.accept()
            logger.info(f"Terhubung dengan {addr}")
            handle_client(client_socket)
    except KeyboardInterrupt:
        cleanup()


def handle_client(client_socket):
    global crossing_flag
    try:
        while True:
            data = client_socket.recv(1024).decode('utf-8')
            if crossing_flag.is_set():
                logger.info("Fungsi Pedestrian Sedang Berjalan - Data Diabaikan")
            else:
                if "Terdeteksi Orang Di Penyebrangan (Dengan Mobil)" in data:
                    logger.info("Memulai Fungsi Pedestrian (Dengan Mobil)")
                    crossing_flag.set()
                    client_socket.sendall("Pedestrian Process Started".encode('utf-8'))
                    handle_pedestrian_crossing(client_socket, crossing_flag, 10, "sound/tunggu-10d.mp3",
                                               "sound/silakan.mp3")
                elif "Terdeteksi Orang Di Penyebrangan (Tanpa Mobil)" in data:
                    logger.info("Memulai Fungsi Pedestrian (Tanpa Mobil)")
                    crossing_flag.set()
                    client_socket.sendall("Pedestrian Process Started".encode('utf-8'))
                    handle_pedestrian_crossing(client_socket, crossing_flag, 0, None, "sound/silakan.mp3")
            client_socket.sendall("Pedestrian Process Finished".encode('utf-8'))
            crossing_flag.clear()
    except Exception as e:
        logger.error(f"Error handling client: {e}")
    finally:
        client_socket.close()


def cleanup():
    for led in mobil.values():
        led.close()
    for led in pejalan_kaki_kiri.values():
        led.close()
    for led in pejalan_kaki_kanan.values():
        led.close()
    server_socket.close()
    logger.info("Program dihentikan, pin GPIO dibersihkan.")


# Inisialisasi socket server
start_server()

# Jalankan siklus lampu lalu lintas
traffic_light_cycle()
