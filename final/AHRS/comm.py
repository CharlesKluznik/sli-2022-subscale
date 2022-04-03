"""File containing communication functions.
"""

from util import *
import traceback
import busio
import board
from digitalio import DigitalInOut
import adafruit_rfm9x

rfm9x = None
spi = None
CS = None
RESET = None
FREQ = None

sleep(2)
try:
    FREQ = 915.0
    CS = DigitalInOut(board.CE1)
    RESET = DigitalInOut(board.D25)
    spi = busio.SPI(board.SCK, MOSI=board.MOSI, MISO=board.MISO)
    rfm9x = adafruit_rfm9x.RFM9x(spi, CS, RESET, FREQ)
    rfm9x.tx_power = 23
except Exception as ex:
        print(f'lora setup exception: {ex}')
        pass


def lora_init():
    try:
        FREQ = 915.0
        CS = DigitalInOut(board.CE1)
        RESET = DigitalInOut(board.D25)
        spi = busio.SPI(board.SCK, MOSI=board.MOSI, MISO=board.MISO)
        rfm9x = adafruit_rfm9x.RFM9x(spi, CS, RESET, FREQ)
        rfm9x.tx_power = 23
    except Exception as ex:
        print(f'lora_init exception: {ex}')
        pass


def lora_transmit(msg:str):
    try:
        FREQ = 915.0
        CS = DigitalInOut(board.CE1)
        RESET = DigitalInOut(board.D25)
        spi = busio.SPI(board.SCK, MOSI=board.MOSI, MISO=board.MISO)
        rfm9x = adafruit_rfm9x.RFM9x(spi, CS, RESET, FREQ)
        rfm9x.tx_power = 23
        data: bytes = bytes(f'{msg}', encoding='utf8')
        rfm9x.send(data)
    except Exception as ex:
        print(f'lora_transmit exception: {ex}')
        pass

def lora_hearbeat():
    try:
        FREQ = 915.0
        CS = DigitalInOut(board.CE1)
        RESET = DigitalInOut(board.D25)
        spi = busio.SPI(board.SCK, MOSI=board.MOSI, MISO=board.MISO)
        rfm9x = adafruit_rfm9x.RFM9x(spi, CS, RESET, FREQ)
        rfm9x.tx_power = 23
        data: bytes = bytes(f'RPi Transmission on {FREQ} at {get_timestamp()}', encoding='utf8')
        rfm9x.send(data)
    except Exception as ex:
        print(f'lora_heartbeat exception: {ex}')
        pass
