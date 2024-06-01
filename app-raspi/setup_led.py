from gpiozero import LED


def initialize_leds(pins):
    return {color: LED(pin) for color, pin in pins.items()}


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
