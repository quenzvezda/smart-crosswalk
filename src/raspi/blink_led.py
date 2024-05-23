from gpiozero import LED
from time import sleep

# Fungsi untuk inisialisasi LED berdasarkan pin yang diberikan
def initialize_leds(pin_numbers):
    leds = [LED(pin) for pin in pin_numbers]
    return leds

# Fungsi untuk menyalakan dan mematikan LED
def control_leds(leds, on_time, off_time):
    try:
        while True:
            for led in leds:
                led.on()
            print("menyala")
            sleep(on_time)

            for led in leds:
                led.off()
            print("mati")
            sleep(off_time)
    except KeyboardInterrupt:
        for led in leds:
            led.close()
        print("Program dihentikan, pin GPIO dibersihkan.")

# Pin GPIO yang akan digunakan
pin_numbers = [23, 24, 25]

# Inisialisasi LED
leds = initialize_leds(pin_numbers)

# Kontrol LED dengan waktu nyala 5 detik dan mati 1 detik
control_leds(leds, 5, 1)
