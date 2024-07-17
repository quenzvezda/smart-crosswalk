from time import sleep, time
import threading
import logging
from playsound import playsound
from setup_led import pejalan_kaki_kiri, pejalan_kaki_kanan, mobil

logger = logging.getLogger('pedestrian')


def play_audio(file_name):
    file_path = f"sound/{file_name}"
    audio_thread = threading.Thread(target=playsound, args=(file_path,))
    audio_thread.start()
    logger.info(f"Suara diputar: {file_name}")


def print_status_with_countdown(message, countdown):
    for i in range(countdown, 0, -1):
        logger.info(f"{message} dalam waktu {i} detik")
        sleep(1)


def car_green_to_red():
    mobil['hijau'].off()
    mobil['kuning'].on()
    logger.info("Lampu Mobil Kuning, Pejalan Kaki Merah")
    sleep(2)

    mobil['kuning'].off()
    mobil['merah'].on()
    logger.info("Lampu Mobil Merah, Pejalan Kaki Merah")
    sleep(1)


def cross_red_to_green():
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


def cross_green_to_red():
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


def car_red_to_green():
    mobil['merah'].off()
    mobil['kuning'].on()
    logger.info("Lampu Mobil Kuning, Pejalan Kaki Merah")
    sleep(2)

    mobil['kuning'].off()
    mobil['hijau'].on()
    logger.info("Lampu Mobil Hijau, Pejalan Kaki Merah")


def wait_crossing_clear(max_wait_time, lampu_hijau_duration, zebra_cross_flag):
    start_time = time()
    remaining_time = max_wait_time - lampu_hijau_duration

    # Initialize last log time
    last_log_time = start_time
    remaining_log_time = remaining_time

    while time() - start_time < remaining_time:
        current_time = time()
        if zebra_cross_flag.is_set():
            break
        if current_time - last_log_time >= 1:
            remaining_log_time -= 1
            logger.info(f"[Crossing Not Clear] Lampu pejalan kaki akan merah dalam waktu {remaining_log_time} detik")
            last_log_time = current_time
        sleep(0.1)


def handle_pedestrian_crossing(crossing_flag, delay_before_crossing, jumlah_orang, zebra_cross_flag):
    # Play the initial waiting audio
    play_audio("mohon-tunggu.mp3")

    if jumlah_orang <= 3:
        lampu_hijau_duration = 10
    elif jumlah_orang <= 6:
        lampu_hijau_duration = 15
    else:
        lampu_hijau_duration = 20

    print_status_with_countdown("Lampu pejalan kaki akan hijau", delay_before_crossing)

    # [Mobil] Hijau -> Kuning -> Hijau
    car_green_to_red()

    # [Penyeberangan] Merah -> Kuning -> Hijau
    cross_red_to_green()

    # Play the crossing audio
    play_audio("silakan.mp3")

    print_status_with_countdown("Lampu pejalan kaki akan merah", lampu_hijau_duration)

    # Countdown logic to check zebra_cross_flag
    max_wait_time = 30
    wait_crossing_clear(max_wait_time, lampu_hijau_duration, zebra_cross_flag)

    # Lampu [Penyeberangan] Hijau -> Kuning -> Merah
    cross_green_to_red()

    # Lampu [Mobil] Merah -> Kuning -> Hijau
    car_red_to_green()

    crossing_flag.clear()
