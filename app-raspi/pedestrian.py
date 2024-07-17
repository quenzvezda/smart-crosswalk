from time import sleep, time
import threading
import logging
from playsound import playsound
from setup_led import pejalan_kaki_kiri, pejalan_kaki_kanan, mobil

logger = logging.getLogger('pedestrian')


def play_audio(file_path):
    playsound(file_path)


def print_status_with_countdown(message, countdown):
    for i in range(countdown, 0, -1):
        logger.info(f"{message} dalam waktu {i} detik")
        sleep(1)


def handle_pedestrian_crossing(client_socket, crossing_flag, delay_before_crossing, jumlah_orang, zebra_cross_flag):
    # Play the initial waiting audio
    initial_audio_thread = threading.Thread(target=play_audio, args=("sound/mohon-tunggu.mp3",))
    initial_audio_thread.start()
    logger.info("Suara diputar: mohon-tunggu.mp3")

    if jumlah_orang <= 3:
        lampu_hijau_duration = 10
    elif jumlah_orang <= 6:
        lampu_hijau_duration = 15
    else:
        lampu_hijau_duration = 20

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

    # Play the crossing audio
    crossing_audio_thread = threading.Thread(target=play_audio, args=("sound/silakan.mp3",))
    crossing_audio_thread.start()
    logger.info("Suara diputar: silakan.mp3")

    print_status_with_countdown("Lampu pejalan kaki akan merah", lampu_hijau_duration)

    # Countdown logic to check zebra_cross_flag
    max_wait_time = 30
    start_time = time()
    remaining_time = max_wait_time - lampu_hijau_duration

    while time() - start_time < remaining_time:
        if zebra_cross_flag.is_set():
            break
        sleep(0.1)

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
