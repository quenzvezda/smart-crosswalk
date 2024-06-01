from gpiozero import LED
from time import sleep
from playsound import playsound
import threading
from setup_led import pejalan_kaki_kiri, pejalan_kaki_kanan, mobil


def play_audio(file_path):
    playsound(file_path)


def handle_pedestrian_crossing(client_socket, crossing_flag, delay_before_crossing, initial_audio_file,
                               crossing_audio_file):
    print("Orang terdeteksi, mengubah lampu menjadi merah")

    if initial_audio_file:
        audio_thread = threading.Thread(target=play_audio, args=(initial_audio_file,))
        audio_thread.start()
        print("Suara diputar: ", initial_audio_file)

    sleep(delay_before_crossing)

    mobil['hijau'].off()
    mobil['kuning'].on()
    print("Lampu Mobil Kuning, Pejalan Kaki Merah")
    sleep(2)

    mobil['kuning'].off()
    mobil['merah'].on()
    print("Lampu Mobil Merah, Pejalan Kaki Merah")
    sleep(1)

    pejalan_kaki_kiri['kuning'].on()
    pejalan_kaki_kanan['kuning'].on()
    pejalan_kaki_kiri['merah'].off()
    pejalan_kaki_kanan['merah'].off()
    print("Lampu Mobil Merah, Pejalan Kaki Kuning")
    sleep(2)

    pejalan_kaki_kiri['kuning'].off()
    pejalan_kaki_kanan['kuning'].off()
    pejalan_kaki_kiri['hijau'].on()
    pejalan_kaki_kanan['hijau'].on()
    print("Lampu Mobil Merah, Pejalan Kaki Hijau")

    crossing_audio_thread = threading.Thread(target=play_audio, args=(crossing_audio_file,))
    crossing_audio_thread.start()
    sleep(10)

    pejalan_kaki_kiri['hijau'].off()
    pejalan_kaki_kanan['hijau'].off()
    pejalan_kaki_kiri['kuning'].on()
    pejalan_kaki_kanan['kuning'].on()
    print("Lampu Mobil Merah, Pejalan Kaki Kuning")
    sleep(2)

    pejalan_kaki_kiri['kuning'].off()
    pejalan_kaki_kanan['kuning'].off()
    pejalan_kaki_kiri['merah'].on()
    pejalan_kaki_kanan['merah'].on()
    print("Lampu Mobil Merah, Pejalan Kaki Merah")
    sleep(1)

    mobil['merah'].off()
    mobil['kuning'].on()
    print("Lampu Mobil Kuning, Pejalan Kaki Merah")
    sleep(2)

    mobil['kuning'].off()
    mobil['hijau'].on()
    print("Lampu Mobil Hijau, Pejalan Kaki Merah")

    crossing_flag.clear()
