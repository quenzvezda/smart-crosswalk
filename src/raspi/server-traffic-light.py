import socket
import threading
from setup_led import pejalan_kaki_kiri, pejalan_kaki_kanan, mobil
from pedestrian import handle_pedestrian_crossing

def traffic_light_cycle():
    try:
        while True:
            # Lampu mobil hijau selamanya sampai ada pejalan kaki
            mobil['hijau'].on()
            pejalan_kaki_kiri['merah'].on()
            pejalan_kaki_kanan['merah'].on()
            print("Lampu Mobil Hijau, Pejalan Kaki Merah")
            client_socket, addr = server_socket.accept()
            threading.Thread(target=handle_client, args=(client_socket, addr)).start()
    except KeyboardInterrupt:
        cleanup()

def handle_client(client_socket, addr):
    try:
        print(f"Terhubung dengan {addr}")
        data = client_socket.recv(1024).decode('utf-8')
        if data == "Terdeteksi Orang Di Penyebrangan":
            if crossing_flag.is_set():
                send_response(client_socket, "Fungsi Pedestrian Sedang Berjalan")
            else:
                send_response(client_socket, "Memulai Fungsi Pedestrian")
                crossing_flag.set()
                handle_pedestrian_crossing(client_socket, send_response, crossing_flag)
    except Exception as e:
        print(f"Error handling client: {e}")
    finally:
        client_socket.close()

def send_response(client_socket, message):
    try:
        client_socket.sendall(message.encode('utf-8'))
    except Exception as e:
        print(f"Error sending response: {e}")

def cleanup():
    for led in mobil.values():
        led.close()
    for led in pejalan_kaki_kiri.values():
        led.close()
    for led in pejalan_kaki_kanan.values():
        led.close()
    server_socket.close()
    print("Program dihentikan, pin GPIO dibersihkan.")

# Inisialisasi socket server
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
host = '0.0.0.0'  # IP Raspberry Pi
port = 12345
server_socket.bind((host, port))
server_socket.listen(5)  # Dapat menangani hingga 5 koneksi dalam antrian
print("Menunggu koneksi dari laptop/desktop...")

# Inisialisasi Flag untuk mengatur pejalan kaki
crossing_flag = threading.Event()

# Jalankan siklus lampu lalu lintas
traffic_light_cycle()
