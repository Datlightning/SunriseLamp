# SPDX-FileCopyrightText: 2019 ladyada for Adafruit Industries
# SPDX-License-Identifier: MIT

from os import getenv

import adafruit_connection_manager
import adafruit_requests
import board
import busio
import neopixel
from digitalio import DigitalInOut
import time

from adafruit_esp32spi import adafruit_esp32spi

# Get wifi details and more from a settings.toml file
# tokens used by this Demo: CIRCUITPY_WIFI_SSID, CIRCUITPY_WIFI_PASSWORD
ssid = getenv("CIRCUITPY_WIFI_SSID")
password = getenv("CIRCUITPY_WIFI_PASSWORD")

NUM_PIXELS = 80
PIN = board.D6
pixels = neopixel.NeoPixel(PIN, NUM_PIXELS, brightness=0.7, auto_write=False)


print("ESP32 SPI webclient test")
 
JSON_URL = "http://192.168.68.133:5000/processed-image"
 
 
# If you are using a board with pre-defined ESP32 Pins:
# esp32_cs = DigitalInOut(board.ESP_CS) 
# esp32_ready = DigitalInOut(board.ESP_BUSY)
# esp32_reset = DigitalInOut(board.ESP_RESET)

# If you have an AirLift Shield: 
# esp32_cs = DigitalInOut(board.D10)
# esp32_ready = DigitalInOut(board.D7)
# esp32_reset = DigitalInOut(board.D5)

# If you have an AirLift Featherwing or ItsyBitsy Airlift:
esp32_cs = DigitalInOut(board.D13)
esp32_ready = DigitalInOut(board.D11)
esp32_reset = DigitalInOut(board.D12)

# If you have an externally connected ES P32:
# NOTE: You may need to change the pins to reflect your wiring
# esp32_cs = DigitalInOut(board.D9)
# esp32_ready = DigitalInOut(board.D10) 
# esp32_reset = DigitalInOut(board.D5)

# Secondary (SCK1) SPI used to connect to WiFi board on Arduino Nano Connect RP2040
if "SCK1" in dir(board):
    spi = busio.SPI(board.SCK1, board.MOSI1, board.MISO1)
else:
    spi = busio.SPI(board.SCK, board.MOSI, board.MISO)
esp = adafruit_esp32spi.ESP_SPIcontrol(spi, esp32_cs, esp32_ready, esp32_reset)

pool = adafruit_connection_manager.get_radio_socketpool(esp)
ssl_context = adafruit_connection_manager.get_radio_ssl_context(esp)
requests = adafruit_requests.Session(pool, ssl_context)

if esp.status == adafruit_esp32spi.WL_IDLE_STATUS:
    print("ESP32 found and in idle mode")
# print("Firmware vers.", esp.firmware_version)
# print("MAC addr:", ":".join("%02X" % byte for byte in esp.MAC_address))

# for ap in esp.scan_networks():
    # print("\t%-23s RSSI: %d" % (ap.ssid, ap.rssi))
    
# print("Connecting to AP...")
while not esp.is_connected:
    try:
        esp.connect_AP(ssid, password)
    except OSError as e:
        print("could not connect to AP, retrying: ", e)
        continue
# print("Connected to", esp.ap_info.ssid, "\tRSSI:", esp.ap_info.rssi)
# print("My IP address is", esp.ipv4_address)
# print("IP lookup adafruit.com: %s" % esp.pretty_ip(esp.get_host_by_name("adafruit.com")))
# print("Ping google.com: %d ms" % esp.ping("google.com"))
def wheel(pos):
    """Generate rainbow colors across 0–255 positions."""
    if pos < 0 or pos > 255:
        return (0, 0, 0)
    if pos < 85:
        return (255 - pos * 3, pos * 3, 0)
    elif pos < 170:
        pos -= 85
        return (0, 255 - pos * 3, pos * 3)
    else:
        pos -= 170
        return (pos * 3, 0, 255 - pos * 3)
def rainbow_chase(wait):
    for j in range(255):
        for i in range(NUM_PIXELS):
            # Group pixels in chunks of 8
            group_index = i % 8
            pixel_index = (group_index * 256 // 8 + j) & 255
            color = wheel(pixel_index)
            pixels[i] = color
        pixels.show()
        time.sleep(wait)
# esp._debug = True
while True:
    try:
        r = requests.get(JSON_URL)
        colors = r.json()['colors']
    except:
        colors = [] 
    if colors:
        for arc in range(8):
            for height in range(10):
                color = colors[arc][height]
                pixels[arc * 10 + height] = (color["r"], color["g"], color["b"])
        pixels.show()
        print(pixels) 
        time.sleep(5) 
    else:
        rainbow_chase(0)
     
