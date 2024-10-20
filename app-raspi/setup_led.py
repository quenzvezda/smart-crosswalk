import sys
import configparser

if 'win' in sys.platform:
    from mock_gpio import LED
else:
    from gpiozero import LED

# Initialize ConfigParser
config = configparser.ConfigParser()
config.read('config.ini')

def initialize_leds(pins):
    return {color: LED(pin) for color, pin in pins.items()}

# Read GPIO pins from config
pin_pejalan_kaki_kiri = {
    'merah': config.getint('GPIO', 'pedestrian_left_red'),
    'kuning': config.getint('GPIO', 'pedestrian_left_yellow'),
    'hijau': config.getint('GPIO', 'pedestrian_left_green')
}

pin_pejalan_kaki_kanan = {
    'merah': config.getint('GPIO', 'pedestrian_right_red'),
    'kuning': config.getint('GPIO', 'pedestrian_right_yellow'),
    'hijau': config.getint('GPIO', 'pedestrian_right_green')
}

pin_mobil = {
    'merah': config.getint('GPIO', 'vehicle_red'),
    'kuning': config.getint('GPIO', 'vehicle_yellow'),
    'hijau': config.getint('GPIO', 'vehicle_green')
}

# Initialize traffic lights
pejalan_kaki_kiri = initialize_leds(pin_pejalan_kaki_kiri)
pejalan_kaki_kanan = initialize_leds(pin_pejalan_kaki_kanan)
mobil = initialize_leds(pin_mobil)
