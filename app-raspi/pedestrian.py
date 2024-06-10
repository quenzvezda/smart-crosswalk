from gpiozero import LED
from time import sleep
from playsound import playsound
import threading
import logging
from setup_led import pejalan_kaki_kiri, pejalan_kaki_kanan, mobil

logger = logging.getLogger('pedestrian')


def play_audio(file_path):
    playsound(file_path)


def print_status_with_countdown(message, countdown):
    for i in range(countdown, 0, -1):
        logger.info(f"{message} dalam waktu {i} detik")
        sleep(1)


def handle_pedestrian_crossing(client_socket, crossing_flag, delay_before_crossing, initial_audio_file,
                               crossing_audio_file):
    logger.info("Orang terdeteksi, mengubah lampu menjadi merah")

    if initial_audio_file:
        audio_thread = threading.Thread(target=play_audio, args=(initial_audio_file,))
        audio_thread.start()
        logger.info(f"Suara diputar: {initial_audio_file}")

    print_status_with_countdown("Lampu pejalan kaki akan hijau", delay_before_crossing)

    mobil['hijau'].off()
    mobil['kuning'].on()
    logger.info("Lampu Mobil Kuning, Pejalan Kaki Merah")
    sleep(2)

    mobil['kuning'].off()
    mobil['merah'].on()
    logger.info("Lampu Mobil Merah, Pejalan Kaki Merah")
    sleep(1)

    pejalan_kaki_kiri['kuning'].on()
    pejalan_kaki_kanan['kuning'].on()
    pejalan_kaki_kiri['merah'].off()
    pejalan_kaki_kanan['merah'].off()
    logger.info("Lampu Mobil Merah, Pejalan Kaki Kuning")
    sleep(2)

    pejalan_kaki_kiri['kuning'].off()
    pejalan_kaki_kanan['kuning'].off()
    pejalan_kaki_kiri['hijau'].on()
    pejalan_kaki_kanan['hijau'].on()
    logger.info("Lampu Mobil Merah, Pejalan Kaki Hijau")

    crossing_audio_thread = threading.Thread(target=play_audio, args=(crossing_audio_file,))
    crossing_audio_thread.start()

    print_status_with_countdown("Lampu pejalan kaki akan merah", 10)

    pejalan_kaki_kiri['hijau'].off()
    pejalan_kaki_kanan['hijau'].off()
    pejalan_kaki_kiri['kuning'].on()
    pejalan_kaki_kanan['kuning'].on()
    logger.info("Lampu Mobil Merah, Pejalan Kaki Kuning")
    sleep(2)

    pejalan_kaki_kiri['kuning'].off()
    pejalan_kaki_kanan['kuning'].off()
    pejalan_kaki_kiri['merah'].on()
    pejalan_kaki_kanan['merah'].on()
    logger.info("Lampu Mobil Merah, Pejalan Kaki Merah")
    sleep(1)

    mobil['merah'].off()
    mobil['kuning'].on()
    logger.info("Lampu Mobil Kuning, Pejalan Kaki Merah")
    sleep(2)

    mobil['kuning'].off()
    mobil['hijau'].on()
    logger.info("Lampu Mobil Hijau, Pejalan Kaki Merah")

    crossing_flag.clear()
