"""File containing communication functions.
"""

from util import *
import busio
import board
from digitalio import DigitalInOut
import adafruit_rfm9x

rfm9x = None
FREQ = 915.0
CS = DigitalInOut(board.CE1)
RESET = DigitalInOut(board.D25)
spi = busio.SPI(board.SCK, MOSI=board.MOSI, MISO=board.MISO)

def lora_init():
    # Configure LoRa Radio
    rfm9x = adafruit_rfm9x.RFM9x(spi, CS, RESET, FREQ)
    rfm9x.tx_power = 23


def lora_transmit(msg:str):
    data: bytes = bytes(f'{msg}', encoding='utf8')
    rfm9x.send(data)

def lora_hearbeat():
    data: bytes = bytes(f'RPi Transmission on {FREQ} at {get_timestamp}', encoding='utf8')
    rfm9x.send(data)