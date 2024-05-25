import socket
from gpiozero import LED
from time import sleep

led = LED(23)  # Misalnya menggunakan pin 17 untuk LED
led1 = LED(22)

# Inisialisasi socket server
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
host = '192.168.2.14'  # IP Raspberry Pi
port = 12345
server_socket.bind((host, port))
server_socket.listen(1)
print("Menunggu koneksi dari laptop/desktop...")

def handle_traffic_signal(command):
    if command == "Terdeteksi Orang Di Penyebrangan":
        print("Orang terdeteksi, mengubah lampu menjadi merah")
        led.off()  # Hijau OFF
        led1.on()
        sleep(10)  # Countdown 10 detik
        led.on()   # Merah ON
        led1.off()
        sleep(5)  # Lampu merah selama 30 detik
        led.off()  # Kembali ke Hijau
        print("Waktu habis, mengubah lampu menjadi hijau")

while True:
    client_socket, addr = server_socket.accept()
    try:
        print(f"Terhubung dengan {addr}")
        while True:
            data = client_socket.recv(1024).decode('utf-8')
            if data:
                print(f"Data diterima: {data}")
                handle_traffic_signal(data)
            else:
                break
    finally:
        client_socket.close()

