from gpiozero import LED
from time import sleep
from playsound import playsound
import threading
from setup_led import pejalan_kaki_kiri, pejalan_kaki_kanan, mobil

def play_audio(file_path):
    playsound(file_path)

def handle_pedestrian_crossing(client_socket, send_response, crossing_flag, delay_before_crossing, audio_file):
    print("Orang terdeteksi, mengubah lampu menjadi merah")
    # Memutar audio informasi di thread terpisah
    audio_thread = threading.Thread(target=play_audio, args=(audio_file,))
    audio_thread.start()
    print("Suara diputar...")
    sleep(delay_before_crossing)

    # Lampu mobil kuning selama 2 detik
    mobil['hijau'].off()
    mobil['kuning'].on()
    print("Lampu Mobil Kuning, Pejalan Kaki Merah")
    sleep(2)

    # Lampu mobil merah, jeda 1 detik semua merah
    mobil['kuning'].off()
    mobil['merah'].on()
    print("Lampu Mobil Merah, Pejalan Kaki Merah")
    sleep(1)

    # Lampu pejalan kaki kuning selama 2 detik
    pejalan_kaki_kiri['kuning'].on()
    pejalan_kaki_kanan['kuning'].on()
    pejalan_kaki_kiri['merah'].off()
    pejalan_kaki_kanan['merah'].off()
    print("Lampu Mobil Merah, Pejalan Kaki Kuning")
    sleep(2)

    # Lampu pejalan kaki hijau selama 10 detik
    pejalan_kaki_kiri['kuning'].off()
    pejalan_kaki_kanan['kuning'].off()
    pejalan_kaki_kiri['hijau'].on()
    pejalan_kaki_kanan['hijau'].on()
    print("Lampu Mobil Merah, Pejalan Kaki Hijau")
    sleep(10)

    # Lampu pejalan kaki kuning selama 2 detik
    pejalan_kaki_kiri['hijau'].off()
    pejalan_kaki_kanan['hijau'].off()
    pejalan_kaki_kiri['kuning'].on()
    pejalan_kaki_kanan['kuning'].on()
    print("Lampu Mobil Merah, Pejalan Kaki Kuning")
    sleep(2)

    # Lampu pejalan kaki merah, jeda 1 detik semua merah
    pejalan_kaki_kiri['kuning'].off()
    pejalan_kaki_kanan['kuning'].off()
    pejalan_kaki_kiri['merah'].on()
    pejalan_kaki_kanan['merah'].on()
    print("Lampu Mobil Merah, Pejalan Kaki Merah")
    sleep(1)

    # Lampu mobil kuning selama 2 detik
    mobil['merah'].off()
    mobil['kuning'].on()
    print("Lampu Mobil Kuning, Pejalan Kaki Merah")
    sleep(2)

    # Lampu mobil hijau dan kembali ke siklus awal
    mobil['kuning'].off()
    mobil['hijau'].on()
    print("Lampu Mobil Hijau, Pejalan Kaki Merah")

    # Mengirim pesan ke client bahwa fungsi pedestrian selesai
    send_response(client_socket, "Fungsi Pedestrian Selesai")
    crossing_flag.clear()
