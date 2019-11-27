import board
import busio
from digitalio import DigitalInOut
import adafruit_esp32spi.adafruit_esp32spi_socket as socket
from adafruit_esp32spi import adafruit_esp32spi
import adafruit_requests as requests
from adafruit_pybadger import PyBadger 
import neopixel
import json
from secrets import secrets
import time


OFF = (0,0,0)
BLUE = (32,32,255)
pybadger = PyBadger()
pixels = pybadger.pixels
pixels.brightness = 0.005
pixels.fill(OFF)
pixels.show()

# Setup WiFi
esp32_cs = DigitalInOut(board.D13)
esp32_ready = DigitalInOut(board.D11)
esp32_reset = DigitalInOut(board.D12)

spi = busio.SPI(board.SCK, board.MOSI, board.MISO)
esp = adafruit_esp32spi.ESP_SPIcontrol(spi, esp32_cs, esp32_ready, esp32_reset)

requests.set_socket(socket, esp)

if esp.status == adafruit_esp32spi.WL_IDLE_STATUS:
    print("ESP32 found and in idle mode")
print("Firmware vers.", esp.firmware_version)
print("MAC addr:", [hex(i) for i in esp.MAC_address])

wifi_not_connected = True

while wifi_not_connected:
    try:
        esp.connect_AP(secrets['wifi_user'], secrets['wifi_pass'])
        wifi_not_connected = False
    except Exception as e:
        print(e)
        pass

print("Connected to", str(esp.ssid, 'utf-8'), "\tRSSI:", esp.rssi)
print("My IP address is", esp.pretty_ip(esp.ip_address))

time.sleep(2)


def show_badge():
    pybadger.show_badge(name_string="Mark", hello_scale=1, my_name_is_scale=1, name_scale=1)


def show_wildcat():
    pybadger.show_business_card(image_name="wildcat.bmp",email_string_two="fischerm@email.arizona.edu")


def aws_announcements():
    pybadger.aws_announcements(name_string="...:::...", 
                                hello_scale=1, 
                                my_name_is_scale=1, 
                                name_scale=1
                                )
    stats_resp = requests.get('https://f3m81lupa9.execute-api.us-west-2.amazonaws.com/dev/stats')
    stats = stats_resp.json()
    pybadger.aws_announcements(name_string=stats['count'], 
                                hello_scale=1, 
                                my_name_is_scale=1, 
                                name_scale=1
                                )


aws_announcements()

while True:
    pybadger.auto_dim_display(delay=50) # Remove or comment out this line if you have the PyBadge LC
    if pybadger.button.a:
        board.DISPLAY.brightness = 1
        show_wildcat()
    elif pybadger.button.b:
        board.DISPLAY.brightness = 1
        pybadger.show_qr_code(data="https://www.arizona.edu")
    elif pybadger.button.start:
        board.DISPLAY.brightness = 1
        show_badge()
    elif pybadger.button.up:
        board.DISPLAY.brightness = 1
        aws_announcements()
