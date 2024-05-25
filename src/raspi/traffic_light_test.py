from gpiozero import LED
from time import sleep

# Mobil Hijau 10 Detik - Orang Merah 10 Detik
# Waktu Pergantian Dari Merah ke Hijau Total Selama 3 Detik (2 Detik Kuning + 1 Detik Merah (Semuanya Merah))
# Mobil Merah 5 Detik - Orang Hijau 5 Detik

# Inisialisasi LED berdasarkan pin yang diberikan
def initialize_leds(pins):
    return {color: LED(pin) for color, pin in pins.items()}


# Fungsi untuk mengatur lampu lalu lintas
def traffic_light_cycle():
    try:
        while True:
            # Lampu mobil hijau selama 10 detik
            mobil['hijau'].on()
            pejalan_kaki_kiri['merah'].on()
            pejalan_kaki_kanan['merah'].on()
            print("Lampu Mobil Hijau, Pejalan Kaki Merah")
            sleep(10)

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

            # Lampu pejalan kaki hijau selama 5 detik
            pejalan_kaki_kiri['kuning'].off()
            pejalan_kaki_kanan['kuning'].off()
            pejalan_kaki_kiri['hijau'].on()
            pejalan_kaki_kanan['hijau'].on()
            print("Lampu Mobil Merah, Pejalan Kaki Hijau")
            sleep(5)

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

    except KeyboardInterrupt:
        for led in mobil.values():
            led.close()
        for led in pejalan_kaki_kiri.values():
            led.close()
        for led in pejalan_kaki_kanan.values():
            led.close()
        print("Program dihentikan, pin GPIO dibersihkan.")


# Pin GPIO untuk lampu pejalan kaki kiri
pin_pejalan_kaki_kiri = {
    'merah': 5,
    'kuning': 6,
    'hijau': 26
}

# Pin GPIO untuk lampu pejalan kaki kanan
pin_pejalan_kaki_kanan = {
    'merah': 17,
    'kuning': 27,
    'hijau': 22
}

# Pin GPIO untuk lampu mobil
pin_mobil = {
    'merah': 23,
    'kuning': 24,
    'hijau': 25
}

# Inisialisasi lampu lalu lintas
pejalan_kaki_kiri = initialize_leds(pin_pejalan_kaki_kiri)
pejalan_kaki_kanan = initialize_leds(pin_pejalan_kaki_kanan)
mobil = initialize_leds(pin_mobil)

# Jalankan siklus lampu lalu lintas
traffic_light_cycle()
