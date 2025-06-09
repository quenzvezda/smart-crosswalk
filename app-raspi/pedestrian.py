from time import sleep, time
import threading
import logging
from playsound import playsound
import configparser
from setup_led import pejalan_kaki_kiri, pejalan_kaki_kanan, mobil

logger = logging.getLogger('pedestrian')

# --- MULAI: BACA CONFIG.INI ---
config = configparser.ConfigParser()
config.read('config.ini')

# Ambil nilai-nilai audio dari config
wait_audio_file = config.get('Audio', 'wait_audio')    # e.g. "sound/mohon-tunggu.mp3"
go_audio_file   = config.get('Audio', 'go_audio')      # e.g. "sound/silakan.mp3"
beep_audio_file = config.get('Audio', 'beep_audio')    # e.g. "sound/beep.wav"
beep_duration   = config.getfloat('Audio', 'beep_duration', fallback=2.0)
# --- SELESAI: BACA CONFIG.INI ---


def play_sound(file_path: str, duration: float = None):
    """
    Memutar file audio:
      - Jika duration=None, mainkan sekali (blocking di thread itu sendiri).
      - Jika duration=angka, loop memutar file tersebut hingga total waktu ≈ duration detik.
    Pemanggilan fungsi ini akan selalu spawn sebuah daemon thread, jadi tidak akan memblok
    eksekusi di thread pemanggil.
    """
    def _worker():
        if duration is None:
            # Cukup mainkan sekali
            playsound(file_path)
        else:
            # Loop memutar hingga waktu >= duration
            end_time = time() + duration
            while time() < end_time:
                playsound(file_path)

    # Jalankan _worker di thread terpisah agar non-blocking
    t = threading.Thread(target=_worker, daemon=True)
    t.start()
    logger.info(f"Suara diputar (file={file_path}, durasi={'once' if duration is None else duration})")


def print_status_with_countdown(message: str, countdown: int):
    """
    Log setiap detik: "<message> dalam waktu {i} detik"
    """
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


def wait_crossing_clear(max_wait_time: int, lampu_hijau_duration: int, zebra_cross_flag):
    """
    Tunggu hingga zebra_cross_flag.set() atau hingga "waktu total = max_wait_time".
    - Setelah minimum hijau terpenuhi (lampu_hijau_duration), mulai hitung sisa waktu.
    - Jika zebra_cross_flag.set() sebelum timeout:
        • Putar beep selama beep_duration detik (non-blocking) lalu tunggu 2 detik sebelum break.
    - Jika zebra_cross_flag TIDAK diset hingga mendekati timeout (≤ beep_duration):
        • Putar beep selama beep_duration detik (non-blocking), tapi tidak menunda break.
    Logging setiap detik jika belum clear.
    """
    start_time  = time()
    total_wait   = max_wait_time - lampu_hijau_duration
    last_log     = start_time
    remaining    = total_wait
    beep_played  = False  # pastikan beep hanya sekali

    while True:
        now       = time()
        elapsed   = now - start_time
        time_left = total_wait - elapsed

        # Skenario 1: area sudah clear sebelum timeout
        if zebra_cross_flag.is_set():
            # Putar beep selama beep_duration, tunggu 2 detik sebelum break
            play_sound(beep_audio_file, duration=beep_duration)
            sleep(beep_duration)
            break

        # Skenario 2: mendekati timeout (≤ beep_duration tersisa), beep sekali
        if not beep_played and time_left <= beep_duration:
            play_sound(beep_audio_file, duration=beep_duration)
            beep_played = True

        # Jika waktu total telah habis, keluar loop
        if elapsed >= total_wait:
            break

        # Logging setiap detik
        if now - last_log >= 1:
            remaining -= 1
            logger.info(f"[Crossing Not Clear] Lampu pejalan kaki akan merah dalam waktu {remaining:.0f} detik")
            last_log = now

        sleep(0.1)


def handle_pedestrian_crossing(crossing_flag, delay_before_crossing: int, jumlah_orang: int, zebra_cross_flag, client_socket):
    # 1. Play "wait audio" (sekali)
    play_sound(wait_audio_file)

    # 2. Hitung durasi hijau pejalan kaki berdasarkan jumlah orang
    if jumlah_orang <= 3:
        lampu_hijau_duration = 10
    elif jumlah_orang <= 6:
        lampu_hijau_duration = 15
    else:
        lampu_hijau_duration = 20

    # 3. Countdown sebelum lampu hijau (delay_before_crossing)
    print_status_with_countdown("Lampu pejalan kaki akan hijau", delay_before_crossing)

    # 4. Transisi: Mobil hijau → kuning → merah
    car_green_to_red()

    # 5. Transisi: Pejalan kaki merah → kuning → hijau
    cross_red_to_green()

    # 6. Play "go audio" (sekali)
    play_sound(go_audio_file)

    # 7. Countdown hijau pejalan kaki minimum
    print_status_with_countdown("Lampu pejalan kaki akan merah", lampu_hijau_duration)

    # Setelah countdown hijau selesai, beri tahu klien bahwa minimum time terpenuhi
    client_socket.sendall("Minimum Time is Reached".encode('utf-8'))
    # Clear flag, agar wait_crossing_clear bisa memantau ulang
    zebra_cross_flag.clear()

    # 8. Tunggu zebra_cross_flag atau timeout, plus putar beep 2 detik sebelum ubah lampu
    max_wait_time = config.getint('Pedestrian', 'max_wait_time', fallback=30)
    wait_crossing_clear(max_wait_time, lampu_hijau_duration, zebra_cross_flag)

    # 9. Transisi: Pejalan kaki hijau → kuning → merah
    cross_green_to_red()

    # 10. Transisi: Mobil merah → kuning → hijau
    car_red_to_green()

    # 11. Selesai: clear crossing_flag
    crossing_flag.clear()
