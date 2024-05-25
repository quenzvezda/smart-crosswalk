import socket
import tkinter as tk


def send_command():
    try:
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        host = '192.168.2.14'  # IP Raspberry Pi
        port = 12345
        client_socket.connect((host, port))
        client_socket.sendall("Terdeteksi Orang Di Penyebrangan".encode('utf-8'))
        client_socket.close()
    except Exception as e:
        print(f"Error: {e}")


app = tk.Tk()
app.title("Traffic Control Simulator")
button = tk.Button(app, text="Orang Menyebrang", command=send_command)
button.pack(pady=20)

app.mainloop()
