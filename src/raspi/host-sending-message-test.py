import socket
import tkinter as tk
from threading import Thread

isProcessRun = False

def send_command():
    global isProcessRun
    if not isProcessRun:
        try:
            client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            host = '192.168.2.14'  # IP Raspberry Pi
            port = 12345
            client_socket.connect((host, port))
            client_socket.sendall("Terdeteksi Orang Di Penyebrangan".encode('utf-8'))
            Thread(target=receive_response, args=(client_socket,)).start()
        except Exception as e:
            print(f"Error: {e}")
    else:
        print("Fungsi pedestrian sedang berjalan. Silahkan tunggu.")

def receive_response(client_socket):
    global isProcessRun
    try:
        while True:
            data = client_socket.recv(1024).decode('utf-8')
            if data == "Fungsi Pedestrian Sedang Berjalan":
                isProcessRun = True
                print("Fungsi pedestrian sedang berjalan. Silahkan tunggu.")
            elif data == "Fungsi Pedestrian Selesai":
                isProcessRun = False
                print("Fungsi pedestrian selesai. Anda dapat mengirim perintah lagi.")
            elif data == "Memulai Fungsi Pedestrian":
                isProcessRun = True
                print(data)
    except Exception as e:
        print(f"Error receiving response: {e}")
    finally:
        client_socket.close()

app = tk.Tk()
app.title("Traffic Control Simulator")
button = tk.Button(app, text="Orang Menyebrang", command=send_command)
button.pack(pady=20)

app.mainloop()
