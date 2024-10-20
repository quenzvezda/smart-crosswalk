import socket
import threading
from setup_led import pejalan_kaki_kiri, pejalan_kaki_kanan, mobil
from pedestrian import handle_pedestrian_crossing
import logging
import configparser

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('server')

# Initialize ConfigParser
config = configparser.ConfigParser()
config.read('config.ini')

crossing_flag = threading.Event()
zebra_cross_flag = threading.Event()
server_socket = None

def start_server():
    global server_socket
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    host = config.get('Server', 'host')  # Read from config
    port = config.getint('Server', 'port')  # Read from config
    server_socket.bind((host, port))
    server_socket.listen(1)  # Can handle up to 1 queued connection
    logger.info(f"Menunggu koneksi dari laptop/desktop di {host}:{port}...")

def traffic_light_cycle():
    mobil['hijau'].on()
    pejalan_kaki_kiri['merah'].on()
    pejalan_kaki_kanan['merah'].on()
    logger.info("Lampu Mobil Hijau, Pejalan Kaki Merah")
    try:
        start_server()
        while True:
            client_socket, addr = server_socket.accept()
            logger.info(f"Terhubung dengan {addr}")
            threading.Thread(target=handle_client, args=(client_socket,)).start()
    except KeyboardInterrupt:
        cleanup()

def handle_client(client_socket):
    global crossing_flag
    try:
        while True:
            data = client_socket.recv(1024).decode('utf-8')
            logger.info(data)
            if "Zebra Cross is Clear" in data:
                zebra_cross_flag.set()
            if crossing_flag.is_set():
                logger.info("Fungsi Pedestrian Sedang Berjalan - Data Diabaikan")
            else:
                if "Terdeteksi" in data:
                    parts = data.split(" ")
                    jumlah_orang = int(parts[1])
                    ada_mobil = "Dengan Mobil" in data

                    if ada_mobil:
                        delay_before_crossing = config.getint('Pedestrian', 'delay_before_crossing_with_vehicle')
                        logger.info("Terdeteksi {} Orang Dan (Mobil), Memulai Fungsi Pedestrian".format(jumlah_orang))
                    else:
                        delay_before_crossing = config.getint('Pedestrian', 'delay_before_crossing_without_vehicle')
                        logger.info("Terdeteksi {} Orang Dan (Tanpa Mobil), Memulai Fungsi Pedestrian".format(jumlah_orang))

                    crossing_flag.set()
                    client_socket.sendall("Pedestrian Process Started".encode('utf-8'))
                    threading.Thread(target=run_pedestrian_cycle, args=(client_socket, delay_before_crossing, jumlah_orang)).start()
    except Exception as e:
        logger.error(f"Error handling client: {e}")
    finally:
        client_socket.close()

def run_pedestrian_cycle(client_socket, delay_before_crossing, jumlah_orang):
    handle_pedestrian_crossing(crossing_flag, delay_before_crossing, jumlah_orang, zebra_cross_flag, client_socket)
    client_socket.sendall("Pedestrian Process Finished".encode('utf-8'))
    crossing_flag.clear()

def cleanup():
    for led in mobil.values():
        led.close()
    for led in pejalan_kaki_kiri.values():
        led.close()
    for led in pejalan_kaki_kanan.values():
        led.close()
    if server_socket:
        server_socket.close()
    logger.info("Program dihentikan, pin GPIO dibersihkan.")

# Run the traffic light cycle
traffic_light_cycle()
